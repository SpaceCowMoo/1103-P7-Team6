import csv
import json
import os
from dotenv import load_dotenv
from google import genai
from google.genai import errors
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

def call_gemini(client, prompt):
    try:
        response = client.models.generate_content(
            model="gemini-2.5-flash",
            contents=prompt,
            config={
                "response_mime_type": "application/json"
            }
        )

    except errors.APIError as e:
        raise RuntimeError(
            f"Gemini API request failed: {e}"
        ) from e

    except (ConnectionError, TimeoutError) as e:
        raise RuntimeError(
            f"Unable to connect to Gemini: {e}"
        ) from e

    if not response.text or not response.text.strip():
        raise RuntimeError(
            "Gemini returned an empty response"
        )

    return response.text

def parse_gemini_response(response_text):
    if not isinstance(response_text, str) or not response_text.strip():
        raise ValueError("Gemini returned an empty response")

    response_text = response_text.strip()

    # Remove Markdown code fences if present
    if response_text.startswith("```json"):
        response_text = response_text[7:]
    elif response_text.startswith("```"):
        response_text = response_text[3:]

    if response_text.endswith("```"):
        response_text = response_text[:-3]

    try:
        result = json.loads(response_text.strip())
    except json.JSONDecodeError:
        raise ValueError("Gemini returned invalid JSON")

    return result

def validate_gemini_response(result, job_id):
    if not isinstance(result, dict):
        raise ValueError("Gemini response must be a dictionary")

    if set(result.keys()) != set(EXPECTED_AI_OUTPUT.keys()):
        raise ValueError("Gemini response has incorrect fields")

    if result["job_id"] != job_id:
        raise ValueError("Gemini returned an incorrect job_id")

    for key, value in result.items():
        if key == "job_id":
            continue

        if value is None:
            continue

        if type(value) is not int:
            raise ValueError(f"{key} must be an integer or null")

        if not 0 <= value <= 100:
            raise ValueError(f"{key} must be between 0 and 100")

    return result

def evaluate_internship(client, student_profile, internship):
    max_attempts = 3

    prompt = build_prompt(student_profile, internship)

    for attempt in range(1, max_attempts + 1):
        try:
            response = call_gemini(client, prompt)

            parsed_response = parse_gemini_response(response)

            validated_response = validate_gemini_response(
                parsed_response,
                internship["job_id"]
            )

            return validated_response

        except ValueError as e:
            if attempt == max_attempts:
                raise RuntimeError(
                    f"Gemini returned invalid data after {max_attempts} attempts"
                ) from e

    raise RuntimeError("Gemini evaluation failed")

def evaluate_multiple_internships(client, student_profile, internships):
    successful = []
    failed = []

    for internship in internships:
        job_id = internship.get("job_id")

        try:
            result = evaluate_internship(
                client,
                student_profile,
                internship
            )

            successful.append(result)

        except (RuntimeError, ValueError, KeyError) as e:
            failed.append({
                "job_id": job_id,
                "error": str(e)
            })

    return {
        "successful": successful,
        "failed": failed
    }

def get_latest_profile(filename):
    with open(filename, "r", encoding="utf-8") as file:
        data = json.load(file)

    profile = data.get("Student_Profile")

    if not isinstance(profile, dict) or not profile:
        raise ValueError("Student_Profile is missing or empty")

    return profile

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
        "course_of_study": profile.get("Cource_of_Study"),
        "year_of_study": profile.get("Year_of_Study"),
        "internship_duration": profile.get("Avaliable_Intership_date"),
        "preferred_month": profile.get("Preferred_month"),
        "skills": profile.get("Skills"),
        "preferred_roles": profile.get("Preferred_Roles"),
        "minimum_monthly_salary": profile.get("Minimum_monthly_Salary"),
        "preferred_location": profile.get("Preferred_location"),
        "industry_interests": profile.get("Industry_interest"),
        "company_preference": profile.get("Company_preference"),
        "past_experience": profile.get("past_experience")
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
- Use the full integer range from 0 to 100.
- Scores do not need to be multiples of 5 or 10.
- Use specific scores such as 57, 73 or 86 when justified.
- Base each score on the degree of alignment between the student's profile and internship requirements.
- Do not add artificial precision when there is insufficient information.
- Return null when an optional criterion cannot be assessed.
- Do not invent missing preferences.
- Do not assume missing internship information.
- Return null if a criterion cannot be reliably assessed from the provided student profile and internship listing.
- A score of 0 means confirmed lack of alignment, not missing information.
- Return the original job_id unchanged.
- Do not include overall scores, rankings or explanations.

EXPECTED JSON STRUCTURE:

