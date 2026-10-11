from ai_manager import evaluate_internship
import json


class FakeResponse:
    def __init__(self, text):
        self.text = text


class FakeModel:
    def __init__(self):
        self.calls = 0

    def generate_content(self, **kwargs):
        self.calls += 1

        if self.calls <= 3:
            return FakeResponse("invalid json")

        if self.calls == 2:
            return FakeResponse(json.dumps({
                "job_id": 1,
                "SkillsMatch": 150,
                "RoleMatch": 70,
                "IndustryInterestMatch": 60,
                "ExperienceMatch": 50,
                "SalaryMatch": 80,
                "WorkArrangementMatch": None,
                "LocationMatch": 90,
                "CompanyPreferenceMatch": None
            }))

        return FakeResponse(json.dumps({
            "job_id": 1,
            "SkillsMatch": 75,
            "RoleMatch": 70,
            "IndustryInterestMatch": 60,
            "ExperienceMatch": 50,
            "SalaryMatch": 80,
            "WorkArrangementMatch": None,
            "LocationMatch": 90,
            "CompanyPreferenceMatch": None
        }))


class FakeClient:
    def __init__(self):
        self.models = FakeModel()


client = FakeClient()

student_profile = {
    "skills": ["Python", "SQL"],
    "preferred_roles": ["Data Analyst"]
}

internship = {
    "job_id": 1,
    "job_title": "Data Analyst Intern",
    "required_skills": "Python, SQL"
}

try:
    result = evaluate_internship(
        client,
        student_profile,
        internship
    )

except RuntimeError as e:
    print("Retry limit reached!")
    print(e)
    print("Total API attempts:", client.models.calls)