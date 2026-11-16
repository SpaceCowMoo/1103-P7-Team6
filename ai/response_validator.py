
import json


class AIResponseValidator:

    EXPECTED_AI_OUTPUT = {
        "job_id": int,
        "SkillsMatch": int,
        "RoleMatch": int,
        "IndustryInterestMatch": int,
        "ExperienceMatch": int,
        "CompanyPreferenceMatch": int
    }

    def parse_gemini_response(self, response_text):
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

    # Validate the fields, job ID and score ranges of an AI-assessed internship
    # Reject unexpected fields, incorrect IDs and invalid score values
    def validate_gemini_response(self, result, job_id):
        if not isinstance(result, dict):
            raise ValueError("Gemini response must be a dictionary")

        if set(result.keys()) != set(self.EXPECTED_AI_OUTPUT.keys()):
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

    def validate_shortlist_response(self, result, internships):
        if not isinstance(result, dict):
            raise ValueError("Top-five response must be a dictionary")

        if set(result.keys()) != {"selected_internships"}:
            raise ValueError("Incorrect top-five response fields")

        selected = result["selected_internships"]

        if not isinstance(selected, list) or not 5 <= len(selected) <= 10:
            raise ValueError(
                "Gemini must select between 5 and 10 internships"
            )

        # Collect valid job IDs to prevent Gemini from selecting nonexistent listings
        valid_job_ids = {
            internship["job_id"] for internship in internships
        }

        # Track selected IDs to detect duplicate internship recommendations
        seen_ids = set()

        for entry in selected:
            if not isinstance(entry, dict):
                raise ValueError("Each selection must be a dictionary")

            job_id = entry.get("job_id")

            if type(job_id) is not int or job_id not in valid_job_ids:
                raise ValueError(f"Invalid selected job_id: {job_id}")

            if job_id in seen_ids:
                raise ValueError(f"Duplicate selected job_id: {job_id}")

            self.validate_gemini_response(entry, job_id)
            seen_ids.add(job_id)

        return selected

    def validate_feedback_response(self, result):
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

