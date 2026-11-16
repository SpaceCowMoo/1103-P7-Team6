# AI Manager - InternLink
# Handles Gemini API communication, prompt construction,
# response parsing, JSON validation and AI-generated feedback.
from ai.gemini_client import GeminiClient
from ai.response_validator import AIResponseValidator
from ai.prompt_builder import AIPromptBuilder
from ai.ai_client import AIClient

class AIManager:

    def __init__(self, client=None):
        if client is None:
            client = GeminiClient()

        if not isinstance(client, AIClient):
            raise TypeError("client must implement AIClient")

        self._client = client
        self._validator = AIResponseValidator()
        self._prompt_builder = AIPromptBuilder()

    def connect(self):
        self._client.connect()

    def generate_response(self, prompt):
        return self._client.generate(prompt)

    def parse_response(self, response_text):
        return self._validator.parse_gemini_response(response_text)

    def validate_response(self, result, job_id):
        return self._validator.validate_gemini_response(
            result, job_id
        )

    def validate_shortlist(self, result, internships):
        return self._validator.validate_shortlist_response(
            result, internships
        )

    def build_shortlist_prompt(self, student_profile, internships):
        return self._prompt_builder.build_shortlist_prompt(
            student_profile, internships
        )

    def build_skill_gap_prompt(self, student_profile, shortlisted_internships):
        return self._prompt_builder.build_skill_gap_prompt(
            student_profile, shortlisted_internships
        )

    def select_shortlisted_internships(self, student_profile, internships):
        if len(internships) < 5:
            raise ValueError(
                "At least five eligible internships are required"
            )

        prompt = self.build_shortlist_prompt(
            student_profile, internships
        )

        max_attempts = 3

        for attempt in range(1, max_attempts + 1):
            try:
                response = self.generate_response(prompt)
                parsed = self.parse_response(response)

                return self.validate_shortlist(parsed, internships)

            except ValueError as e:
                if attempt == max_attempts:
                    raise RuntimeError(
                        "Gemini failed to return a valid internship shortlist"
                    ) from e

        raise RuntimeError("Internship shortlisting failed")

    def generate_skill_gap_feedback(
        self, student_profile, shortlisted_internships
    ):
        prompt = self.build_skill_gap_prompt(
            student_profile, shortlisted_internships
        )

        max_attempts = 3

        for attempt in range(1, max_attempts + 1):
            try:
                response = self.generate_response(prompt)
                result = self.parse_response(response)

                return self._validator.validate_feedback_response(result)

            except ValueError as error:
                if attempt == max_attempts:
                    raise RuntimeError(
                        "Gemini failed to return valid skill-gap feedback"
                    ) from error

        raise RuntimeError("Skill-gap feedback generation failed")

    def run_ai_pipeline(self, student_profile, internships):
        # Step 1: Filter internships by duration
        eligible_internships = self.filter_by_duration(
            student_profile,
            internships
        )

        # Step 2: Let AI shortlist internships and generate match scores
        selected_scores = self.select_shortlisted_internships(
            student_profile,
            eligible_internships
        )

        # Step 3: Match selected job IDs to full internship records
        internship_lookup = {
            internship["job_id"]: internship
            for internship in eligible_internships
        }

        shortlisted_internships = []

        for scores in selected_scores:
            job_id = scores["job_id"]

            internship = internship_lookup[job_id].copy()

            # Combine internship details with AI scores
            internship.update(scores)

            shortlisted_internships.append(internship)

        # Step 4: Generate skill-gap feedback
        feedback = self.generate_skill_gap_feedback(
            student_profile,
            shortlisted_internships
        )

        # Step 5: Return only job IDs and AI match scores
        return {
            "selected_internships": {
                "internships": selected_scores
            },
            "overall_feedback": feedback
        }

    def filter_by_duration(self, student_profile, internships):
        available_months = student_profile.get("internship_duration")

        if available_months is None:
            raise ValueError("Student internship duration is required")

        try:
            available_months = int(available_months)
        except (TypeError, ValueError):
            raise ValueError(
                "Student internship duration must be a number of months"
            )

        if available_months <= 0:
            raise ValueError(
                "Student internship duration must be greater than zero"
            )

        eligible = []

        for internship in internships:
            duration = internship.get("duration_months")

            if duration is None:
                continue

            try:
                duration = int(duration)
            except (TypeError, ValueError):
                continue

            if 0 < duration <= available_months:
                eligible.append(internship)

        return eligible

    def get_ai_input(self, profile):
        return {
            "course_of_study": profile.get("course_of_study"),
            "year_of_study": profile.get("year_of_study"),
            "internship_duration": profile.get("duration"),
            "available_internship_dates": profile.get("available_internship_dates"),
            "skills": profile.get("skills"),
            "preferred_roles": profile.get("preferred_roles"),
            "minimum_monthly_salary": profile.get("minimum_monthly_salary"),
            "preferred_work_arrangement": profile.get("preferred_work_arrangement"),
            "preferred_location": profile.get("preferred_location"),
            "industry_interests": profile.get("industry_interest"),
            "company_preference": profile.get("company_preference"),
            "past_experience": profile.get("past_experience", {})
        }


