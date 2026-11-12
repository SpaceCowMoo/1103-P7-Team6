# Simple tests for the database package. Each test uses a fresh in-memory database.
# Run from the project folder:  python -m unittest discover -s tests

import unittest

from database import DataManager
from Flags_class import Flags
from listing_Class import Listing
from run_models import RunResult
from Student_Resume_Class import StudentResume

INTERNSHIP = {
    "company_name": "Test Co", "company_type": "Start-ups", "industry": "Tech",
    "job_title": "Data Intern", "relevant_course": "ICT", "monthly_allowance": 1000,
    "work_mode": "Remote", "duration_months": 3, "required_skills": "Python",
    "location_district": "Tampines", "job_description": "Clean data",
}


class DatabaseTest(unittest.TestCase):
    def setUp(self):
        self.dm = DataManager.open(":memory:")

    def tearDown(self):
        self.dm.close()

    def test_tables_are_created(self):
        self.assertEqual(set(self.dm.table_counts()), {"internships", "users", "resumes", "runs"})

    def test_internship_crud(self):
        job_id = self.dm.internships.create(INTERNSHIP)
        self.assertEqual(self.dm.internships.get(job_id).get_job_title(), "Data Intern")

        self.dm.internships.update(job_id, {"monthly_allowance": 1200})
        self.assertEqual(self.dm.internships.get(job_id).get_monthly_allowance(), 1200)

        self.assertTrue(self.dm.internships.delete(job_id))
        self.assertIsNone(self.dm.internships.get(job_id))

    def test_user_resume_and_run(self):
        user = self.dm.users.create("joe_tan", name="Joe", age=21, student_id="S123")
        user_id = user.get_login_details().get_user_id()
        self.assertEqual(self.dm.users.get_by_username("joe_tan").get_name(), "Joe")

        self.dm.resumes.save(user_id, StudentResume(Skills=["Excel"]))
        self.assertEqual(self.dm.resumes.get(user_id).get_Skills(), ["Excel"])

        job_ids = [self.dm.internships.create(INTERNSHIP) for _ in range(5)]
        results = [
            RunResult(rank, 90.0 - rank, Listing(self.dm.internships.get(job_id), [Flags("Test flag", True)]))
            for rank, job_id in enumerate(job_ids, start=1)
        ]
        run_id = self.dm.runs.save(user_id, self.dm.resumes.get(user_id), results, ["Learn SQL."])

        run = self.dm.runs.get(run_id, user_id)
        self.assertEqual(run.get_feedback(), ["Learn SQL."])
        self.assertEqual(run.get_results()[0].get_score(), 89.0)
        self.assertEqual(len(self.dm.runs.list_for_user(user_id)), 1)


if __name__ == "__main__":
    unittest.main()
