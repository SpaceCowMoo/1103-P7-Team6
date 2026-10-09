import csv
import json
import os
from dotenv import load_dotenv
from google import genai
import data_manager

EXPECTED_AI_OUTPUT = {
    "job_id": None,
    "SkillsMatch": None,
    "RoleMatch": None,
    "IndustryInterestMatch": None,
    "ExperienceMatch": None,
    "SalaryMatch": None,
    "WorkArrangementMatch": None,
    "LocationMatch": None,
    "CompanyPreferenceMatch": None
}

def configure_gemini():
    load_dotenv()

    api_key = os.getenv("GEMINI_API_KEY")

    if not api_key:
        raise ValueError("GEMINI_API_KEY is missing from .env")

    client = genai.Client(api_key=api_key)

    return client

def get_latest_profile(filename):
    latest_profile = None

    with open(filename, "r", newline="", encoding="utf-8") as file:
        reader = csv.DictReader(file)

        for row in reader:
            latest_profile = row

    return latest_profile

# Convert CSV values into Python data types
def convert_value(value):
    if value is None or value.strip() == "":
        return None

    try:
        return json.loads(value)
    except (json.JSONDecodeError, TypeError):
        return value

def get_ai_input(profile):
    ai_input = {
        "course_of_study": profile["Course_of_Study"],
        "year_of_study": profile["Year_of_Study"],
        "internship_duration": profile["Internship_Duration"],
        "preferred_month": profile["Prefer_month"],
        "skills": convert_value(profile["Skills"]),
        "preferred_roles": convert_value(profile["Prefer_Role"]),
        "minimum_monthly_salary": convert_value(
            profile["Minimum_monthly_salary"]
        ),
        "preferred_location": convert_value(profile["Preferred_location"]),
        "industry_interests": convert_value(profile["Industry_interests"]),
        "company_preference": convert_value(profile["Company_preference"]),
        "past_experience": convert_value(profile["Past_experience"])
    }

    return ai_input

def get_test_internship(conn, job_id):
    return data_manager.get_internship(conn, job_id)

def build_prompt(student_profile, internship):

    prompt = f"""
You are an AI internship matching assistant for InternLink.

Analyse how well the student matches the internship listing.

STUDENT PROFILE:
{json.dumps(student_profile, indent=2)}

INTERNSHIP LISTING:
{json.dumps(internship, indent=2)}

MATCHING CRITERIA:

1. SkillsMatch:
Evaluate how well the student's skills match the
internship's required skills.

2. RoleMatch:
Evaluate whether the internship role aligns with
the student's preferred roles.

3. IndustryInterestMatch:
Evaluate whether the internship industry aligns
with the student's industry interests.

4. ExperienceMatch:
Evaluate whether the student's past experience is
relevant to the internship responsibilities.

5. SalaryMatch:
Evaluate the internship allowance against the
student's minimum expected monthly salary.

6. WorkArrangementMatch:
Evaluate whether the internship's work arrangement
matches the student's preference, if provided.

7. LocationMatch:
Evaluate whether the internship location aligns
with the student's preferred location.

8. CompanyPreferenceMatch:
Evaluate whether the company aligns with the
student's preferred company type.

SCORING RULES:

- Assess each criterion independently.
- Give each criterion a score from 0 to 100.
- 0 means no alignment.
- 100 means excellent alignment.
- Use only the provided student and internship information.
- If an optional preference is missing, do not invent it.
- Do not calculate an overall match score.
- Do not rank internships.
- Do not apply business rules or flags.
- Do not provide individual internship explanations.

JSON RESPONSE INSTRUCTIONS:

Return ONLY a valid JSON object.

- Do not include Markdown code fences.
- Do not include text outside the JSON object.
- Use exactly the field names shown below.
- All match scores must be integers from 0 to 100.
- Return null when an optional criterion cannot be assessed.
- Do not invent missing preferences.
- Return the original job_id unchanged.
- Do not include overall scores, rankings or explanations.

EXPECTED JSON STRUCTURE:

{json.dumps(EXPECTED_AI_OUTPUT, indent=2)}

Replace the null placeholders with actual scores where
sufficient information is available.
Keep null for criteria that cannot be assessed.
"""

    return prompt

if __name__ == "__main__":
    client = configure_gemini()
    print("Gemini client configured successfully!")

    profile = get_latest_profile("data/student_profiles.csv")

    if profile is None:
        raise ValueError("No student profiles found.")

    ai_input = get_ai_input(profile)

    db_path = os.getenv("INTERNSHIP_DB", "data/internships.db")
    csv_path = os.getenv("INTERNSHIP_DATA", "data/internships.csv")

    # Connect to database
    conn = data_manager.get_conn(db_path)

    try:
        # Create internship table if it doesn't exist
        data_manager.init_db(conn)

        # Load internship CSV if database is empty
        if data_manager.is_empty(conn, "internships"):
            data_manager.load_internships_csv(conn, csv_path)

        # Retrieve internship with job_id = 1
        internship = get_test_internship(conn, 1)

    finally:
        conn.close()

    prompt = build_prompt(ai_input, internship)

    print(prompt)