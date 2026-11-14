# Simple tests for the database. Each test uses a fresh in-memory database,
# so data/internlink.db is never touched.
# Run from the project folder:  python -m unittest discover -s tests -v

import unittest

from database import Database
from models.flags import Flags
from models.internship import Internship
from models.listing import Listing
from models.removed_internship import RemovedInternship
from models.run_result import RunResult
from models.run_snapshot import RunSnapshot
from models.student_profile import StudentProfile
from models.student_resume import StudentResume

INTERNSHIP = {
    "company_name": "Test Co", "company_type": "Start-ups", "industry": "Tech",
    "job_title": "Data Intern", "relevant_course": "ICT", "monthly_allowance": 1000,
    "work_mode": "Remote", "duration_months": 3, "required_skills": "Python",
    "location_district": "Tampines", "job_description": "Clean data",
}


class DatabaseTest(unittest.TestCase):
    def setUp(self):
        self.db = Database.open(":memory:")

    def tearDown(self):
        self.db.close()

    def make_results(self):
        """5 RunResult for 5 new internships, rank 1 has one flag"""
        results = []
        for rank in range(1, 6):
            job = Internship.create(self.db, INTERNSHIP)
            flags = [Flags("Test flag", True)] if rank == 1 else []
            results.append(RunResult(rank, 90.0 - rank, Listing(job, flags)))
        return results

    def test_tables_are_created(self):
        self.assertEqual(set(self.db.table_counts()), {"internships", "users", "resumes", "runs"})

    def test_internship_crud(self):
        job = Internship.create(self.db, INTERNSHIP)
        self.assertEqual(Internship.get(self.db, job.get_job_id()).get_job_title(), "Data Intern")

        self.assertTrue(job.update(self.db, {"monthly_allowance": 1200}))
        self.assertEqual(job.get_monthly_allowance(), 1200)
        self.assertEqual(len(Internship.list_all(self.db, limit=-1, work_mode="Remote")), 1)

        self.assertTrue(job.delete(self.db))
        self.assertIsNone(Internship.get(self.db, job.get_job_id()))

    def test_user_and_resume(self):
        user = StudentProfile.create(self.db, "joe_tan", name="Joe", age=21, student_id="S123")
        user_id = user.get_login_details().get_user_id()
        self.assertEqual(StudentProfile.get_by_username(self.db, "JOE_TAN").get_name(), "Joe")
        with self.assertRaises(ValueError):
            StudentProfile.create(self.db, "joe_tan")  # username taken

        self.assertIsNone(StudentResume.load(self.db, user_id))
        StudentResume(Skills=["Excel"]).save(self.db, user_id)
        StudentResume(Skills=["Excel", "Python"]).save(self.db, user_id)  # overwrites
        self.assertEqual(StudentResume.load(self.db, user_id).get_Skills(), ["Excel", "Python"])

    def test_run_history(self):
        user_id = StudentProfile.create(self.db, "joe_tan").get_login_details().get_user_id()
        run = RunSnapshot.create(self.db, user_id, StudentResume(Skills=["Excel"]),
                                 self.make_results(), ["Learn SQL."])

        self.assertEqual(run.get_feedback(), ["Learn SQL."])
        self.assertEqual(run.get_resume().get_Skills(), ["Excel"])
        top = run.get_results()[0]
        self.assertEqual(top.get_score(), 89.0)
        self.assertEqual(top.get_listing().get_Flags()[0].get_flag_name(), "Test flag")
        self.assertEqual(len(RunSnapshot.list_for_user(self.db, user_id)), 1)

        # Another user can't see it
        other_id = StudentProfile.create(self.db, "amy").get_login_details().get_user_id()
        self.assertIsNone(RunSnapshot.get(self.db, run.get_run_id(), other_id))

        # A deleted internship shows as "Internship removed"
        top.get_listing().get_internship().delete(self.db)
        again = RunSnapshot.get(self.db, run.get_run_id(), user_id)
        self.assertIsInstance(again.get_results()[0].get_listing().get_internship(), RemovedInternship)

        self.assertTrue(run.delete(self.db))
        self.assertEqual(RunSnapshot.list_for_user(self.db, user_id), [])


if __name__ == "__main__":
    unittest.main()
