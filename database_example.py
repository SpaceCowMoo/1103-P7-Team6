# database_example.py
# How to use the database from your own code. Copy the part you need.
#
#   python database_example.py
#
# This uses an in-memory database (":memory:"), so it never touches data/internlink.db.
# In the real app, open it with Database.open(DB_PATH, INTERNSHIP_DATA) instead.
#
# Each stored class has its own database methods, and you pass them `db`:
#   Internship      get, list_all, create, update, delete
#   StudentProfile  create, get_by_id, get_by_username, delete   (the user account)
#   StudentResume   save, load                                    (one per user)
#   RunSnapshot     create, get, list_for_user, delete            (the search history)

from database import Database
from Flags_class import Flags
from Internship_Class import Internship
from listing_Class import Listing
from Past_internship_done_class import PastInternship
from run_models import RunResult, RunSnapshot
from Student_Profile_Class import StudentProfile
from Student_Resume_Class import StudentResume


def main():
    # ---------- open (once at startup) ----------
    db = Database.open(":memory:", "data/internships.csv")
    print("Rows per table:", db.table_counts())

    # ---------- internships ----------
    job = Internship.get(db, 1)                                   # Internship or None
    print("\nJob 1:", job.get_job_title(), "at", job.get_company_name())

    hybrid = Internship.list_all(db, limit=-1, work_mode="Hybrid")          # exact match, -1 = all
    print("Hybrid jobs:", len(hybrid))
    found = Internship.list_all(db, limit=5, partial=True, job_title="data")  # substring
    print("First 5 with 'data' in the title:", [j.get_job_title() for j in found])

    # new_job = Internship.create(db, {"company_name": "...", ... the 11 columns except job_id})
    # new_job.update(db, {"monthly_allowance": 1200})   # True if updated
    # new_job.delete(db)                                # True if deleted

    # ---------- users (StudentProfile) ----------
    user = StudentProfile.create(db, "joe_tan", name="Joe", age=21, student_id="S123")
    user_id = user.get_login_details().get_user_id()     # use this id below
    print("\nUser:", user.get_name(), "id", user_id)
    # StudentProfile.get_by_id(db, user_id) / StudentProfile.get_by_username(db, "joe_tan")

    # ---------- resume (StudentResume, one per user) ----------
    resume = StudentResume(
        Courses="ICT (Software Engineering)", Year_of_Study=2, Skills=["Python", "SQL"],
        Minimum_monthly_salary=1500.0, Preferred_location=["East"],
        preferred_work_arrangement=["Hybrid"],
        Past_internships=[PastInternship("School", "IT intern", "Set up laptops", 3,
                                         "11/05/2024", "14/08/2024")],
    )
    resume.save(db, user_id)                                     # saving again overwrites it
    print("Resume skills:", StudentResume.load(db, user_id).get_Skills())   # None if never saved

    # ---------- runs (RunSnapshot, the search history) ----------
    # A run needs exactly 5 RunResult (rank 1 = best), each holding a Listing
    results = []
    for rank, job in enumerate(Internship.list_all(db, limit=5), start=1):
        flags = [Flags("Location does not meet user's preference", True)] if rank == 2 else []
        results.append(RunResult(rank, 90.0 - rank * 5, Listing(job, flags)))

    run = RunSnapshot.create(db, user_id, StudentResume.load(db, user_id), results,
                             ["Learn Docker.", "Build a portfolio."])

    print(f"\nRun {run.get_run_id()} at {run.get_created_at()}")
    for result in run.get_results():
        listing = result.get_listing()
        flag_names = [flag.get_flag_name() for flag in listing.get_Flags()]
        print(f"  #{result.get_rank()} {listing.get_internship().get_job_title()} "
              f"score {result.get_score()} flags {flag_names}")
    print("  Feedback:", run.get_feedback())
    print("History size:", len(RunSnapshot.list_for_user(db, user_id)))   # newest first
    # RunSnapshot.get(db, run_id, user_id)   # one run, or None
    # run.delete(db)                         # True if deleted

    # ---------- close (once at the end) ----------
    db.close()


if __name__ == "__main__":
    main()
