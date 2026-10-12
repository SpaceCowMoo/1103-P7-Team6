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

    profile = data.get("student_profile")

    if not isinstance(profile, dict) or not profile:
        raise ValueError("Student_Profile is missing or empty")

    return profile

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
select between FIVE and TEN suitable internships for this student.

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

SELECTION PRIORITY:

- Prioritise course relevance, academic-level suitability,
  demonstrated skills and preferred roles.
- Consider industry interests, experience and company
  preferences when comparing otherwise suitable internships.
- Do not prioritise an internship merely because it offers
  a higher monthly allowance.
- Do not select an internship with substantially unsuitable
  responsibilities solely to fill the shortlist.

ACADEMIC LEVEL SUITABILITY:

- Assess whether each internship is realistic for the student's
  current year of study, course and demonstrated abilities.
- Use the internship's job_title, required_skills,
  relevant_course and job_description to assess suitability.
- A Year 1 student should generally be considered for
  entry-level internships with appropriate learning opportunities.
- Do not assume a student possesses advanced technical knowledge
  simply because they are studying a related course.
- Treat positions requiring substantial system architecture,
  technical leadership or advanced specialist expertise
  as less suitable unless the student demonstrates the
  necessary skills and relevant experience.
- Do not reject an internship solely because its job title
  sounds advanced. Evaluate the actual responsibilities.
- Consider relevant projects, skills and past experience
  as evidence that a student can handle more advanced work.
- Prefer internships where the student has a reasonable
  foundation to perform the work and learn the missing skills.
- Do not invent entry requirements that are not present
  in the internship listing.

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

{json.dumps(EXPECTED_SHORTLIST_OUTPUT, indent=2)}

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


def build_skill_gap_prompt(student_profile, shortlisted_internships):
    return f"""
You are an AI internship career advisor.

Analyse the student's profile and the shortlisted internships.

STUDENT PROFILE:
{json.dumps(student_profile, indent=2)}

SHORTLISTED INTERNSHIPS:
{json.dumps(shortlisted_internships, indent=2)}

TASK:
Generate personalised skill-gap feedback for the student.


INSTRUCTIONS:

- Return 3 to 5 personalised, actionable feedback points.
- Each point must identify a relevant skill gap and
  recommend a specific action to address it.
- Compare the student's existing skills with the required_skills
  and job_description of the shortlisted internships.
- Prioritise skills that appear across multiple shortlisted
  internships, especially those relevant to preferred roles.
- Consider the student's course, year of study,
  existing skills and past experience.
- Build upon the student's existing knowledge rather
  than recommending only unrelated advanced technologies.
- Suggest practical learning activities such as small projects,
  exercises, tutorials or portfolio development.
- Recommend activities realistic for the student's current
  academic level.
- Where appropriate, explain how the activity helps prepare
  the student for the shortlisted internship responsibilities.
- Do not claim that the student lacks a skill if it is
  already demonstrated in their profile.
- Do not assume that the student has unlisted skills.
- Do not invent internship requirements.
- Avoid generic advice such as "improve your skills"
  or "gain more experience".
- Avoid repeating the same recommendation.
- Each point should be one concise, actionable sentence.
- Do not calculate match scores or rank internships.

OUTPUT FORMAT:
Return only valid JSON:

{{
    "overall_feedback": {{
        "points": [
            "First actionable recommendation.",
            "Second actionable recommendation.",
            "Third actionable recommendation."
        ]
    }}
}}
"""


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

    # Step 3: Generate structured overall skill-gap feedback
    feedback = generate_skill_gap_feedback(
        client,
        student_profile,
        shortlisted_internships
    )

    return {
        "selected_internships": {
            "internships": shortlisted_internships
        },
        "overall_feedback": feedback
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

    print("\nUpdated Student Profile:")
    print(json.dumps(ai_input, indent=2))

    db_path = os.getenv("INTERNSHIP_DB", "data/internships.db")
    csv_path = os.getenv("INTERNSHIP_DATA", "data/internships.csv")

    print("\nDatabase being used:", os.path.abspath(db_path))

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

        # Extract the two output dictionaries
        selected_output = results["selected_internships"]
        feedback_output = results["overall_feedback"]

        shortlisted_internships = selected_output["internships"]
        feedback_points = feedback_output["points"]

        # Display shortlisted internships
        print("\n========== AI SHORTLISTED INTERNSHIPS ==========")

        for index, internship in enumerate(shortlisted_internships, 1):
            print(f"\nInternship {index}:")
            print(json.dumps(internship, indent=2))

        # Display overall skill-gap feedback
        print("\n========== OVERALL SKILL-GAP FEEDBACK ==========")

        for index, point in enumerate(feedback_points, 1):
            print(f"{index}. {point}")

        # Evaluation summary
        print("\n========== EVALUATION SUMMARY ==========")
        print("Total available internships:", len(internships))
        print("Selected internships:", len(shortlisted_internships))
        print("Feedback points generated:", len(feedback_points))

        print("\nAI Manager pipeline completed successfully!")

    except (RuntimeError, ValueError, KeyError, TypeError) as e:
        print("\nAI Manager failed:", e)
