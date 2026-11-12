# database_example.py
# How to use the database from your own code. Copy the part you need.
#
#   python database_example.py
#
# This uses an in-memory database (":memory:"), so it never touches data/internlink.db.
# In the real app, open it with DataManager.open(DB_PATH, INTERNSHIP_DATA) instead.

from database import DataManager
from Flags_class import Flags
from listing_Class import Listing
from Past_internship_done_class import PastInternship
from run_models import RunResult
from Student_Resume_Class import StudentResume


def main():
    # ---------- open (do this once at startup, close once at the end) ----------
    dm = DataManager.open(":memory:", "data/internships.csv")
    print("Rows per table:", dm.table_counts())

    # ---------- internships -> Internship objects ----------
    internship = dm.internships.get(1)                  # one, or None
    print("\nJob 1:", internship.get_job_title(), "at", internship.get_company_name())

    hybrid = dm.internships.list_all(limit=-1, work_mode="Hybrid")   # exact match, limit=-1 = all
    print("Hybrid jobs:", len(hybrid))
    found = dm.internships.list_all(limit=5, partial=True, job_title="data")  # substring
    print("First 5 with 'data' in the title:", [i.get_job_title() for i in found])

    # create / update / delete
    # new_id = dm.internships.create({"company_name": "...", ... all 11 columns except job_id})
    # dm.internships.update(new_id, {"monthly_allowance": 1200})   # True if updated
    # dm.internships.delete(new_id)                                # True if deleted

    # ---------- users -> StudentProfile objects ----------
    user = dm.users.create("joe_tan", name="Joe", age=21, student_id="S123")
    user_id = user.get_login_details().get_user_id()   # use this id everywhere below
    print("\nUser:", user.get_name(), "id", user_id)
    # dm.users.get_by_id(user_id) / dm.users.get_by_username("joe_tan")  -> StudentProfile or None

    # ---------- resumes -> StudentResume objects (one per user) ----------
    resume = StudentResume(
        Courses=["ICT (Software Engineering)"], Year_of_Study=2, Skills=["Python", "SQL"],
        Minimum_monthly_salary=1500.0, Preferred_location=["East"],
        preferred_work_arrangement=["Hybrid"],
        Past_internships=[PastInternship("School", "IT intern", "Set up laptops", 3,
                                         "11/05/2024", "14/08/2024")],
    )
    dm.resumes.save(user_id, resume)     # saving again overwrites it
    print("Resume skills:", dm.resumes.get(user_id).get_Skills())   # None if never saved

    # ---------- runs -> RunSnapshot objects (the search history) ----------
    # A run needs exactly 5 RunResult (rank 1 = best), each holding a Listing
    results = []
    for rank, job in enumerate(dm.internships.list_all(limit=5), start=1):
        flags = [Flags("Location does not meet user's preference", True)] if rank == 2 else []
        results.append(RunResult(rank, 90.0 - rank * 5, Listing(job, flags)))

    run_id = dm.runs.save(user_id, dm.resumes.get(user_id), results, ["Learn Docker.", "Build a portfolio."])

    run = dm.runs.get(run_id, user_id)    # None if not found or not this user's run
    print(f"\nRun {run.get_run_id()} at {run.get_created_at()}")
    for result in run.get_results():
        listing = result.get_listing()
        flag_names = [flag.get_flag_name() for flag in listing.get_Flags()]
        print(f"  #{result.get_rank()} {listing.get_internship().get_job_title()} "
              f"score {result.get_score()} flags {flag_names}")
    print("  Feedback:", run.get_feedback())
    print("History size:", len(dm.runs.list_for_user(user_id)))   # newest first
    # dm.runs.delete(run_id, user_id)   # True if deleted

    dm.close()


if __name__ == "__main__":
    main()
