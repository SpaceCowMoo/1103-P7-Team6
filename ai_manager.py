# AI Manager - InternLink
# Handles Gemini API communication, prompt construction,
# response parsing, JSON validation and AI-generated feedback.
import json
import data_manager
from ai.gemini_client import GeminiClient
from ai.response_validator import AIResponseValidator
from ai.prompt_builder import AIPromptBuilder

validator = AIResponseValidator()
prompt_builder = AIPromptBuilder()

# Expected fields and structure for each AI-assessed internship
# Scores range from 0-100, or None if a criterion cannot be assessed
EXPECTED_AI_OUTPUT = {
    "job_id": None,
    "SkillsMatch": None,
    "RoleMatch": None,
    "IndustryInterestMatch": None,
    "ExperienceMatch": None,
    "CompanyPreferenceMatch": None
}

# JSON template used to instruct Gemini on the required shortlist format
EXPECTED_SHORTLIST_OUTPUT = {
    "selected_internships": [
        EXPECTED_AI_OUTPUT
    ]
}


class AIManager:

    def __init__(self, client=None):
        self._client = client if client is not None else GeminiClient()
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


# Load the API key from .env and initialise the Gemini client
def configure_gemini():
    client = GeminiClient()
    client.connect()
    return client

# Send a prompt to Gemini and request a JSON response
# Raise an error if the API fails or returns an empty response
def call_gemini(client, prompt):
    return client.generate(prompt)

# Convert Gemini's text response into a Python dictionary
# Remove Markdown formatting if present and reject invalid JSON
def parse_gemini_response(response_text):
    return validator.parse_gemini_response(response_text)

# Validate the fields, job ID and score ranges of an AI-assessed internship
# Reject unexpected fields, incorrect IDs and invalid score values
def validate_gemini_response(result, job_id):
    return validator.validate_gemini_response(result, job_id)

# Convert the student profile into the field names expected by the AI prompts
def get_ai_input(profile):
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

# Filter out internships that exceed the student's available duration
# Skip listings with missing or invalid duration values
def filter_by_duration(student_profile, internships):
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

# Build the AI prompt using the student profile and eligible internships
# Instruct Gemini to shortlist 5-10 internships and score five matching criteria
# Final ranking, weighted scores and preference flags are handled by Logic Manager
def build_shortlist_prompt(student_profile, internships):
    return prompt_builder.build_shortlist_prompt(
        student_profile,
        internships
    )

# Validate the shortlist returned by Gemini
# Ensure there are 5-10 unique internships with valid IDs and scores
def validate_shortlist_response(result, internships):
    return validator.validate_shortlist_response(result, internships)

# Request and validate an AI-generated internship shortlist
# Retry up to three times if Gemini returns an invalid response
def select_shortlisted_internships(client, student_profile, internships):
    if len(internships) < 5:
        raise ValueError(
            "At least five eligible internships are required"
        )

    prompt = build_shortlist_prompt(student_profile, internships)

    max_attempts = 3

    for attempt in range(1, max_attempts + 1):
        try:
            response = call_gemini(client, prompt)
            parsed = parse_gemini_response(response)

            return validate_shortlist_response(parsed, internships)

        except ValueError as e:
            if attempt == max_attempts:
                raise RuntimeError(
                    "Gemini failed to return a valid internship shortlist"
                ) from e

    raise RuntimeError("Internship shortlisting failed")

# Build a prompt to identify skill gaps across the shortlisted internships
# Request personalised, actionable recommendations based on the student's profile
def build_skill_gap_prompt(student_profile, shortlisted_internships):
    return prompt_builder.build_skill_gap_prompt(
        student_profile,
        shortlisted_internships
    )

# Generate and validate personalised skill-gap feedback using Gemini
# Ensure the response contains 3-5 non-empty feedback points
# Retry up to three times if the response format is invalid
def generate_skill_gap_feedback(client, student_profile, shortlisted_internships):
    prompt = build_skill_gap_prompt(
        student_profile,
        shortlisted_internships
    )

    max_attempts = 3

    for attempt in range(1, max_attempts + 1):
        try:
            response = call_gemini(client, prompt)
            result = parse_gemini_response(response)

            if not isinstance(result, dict):
                raise ValueError("Feedback response must be a dictionary")

            if set(result.keys()) != {"overall_feedback"}:
                raise ValueError("Unexpected feedback response fields")

            feedback = result["overall_feedback"]

            if not isinstance(feedback, dict):
                raise ValueError("overall_feedback must be a dictionary")

            if set(feedback.keys()) != {"points"}:
                raise ValueError("Feedback must contain only 'points'")

            points = feedback["points"]

            if not isinstance(points, list) or not 3 <= len(points) <= 5:
                raise ValueError("Feedback must contain 3 to 5 points")

            if not all(
                isinstance(point, str) and point.strip()
                for point in points
            ):
                raise ValueError("Every feedback point must be non-empty text")

            return feedback

        except ValueError as error:
            if attempt == max_attempts:
                raise RuntimeError(
                    "Gemini failed to return valid skill-gap feedback"
                ) from error

    raise RuntimeError("Skill-gap feedback generation failed")

# Main AI Manager pipeline:
def run_ai_pipeline(client, student_profile, internships):
    # Step 1: Filter internships by duration
    eligible_internships = filter_by_duration(
        student_profile,
        internships
    )

    # Step 2: Let AI shortlist internships and generate match scores
    selected_scores = select_shortlisted_internships(
        client,
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

        # Combine internship details with AI scores for feedback generation
        internship.update(scores)

        shortlisted_internships.append(internship)

    # Step 4: Generate skill-gap feedback using full internship details
    feedback = generate_skill_gap_feedback(
        client,
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