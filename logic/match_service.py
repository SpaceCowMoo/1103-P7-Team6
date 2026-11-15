# MatchService class that retrieves intership data and AI results
# Also handles the scoring of each individual internship and applies flags
# Finally it ranks and saves the results to the database
import ai_manager
from data_manager import DataManager
from logic.match_scorer import MatchScorer
from logic.flag_evaluator import FlagEvaluator
from models.flags import Flags
from models.listing import Listing
from models.run_result import RunResult
from models.run_snapshot import RESULTS_PER_RUN

class MatchService:
    def __init__(self, data):
        # data = the DataManager from AppContext                      
        self.data = data
        self.scorer = MatchScorer()
        self.flag_evaluator = FlagEvaluator(data)

    def find_matches(self, user_id, resume):
        """Ask the AI, score + flag + rank, save. Returns the saved RunSnapshot."""
        profile = self.__to_ai_profile(resume)
        internships = [i.fetch_internship_details() for i in self.data.list_internships(limit=-1)]
        client = ai_manager.configure_gemini()
        ai_result = ai_manager.run_ai_pipeline(client, profile, internships)

        # Continue with scoring, flags and saving
        results = self.__rank(resume, ai_result["selected_internships"]["internships"])
        return self.data.save_run(user_id, resume, results, ai_result["overall_feedback"]["points"])

    def __rank(self, resume, ai_scores_list):
        scored = []
        for ai_scores in ai_scores_list:
            internship = self.data.get_internship(ai_scores["job_id"])
            flag_names, deduction = self.flag_evaluator.evaluate_flags(resume, internship)
            score = self.scorer.calculate_score(ai_scores) - deduction
            scored.append((score, Listing(internship, [Flags(name, True) for name in flag_names])))

        scored.sort(key=lambda pair: pair[0], reverse=True)      # OUTSIDE the loop
        return [RunResult(rank, score, listing)
                for rank, (score, listing) in enumerate(scored[:RESULTS_PER_RUN], start=1)]

    @staticmethod
    def __to_ai_profile(resume):
        """The AI was written for the old dict keys, so translate once, here."""
        d = resume.fetch_Student_Resume_details()
        return {
            "course_of_study": d["Courses"], "year_of_study": d["Year_of_Study"],
            "internship_duration": d["Duration_of_internship"],
            "available_internship_dates": d["available_internship_date"],
            "skills": d["Skills"], "preferred_roles": d["Preferred_role"],
            "minimum_monthly_salary": d["Minimum_monthly_salary"],
            "preferred_work_arrangement": d["preferred_work_arrangement"],
            "preferred_location": d["Preferred_location"],
            "industry_interests": d["industry_interest"],
            "company_preference": d["company_preference"],
            "past_experience": d["Past_internships"],
        }