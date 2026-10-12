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
    "CompanyPreferenceMatch": None
}

EXPECTED_SHORTLIST_OUTPUT = {
    "selected_internships": [
        EXPECTED_AI_OUTPUT
    ]
}

def configure_gemini():
    load_dotenv(override=True)

    api_key = os.getenv("GEMINI_API_KEY")

    if not api_key:
        raise ValueError("GEMINI_API_KEY is missing from .env")

    client = genai.Client(api_key=api_key)

    return client

def call_gemini(client, prompt):
    try:
        response = client.models.generate_content(
            model="gemini-3.8-flash",
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

def get_ai_input(profile):
    ai_input = {
        "course_of_study": profile.get("Cource_of_Study"),
        "year_of_study": profile.get("Year_of_Study"),
        "internship_duration": profile.get("Avaliable_Intership_date"),
        "skills": profile.get("Skills"),
        "preferred_roles": profile.get("Preferred_Roles"),
        "minimum_monthly_salary": profile.get("Minimum_monthly_Salary"),
        "preferred_location": profile.get("Preferred_location"),
        "preferred_work_arrangement": profile.get("Preferred_Work_Arrangement"),
        "industry_interests": profile.get("Industry_interest"),
        "company_preference": profile.get("Company_preference"),
        "past_experience": profile.get("past_experience")
    }

    return ai_input

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
Compare the student's existing skills with the
internship's required_skills and job_description.

- Give a high score when most required skills are covered.
- Give a moderate score when some required skills are covered.
- Give a low score when few required skills are covered.
- Consider transferable and closely related skills.
- Do not require exact keyword matches.
- Use 0 only when there is no meaningful skill alignment.
- Return null if the required skills cannot be assessed.

2. RoleMatch:
Compare the student's preferred_roles with the
internship's job_title and job_description.

- Give a high score for a direct role match.
- Give a moderate score for a closely related role.
- Give a low score for a role with limited overlap.
- Consider similarities in actual responsibilities,
  not just job titles.
- Use 0 only when there is no meaningful role alignment.
- Return null if the student has no preferred role
  or the internship role cannot be assessed.

3. IndustryInterestMatch:
Compare the student's industry_interests with
the internship's industry.

- Give a high score for a direct industry match.
- Give a moderate score for related industries.
- Give a low score for industries with limited overlap.
- Consider transferable interests across industries.
- Use 0 only when there is no meaningful alignment.
- Return null if industry information or the student's
  industry preference is missing.

4. ExperienceMatch:
Compare the student's past_experience with the
internship's job_description and responsibilities.

- Give a high score for directly relevant experience.
- Give a moderate score for transferable experience.
- Give a low score for limited relevant experience.
- Consider responsibilities and transferable skills,
  not just previous job titles.
- Use 0 only when the provided experience has no
  meaningful relevance.
- Return null if past experience is missing or empty.
- Do not assume that missing experience means the
  student is unqualified.

5. CompanyPreferenceMatch:
Compare the student's company_preference with
the internship's company_type.

- Give a high score for a direct company type match.
- Give a moderate score for related company types.
- Give a low score for weak alignment.
- Use 0 only when there is no meaningful alignment.
- Return null if the student has no company preference.
- Return null if company_type is missing or unknown.
- Do not guess company type from the company name alone.

SCORING RULES:

- Assess all five criteria independently.
- Give each assessable criterion an integer score
  from 0 to 100.
- Salary, work arrangement and location are handled
  separately by the Logic Manager.
- Do not generate scores or flags for these fields.

SCORING GUIDELINES:

90-100: Excellent alignment.
70-89: Strong alignment.
40-69: Moderate alignment.
1-39: Weak alignment.
0: No meaningful alignment.
null: Insufficient information to assess the criterion.

IMPORTANT SCORING PRINCIPLES:

- A partial match must receive an appropriate
  non-zero score.
- Do not automatically assign 0 simply because
  the student's profile and internship differ.
- Consider transferable skills, related roles
  and partial alignment where appropriate.
- Do not invent transferable skills or interests
  without reasonable support from the provided data.
- Use 0 only for a confirmed complete mismatch.
- Use null when there is insufficient information.
- Missing optional preferences must result in null,
  not 0.
- Do not give high scores merely because two fields
  share a broad or generic keyword.
- Scores should reflect actual alignment, not
  artificial precision.
- Scores do not need to be multiples of 5 or 10.
- Use only the supplied student and internship data.
- Do not calculate an overall match score.
- Do not rank internships.
- Do not apply business rules or flags.
- Do not provide individual internship explanations.

JSON RESPONSE INSTRUCTIONS:

Return ONLY a valid JSON object.

- Do not include Markdown code fences.
- Do not include text outside the JSON object.
- Use exactly the field names shown below.
- All scores must be integers from 0 to 100 or null.
- Return the original job_id unchanged.
- Do not include additional fields.

EXPECTED JSON STRUCTURE:

{json.dumps(EXPECTED_AI_OUTPUT, indent=2)}

Replace the null placeholders with actual scores where
sufficient information is available.
Keep null for criteria that cannot be assessed.
"""

    return prompt

def build_shortlist_prompt(student_profile, internships):

    prompt = f"""
You are the AI internship matching engine for InternLink.

Your task is to analyse ALL the internship listings and
select the FIVE most suitable internships for this student.

STUDENT PROFILE:
{json.dumps(student_profile, indent=2)}

AVAILABLE INTERNSHIPS:
{json.dumps(internships, indent=2)}

MATCHING CRITERIA:

1. SkillsMatch:
Compare student skills with required_skills and job_description.
Consider transferable skills and closely related technologies.
Return null only when the required skills cannot be assessed.

2. RoleMatch:
Compare preferred_roles with job_title and job_description.
Consider the actual job responsibilities.
Return null when the student has no preferred role or
the internship role cannot be assessed.

3. IndustryInterestMatch:
Compare industry_interests with the internship industry.
Consider related industries and transferable interests.
Return null when the student has no industry preference
or the internship industry is unknown.

4. ExperienceMatch:
Compare past_experience with job_description.
Consider directly relevant and transferable experience.
Return null when past_experience is missing or empty.
Do not penalise students for missing optional experience.

5. CompanyPreferenceMatch:
Compare company_preference with company_type.
An exact company type match receives 100.
Return null only when the preference or company type
is missing, empty or unknown.
Do not guess company type from the company name alone.

SELECTION INSTRUCTIONS:

- Analyse all internships provided in the dataset.
- Select between FIVE and TEN DISTINCT internships.
- Aim to select TEN suitable internships when enough exist.
- The Logic Manager will select and rank the final five.
- Consider the student's course of study and year of study
  when assessing internship suitability.
- Course suitability must be determined semantically using
  relevant_course, job_title and job_description.
- Consider the student's available internship duration.
- Do not select internships that exceed the student's
  available duration.
- Interpret preferred_roles as free text.
- Match preferred roles based on job responsibilities and
  meaning, not exact job title keywords.
- Interpret industry_interests as free text.
- Consider related industries and relevant job responsibilities.
- Analyse the full past_experience dictionary, including
  its free-text job description.
- Consider relevant and transferable work experience.
- Consider salary, preferred work arrangement and location
  when selecting suitable internships.
- Treat these three fields as preferences, not scoring criteria.
- Prefer internships that satisfy more student preferences
  when their overall suitability is otherwise comparable.
- Do not automatically exclude internships that differ from
  optional preferences.
- Do not invent qualifications, skills or job requirements.
- Treat missing optional preferences as neutral.
- Do not calculate weighted overall scores.
- Do not assign final rankings.
- Do not apply salary, location or work arrangement flags.
- Return only job IDs from the supplied dataset.

SCORING INSTRUCTIONS:

- Assess all five matching criteria independently.
- Give each assessable criterion an integer from 0 to 100.
- 90-100: Excellent alignment.
- 70-89: Strong alignment.
- 40-69: Moderate alignment.
- 1-39: Weak alignment.
- 0: No meaningful alignment.
- null: Insufficient information or missing optional preference.
- Consider partial matches and transferable skills.
- Do not treat missing optional preferences as zero.
- Do not artificially change criterion scores merely
  because an internship was previously rejected.
- Salary, work arrangement and location are handled
  separately by the Logic Manager.
- Do not generate scores or flags for these fields.
- Do not provide individual internship explanations.

IMPORTANT SCORING PRINCIPLES:

- Use 0 only for a confirmed complete mismatch.
- Use null when there is insufficient information.
- Missing optional preferences must result in null,
  not 0.
- Do not give high scores merely because two fields
  share a broad or generic keyword.
- Scores should reflect actual alignment.
- Scores do not need to be multiples of 5 or 10.
- Use only the supplied student and internship data.
- Do not calculate an overall match score.
- Do not rank internships.
- Do not apply business rules or flags.

JSON RESPONSE INSTRUCTIONS:

Return ONLY a valid JSON object with this structure:

{json.dumps(EXPECTED_TOP_FIVE_OUTPUT, indent=2)}

- selected_internships must contain between 5 and 10 objects.
- Select 10 when at least 10 suitable internships are available.
- Each object must contain exactly the six fields shown.
- Return the original job_id unchanged.
- All scores must be integers from 0 to 100 or null.
- Do not include extra fields.
- Do not include Markdown code fences.
- Do not include text outside the JSON object.
"""

    return prompt

def validate_shortlist_response(result, internships):
    if not isinstance(result, dict):
        raise ValueError("Top-five response must be a dictionary")

    if set(result.keys()) != {"selected_internships"}:
        raise ValueError("Incorrect top-five response fields")

    selected = result["selected_internships"]

    if not isinstance(selected, list) or not 5 <= len(selected) <= 10:
        raise ValueError(
            "Gemini must select between 5 and 10 internships"
        )

    valid_job_ids = {
        internship["job_id"] for internship in internships
    }

    seen_ids = set()

    for entry in selected:
        if not isinstance(entry, dict):
            raise ValueError("Each selection must be a dictionary")

        job_id = entry.get("job_id")

        if type(job_id) is not int or job_id not in valid_job_ids:
            raise ValueError(f"Invalid selected job_id: {job_id}")

        if job_id in seen_ids:
            raise ValueError(f"Duplicate selected job_id: {job_id}")

        validate_gemini_response(entry, job_id)
        seen_ids.add(job_id)

    return selected


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

def run_ai_pipeline(client, student_profile, internships):
    eligible_internships = filter_by_duration(
        student_profile,
        internships
    )
    selected_scores = select_shortlisted_internships(
        client,
        student_profile,
        eligible_internships
    )

    # Step 2: Match selected job IDs to their full internship records
    internship_lookup = {
        internship["job_id"]: internship
        for internship in eligible_internships
    }

    shortlisted_internships = []

    for scores in selected_scores:
        job_id = scores["job_id"]

        internship = internship_lookup[job_id].copy()

        # Combine internship details with the five AI scores
        internship.update(scores)

        shortlisted_internships.append(internship)

    # Step 3: Generate one overall skill-gap feedback paragraph
    feedback = generate_skill_gap_feedback(
        client,
        student_profile,
        shortlisted_internships
    )

    # Step 4: Return results for the other managers
    return {
        "selected_internships": shortlisted_internships,
        "overall_feedback": feedback["overall_feedback"]
    }

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
    print("Database being used:", os.path.abspath(db_path))
    csv_path = os.getenv("INTERNSHIP_DATA", "data/internships.csv")

    # Connect to database
    conn = data_manager.get_conn(db_path)

    try:
        # Create tables if they don't exist
        data_manager.init_db(conn)

        # Load internship CSV if database is empty
        if data_manager.is_empty(conn, "internships"):
            data_manager.load_internships_csv(conn, csv_path)

        # Retrieve all internships for AI selection
        internships = data_manager.list_internships(conn, limit=-1)

    finally:
        conn.close()

    # ----------------------------------
    # TEST: Complete AI Manager Pipeline
    # ----------------------------------

    try:
        results = run_ai_pipeline(
            client,
            ai_input,
            internships
        )

        print("\nAI Shortlisted Internships:")
        print(json.dumps(results["selected_internships"], indent=2))

        print("\nOverall Skill-Gap Feedback:")
        print(results["overall_feedback"])

        print("\nEvaluation Summary:")
        print("Total available internships:", len(internships))
        print("Selected internships:", len(results["selected_internships"]))

    except (RuntimeError, ValueError) as e:
        print("\nAI Manager failed:", e)
