# MatchService class that retrieves intership data and AI results
# Also handles the scoring of each individual internship and applies flags
# Finally it ranks and saves the results to the database

class MatchService:
    def __init__(self, conn):
        self.conn = conn
        self.ai_manager = AIManager()
        self.data_manager = DataManager(conn)

        self.scorer = MatchScorer()
        self.flag_evaluator = FlagEvaluator(conn)

    def find_matches(self, student_profile):
        internships = self.data_manager.list_internships(limit = -1)
        ai_input = self.ai_manager.get_ai_input(student_profile["student_profile"])
        client = self.ai_manager.configure_gemini()
        ai_result = self.ai_manager.run_ai_pipeline(client, ai_input, internships)

        # Continue with scoring, flags and saving
        return self.save_results(student_profile, ai_result)

    def save_results(self, student_profile, ai_result):
        results = []
        internships = ai_result["selected_internships"]["internships"]
        for internship in internships:
            #calculate individual match score
            current_score = self.scorer.calculate_score(internship)
            #raise flags and apply deductions
            flags, deduction = self.flag_evaluator.evaluate_flags(student_profile, internship)
            final_score = current_score - deduction    #final score calculated after applying flag penalty points
    
            results.append({"job_id": internship["job_id"], 
                            "score": final_score, 
                            "flags": flags})
        
            # sort score in descending order
            results.sort(key=lambda result: result["score"], reverse=True)
            # keep only top 5 results
            results = results[:5]
        
            job_ids = [result["job_id"] for result in results]
            scores = [result["score"] for result in results]
            flags = [result["flags"] for result in results]
            # DB NOTE:  save_match(conn, profile, job_ids, scores, flags, overall_feedback)
            #   job_ids  [12, 4, 30, 7, 2]                    5 ints, best first
            #   scores   [82.3, 70.0, 51.2, 35.0, 20.0]       5 numbers, same order
            #   flags    [["Salary below ..."], [], ...]      5 lists of text, same order
            #   overall_feedback is saved exactly as the AI gave it ({"points": [...]})
            # Read it back with data_manager.get_match(conn, match_id)
            return self.data_manager.save_match(conn, student_profile, job_ids, scores, flags, ai_result["overall_feedback"])