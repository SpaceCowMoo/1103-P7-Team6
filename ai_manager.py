import csv
import json

import data_manager

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
        "company_preference": convert_value(profile["Company preference"]),
        "past_experience": convert_value(profile["Past experience"])
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
"""

    return prompt

if __name__ == "__main__":
    import os
    from dotenv import load_dotenv

    load_dotenv()

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
        if data_manager.is_empty(conn):
            data_manager.load_csv(conn, csv_path)

        # Retrieve internship with job_id = 1
        internship = get_test_internship(conn, 1)

    finally:
        conn.close()

    prompt = build_prompt(ai_input, internship)

    print(prompt)