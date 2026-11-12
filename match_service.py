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
        pass