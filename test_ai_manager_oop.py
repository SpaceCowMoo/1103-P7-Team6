
import json
import unittest

from ai.ai_client import AIClient
from ai_manager import AIManager


class MockAIClient(AIClient):
    """
    Fake AI client for testing without making real Gemini API calls.
    """

    def __init__(self, responses):
        self.responses = list(responses)
        self.call_count = 0
        self.connected = False

    def connect(self):
        self.connected = True

    def generate(self, prompt):
        self.call_count += 1

        if not self.responses:
            raise RuntimeError("No mock responses remaining")

        response = self.responses.pop(0)

        if isinstance(response, Exception):
            raise response

        return response


class TestAIManager(unittest.TestCase):

    def setUp(self):
        self.profile = {
            "internship_duration": 3,
            "course_of_study": "Applied Computing",
            "year_of_study": "Year 2",
            "skills": ["Python", "SQL"],
            "preferred_roles": ["Data Analyst"],
            "industry_interests": ["Technology"],
            "past_experience": {}
        }

        self.internships = [
            {
                "job_id": i,
                "job_title": f"Data Intern {i}",
                "duration_months": 3,
                "required_skills": ["Python", "SQL"],
                "job_description": "Analyse business data",
                "industry": "Technology",
                "company_type": "SME"
            }
            for i in range(1, 7)
        ]

    def make_shortlist(self):
        return {
            "selected_internships": [
                {
                    "job_id": i,
                    "SkillsMatch": 85,
                    "RoleMatch": 90,
                    "IndustryInterestMatch": 80,
                    "ExperienceMatch": None,
                    "CompanyPreferenceMatch": None
                }
                for i in range(1, 6)
            ]
        }

    def make_feedback(self):
        return {
            "overall_feedback": {
                "points": [
                    "Practise SQL joins using sample datasets.",
                    "Build a Python data analysis project.",
                    "Create a portfolio showcasing your work."
                ]
            }
        }

    def make_manager(self, responses):
        client = MockAIClient(responses)
        manager = AIManager(client=client)
        return manager, client

    def test_successful_pipeline(self):
        manager, client = self.make_manager([
            json.dumps(self.make_shortlist()),
            json.dumps(self.make_feedback())
        ])

        manager.connect()

        result = manager.run_ai_pipeline(
            self.profile, self.internships
        )

        self.assertEqual(
            len(result["selected_internships"]["internships"]), 5
        )
        self.assertEqual(
            len(result["overall_feedback"]["points"]), 3
        )
        self.assertEqual(client.call_count, 2)
        self.assertTrue(client.connected)

    def test_duration_filter(self):
        manager, _ = self.make_manager([])

        internships = self.internships + [
            {
                "job_id": 99,
                "duration_months": 6
            }
        ]

        eligible = manager.filter_by_duration(
            self.profile, internships
        )

        self.assertEqual(len(eligible), 6)
        self.assertNotIn(
            99, [job["job_id"] for job in eligible]
        )

    def test_invalid_json_retry(self):
        manager, client = self.make_manager([
            "invalid json",
            json.dumps(self.make_shortlist())
        ])

        selected = manager.select_shortlisted_internships(
            self.profile, self.internships
        )

        self.assertEqual(len(selected), 5)
        self.assertEqual(client.call_count, 2)

    def test_duplicate_job_id_retry(self):
        invalid_shortlist = self.make_shortlist()
        invalid_shortlist["selected_internships"][1]["job_id"] = 1

        manager, client = self.make_manager([
            json.dumps(invalid_shortlist),
            json.dumps(self.make_shortlist())
        ])

        selected = manager.select_shortlisted_internships(
            self.profile, self.internships
        )

        self.assertEqual(len(selected), 5)
        self.assertEqual(client.call_count, 2)

    def test_invalid_score_retry(self):
        invalid_shortlist = self.make_shortlist()
        invalid_shortlist["selected_internships"][0]["SkillsMatch"] = 120

        manager, client = self.make_manager([
            json.dumps(invalid_shortlist),
            json.dumps(self.make_shortlist())
        ])

        selected = manager.select_shortlisted_internships(
            self.profile, self.internships
        )

        self.assertEqual(len(selected), 5)
        self.assertEqual(client.call_count, 2)

    def test_invalid_feedback_retry(self):
        invalid_feedback = {
            "overall_feedback": {
                "points": ["Only one point"]
            }
        }

        manager, client = self.make_manager([
            json.dumps(invalid_feedback),
            json.dumps(self.make_feedback())
        ])

        feedback = manager.generate_skill_gap_feedback(
            self.profile, self.internships[:5]
        )

        self.assertEqual(len(feedback["points"]), 3)
        self.assertEqual(client.call_count, 2)

    def test_three_invalid_responses(self):
        manager, client = self.make_manager([
            "invalid",
            "invalid",
            "invalid"
        ])

        with self.assertRaises(RuntimeError):
            manager.select_shortlisted_internships(
                self.profile, self.internships
            )

        self.assertEqual(client.call_count, 3)

    def test_api_failure(self):
        manager, client = self.make_manager([
            RuntimeError("API unavailable")
        ])

        with self.assertRaises(RuntimeError):
            manager.select_shortlisted_internships(
                self.profile, self.internships
            )

        self.assertEqual(client.call_count, 1)


if __name__ == "__main__":
    unittest.main()