{json.dumps(EXPECTED_AI_OUTPUT, indent=2)}

Replace the null placeholders with actual scores where
sufficient information is available.
Keep null for criteria that cannot be assessed.
"""

    return prompt

def build_skill_gap_prompt(student_profile, top_five):

    prompt = f"""
You are an AI career development assistant for InternLink.

Generate ONE overall personalised skill-gap feedback paragraph
based on the student's top five recommended internships.

STUDENT PROFILE:
{json.dumps(student_profile, indent=2)}

TOP FIVE INTERNSHIPS:
{json.dumps(top_five, indent=2)}

FEEDBACK INSTRUCTIONS:

- Analyse the SkillsMatch scores across all five internships.
- Compare the student's existing skills with the required_skills
  and job descriptions of the shortlisted internships.
- Identify the student's weakest areas of skill alignment.
- Focus on skill gaps that appear across multiple internships.
- Consider the student's existing skills and past experience.
- Suggest practical improvements such as learning relevant
  technologies, taking courses or completing projects.
- Generate ONE overall feedback paragraph of 3 to 5 sentences.
- Do not provide separate feedback for each internship.
- Do not provide separate feedback for individual skills.
- Do not discuss salary, location or company preferences.
- Do not recalculate scores or change internship rankings.
- Do not invent missing skills or internship requirements.
- Do not assume an unlisted skill is definitely absent.
- Keep the feedback constructive, specific and personalised.

JSON RESPONSE INSTRUCTIONS:

Return ONLY a valid JSON object.

- Do not include Markdown code fences.
- Do not include text outside the JSON object.
- Use exactly the field name shown below.
- The feedback must be a single string.

EXPECTED JSON STRUCTURE:

{{
    "overall_feedback": "One personalised feedback paragraph"
}}
"""

    return prompt

def generate_skill_gap_feedback(client, student_profile, top_five):
    if not top_five:
        raise ValueError("No shortlisted internships provided")

    prompt = build_skill_gap_prompt(student_profile, top_five)

    response = call_gemini(client, prompt)

    feedback = parse_gemini_response(response)

    if not isinstance(feedback, dict):
        raise ValueError("Feedback must be a dictionary")

    if set(feedback.keys()) != {"overall_feedback"}:
        raise ValueError("Feedback has incorrect fields")

    if not isinstance(feedback["overall_feedback"], str):
        raise ValueError("Overall feedback must be a string")

    if not feedback["overall_feedback"].strip():
        raise ValueError("Overall feedback cannot be empty")

    return feedback


if __name__ == "__main__":
    client = configure_gemini()
    print("Gemini client configured successfully!")

    profile_path = os.getenv(
        "STUDENT_PROFILE_JSON",
        "data/student_profile.json"
    )

    profile = get_latest_profile(profile_path)

    if profile is None:
        raise ValueError("No student profiles found.")

    ai_input = get_ai_input(profile)
    print("Updated Student Profile:")
    print(json.dumps(ai_input, indent=2))

    db_path = os.getenv("INTERNSHIP_DB", "data/internships.db")
    csv_path = os.getenv("INTERNSHIP_DATA", "data/internships.csv")

    # Connect to database
    conn = data_manager.get_conn(db_path)

    try:
        # Create tables if they don't exist
        data_manager.init_db(conn)

        # Load internship CSV if database is empty
        if data_manager.is_empty(conn, "internships"):
            data_manager.load_internships_csv(conn, csv_path)

        # Retrieve three internships for testing
        internships = data_manager.list_internships(conn, limit=3)

    finally:
        conn.close()

    # ----------------------------------
    # TEST 1: Internship Matching
    # ----------------------------------

    results = evaluate_multiple_internships(
        client,
        ai_input,
        internships
    )

    print("\nSuccessful Evaluations:")
    print(json.dumps(results["successful"], indent=2))

    print("\nFailed Evaluations:")
    print(json.dumps(results["failed"], indent=2))

    print("\nEvaluation Summary:")
    print("Total internships:", len(internships))
    print("Successful:", len(results["successful"]))
    print("Failed:", len(results["failed"]))

    # # ----------------------------------
    # # TEST 2: Overall Skill-Gap Feedback
    # # ----------------------------------     

    # # Temporary scores for testing only
    # sample_scores = [35, 50, 42, 65, 28]

    # for job, score in zip(top_five, sample_scores):
    #     job["SkillsMatch"] = score

    # feedback = generate_skill_gap_feedback(
    #     client,
    #     ai_input,
    #     top_five
    # )

    # print("\nOverall Skill-Gap Feedback:")
    # print(json.dumps(feedback, indent=2))