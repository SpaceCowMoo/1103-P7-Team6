# Tests for DataManager. Each test uses a fresh in-memory database,
# so data/internlink.db is never touched.
# Run from the project folder:  python -m unittest discover -s tests -v

import unittest

from database import Database
from Flags_class import Flags
from Internship_Class import Internship
from listing_Class import Listing
from run_models import RemovedInternship, RunResult, RunSnapshot
from Student_Profile_Class import StudentProfile
from Student_Resume_Class import StudentResume

INTERNSHIP = {
    "company_name": "Test Co", "company_type": "Start-ups", "industry": "Tech",
    "job_title": "Data Intern", "relevant_course": "ICT", "monthly_allowance": 1000,
    "work_mode": "Remote", "duration_months": 3, "required_skills": "Python",
    "location_district": "Tampines", "job_description": "Clean data",
}


class DataManagerTest(unittest.TestCase):
    def setUp(self):
        self.data = DataManager.open(":memory:")

    def tearDown(self):
        self.data.close()

    def make_results(self):
        """5 RunResult for 5 new internships, rank 1 has one flag"""
        results = []
        for rank in range(1, 6):
            job = self.data.create_internship(INTERNSHIP)
            flags = [Flags("Test flag", True)] if rank == 1 else []
            results.append(RunResult(rank, 90.0 - rank, Listing(job, flags)))
        return results

    def test_tables_are_created(self):
        self.assertEqual(set(self.data.table_counts()), {"internships", "users", "resumes", "runs"})

    def test_load_csv(self):
        data = DataManager.open(":memory:", "data/internships.csv")
        try:
            self.assertTrue(data.has_internships())
            self.assertEqual(data.get_internship(1).get_job_id(), 1)
        finally:
            data.close()

    def test_internship_columns_match_data_manager_schema(self):
        database_columns = [
            row["name"] for row in self.db.fetch_all("PRAGMA table_info(internships)")
        ]
        conn = data_manager.get_conn(":memory:")
        try:
            data_manager.init_db(conn)
            data_manager_columns = [
                row["name"]
                for row in conn.execute("PRAGMA table_info(internships)").fetchall()
            ]
        finally:
            conn.close()

        self.assertEqual(database_columns, data_manager.INTERNSHIP_COLUMNS)
        self.assertEqual(data_manager_columns, data_manager.INTERNSHIP_COLUMNS)

    def test_internship_crud(self):
        job = self.data.create_internship(INTERNSHIP)
        self.assertEqual(self.data.get_internship(job.get_job_id()).get_job_title(), "Data Intern")

        updated = self.data.update_internship(job.get_job_id(), {"monthly_allowance": 1200})
        self.assertEqual(updated.get_monthly_allowance(), 1200)
        self.assertEqual(len(self.data.list_internships(limit=-1, work_mode="Remote")), 1)
        self.assertEqual(len(self.data.list_internships(limit=-1, partial=True, job_title="data")), 1)

        self.assertTrue(self.data.delete_internship(job.get_job_id()))
        self.assertIsNone(self.data.get_internship(job.get_job_id()))

    def test_user_and_resume(self):
        user = self.data.create_user("joe_tan", name="Joe", age=21, student_id="S123")
        user_id = user.get_login_details().get_user_id()
        self.assertEqual(self.data.get_user_by_username("JOE_TAN").get_name(), "Joe")
        with self.assertRaises(ValueError):
            self.data.create_user("joe_tan")  # username taken

        self.assertIsNone(self.data.load_resume(user_id))
        self.data.save_resume(user_id, StudentResume(Skills=["Excel"]))
        self.data.save_resume(user_id, StudentResume(Skills=["Excel", "Python"]))  # overwrites
        self.assertEqual(self.data.load_resume(user_id).get_Skills(), ["Excel", "Python"])
        # get_user comes with its one resume
        self.assertEqual(self.data.get_user(user_id).get_Student_Resume()[0].get_Skills(),
                         ["Excel", "Python"])

    def test_resume_round_trip(self):
        """Every resume field, including past internships, survives save + load"""
        user_id = self.data.create_user("joe_tan").get_login_details().get_user_id()
        resume = StudentResume(
            Courses=["Computing Science"], Year_of_Study=2, Duration_of_internship=6,
            available_internship_date="01/01/2027 - 30/06/2027", Skills=["Python"],
            Preferred_role=["Data Analyst"], Minimum_monthly_salary=1500.0,
            Preferred_location=["East"], preferred_work_arrangement=["Hybrid"],
            industry_interest=["Fintech"], company_preference=["Start-ups"],
            Past_internships=[PastInternship("School", "IT intern", "Set up laptops", 3,
                                             "11/05/2024", "14/08/2024")],
        )
        self.data.save_resume(user_id, resume)
        self.assertEqual(self.data.load_resume(user_id).fetch_Student_Resume_details(),
                         resume.fetch_Student_Resume_details())

    def test_resume_json_round_trip_preserves_all_fields(self):
        user_id = StudentProfile.create(self.db, "resume_user").get_login_details().get_user_id()
        resume = StudentResume(
            Courses="Computer Science",
            Year_of_Study=2,
            Duration_of_internship=4,
            available_internship_date="01/01/2025 - 30/04/2025",
            Skills=["Python", "SQL"],
            Preferred_role=["Developer"],
            Minimum_monthly_salary=1200.0,
            Preferred_location=["East"],
            preferred_work_arrangement=["Hybrid"],
            industry_interest=["Technology"],
            company_preference=["MNC"],
            Past_internships=[
                PastInternship(
                    "Test Co",
                    "Developer",
                    "Built an internal tool",
                    3,
                    "01/01/2024",
                    "31/03/2024",
                )
            ],
        )

        resume.save(self.db, user_id)
        loaded_resume = StudentResume.load(self.db, user_id)

        self.assertEqual(
            loaded_resume.fetch_Student_Resume_details(),
            resume.fetch_Student_Resume_details(),
        )

    def test_run_history(self):
        user_id = self.data.create_user("joe_tan").get_login_details().get_user_id()
        run = self.data.save_run(user_id, StudentResume(Skills=["Excel"]),
                                 self.make_results(), ["Learn SQL."])

        self.assertEqual(run.get_feedback(), ["Learn SQL."])
        self.assertEqual(run.get_resume().get_Skills(), ["Excel"])
        top = run.get_results()[0]
        self.assertEqual(top.get_score(), 89.0)
        self.assertEqual(top.get_listing().get_Flags()[0].get_flag_name(), "Test flag")
        self.assertEqual(len(self.data.list_runs(user_id)), 1)

        # Another user can't see it
        other_id = self.data.create_user("amy").get_login_details().get_user_id()
        self.assertIsNone(self.data.get_run(run.get_run_id(), other_id))
        self.assertFalse(self.data.delete_run(run.get_run_id(), other_id))

        # A deleted internship shows as "Internship removed"
        self.data.delete_internship(top.get_listing().get_internship().get_job_id())
        again = self.data.get_run(run.get_run_id(), user_id)
        self.assertIsInstance(again.get_results()[0].get_listing().get_internship(), RemovedInternship)

        self.assertTrue(self.data.delete_run(run.get_run_id(), user_id))
        self.assertEqual(self.data.list_runs(user_id), [])

    def test_delete_user_removes_resume_and_runs(self):
        user_id = self.data.create_user("joe_tan").get_login_details().get_user_id()
        self.data.save_resume(user_id, StudentResume(Skills=["Excel"]))
        self.data.save_run(user_id, StudentResume(), self.make_results(), ["Tip."])

        self.assertTrue(self.data.delete_user(user_id))
        self.assertIsNone(self.data.get_user(user_id))
        self.assertEqual(self.data.table_counts()["resumes"], 0)
        self.assertEqual(self.data.table_counts()["runs"], 0)


if __name__ == "__main__":
    unittest.main()
