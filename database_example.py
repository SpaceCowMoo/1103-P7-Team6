# database_example.py
# How to use the database through DataManager, and a quick check that every part works.
#
#   python database_example.py                    creates data/example.db
#   python database_example.py data/other.db      or any other file
#
# It deletes and recreates the example database every run, so each run starts the same way.
# It never touches data/internlink.db (the app's database).
# After it finishes, the file is left in data/ so you can open it in a SQLite viewer.
#
# Every step prints OK or FAIL. The script exits with code 1 if any check failed.
#
# DataManager is the only class that reads or writes stored data:
#   setup        DataManager.open, close, table_counts, has_internships, load_internships_csv
#   internships  get_internship, list_internships, create_internship, update_internship, delete_internship
#   users        create_user, get_user, get_user_by_username, delete_user   (StudentProfile)
#   resumes      save_resume, load_resume                                   (one per user)
#   runs         save_run, get_run, list_runs, delete_run                   (the search history)

import os
import sys

from data_manager import DataManager
from models.flags import Flags
from models.listing import Listing
from models.past_internship import PastInternship
from models.removed_internship import RemovedInternship
from models.run_result import RunResult
from models.student_resume import StudentResume

EXAMPLE_DB = sys.argv[1] if len(sys.argv) > 1 else os.path.join("data", "example.db")
CSV_PATH = os.path.join("data", "internships.csv")

failures = 0


def check(label, passed, detail=""):
    """Print one result line and count failures"""
    global failures
    if not passed:
        failures += 1
    mark = "OK  " if passed else "FAIL"
    print(f"  {mark} {label}" + (f"  ({detail})" if detail else ""))


def heading(title):
    print(f"\n---------- {title} ----------")


def main():
    if os.path.abspath(EXAMPLE_DB) == os.path.abspath(os.path.join("data", "internlink.db")):
        sys.exit("Refusing to use data/internlink.db: that is the app's database. Pick another file.")

    # ---------- setup: open (once at startup) ----------
    heading("Setup")
    if os.path.exists(EXAMPLE_DB):
        os.remove(EXAMPLE_DB)                                    # start fresh every run
    data = DataManager.open(EXAMPLE_DB, CSV_PATH)               # creates the file, tables, loads CSV
    counts = data.table_counts()
    check(f"created {EXAMPLE_DB}", os.path.exists(EXAMPLE_DB))
    check("tables exist", set(counts) == {"internships", "users", "resumes", "runs"}, str(counts))
    check("internships loaded from CSV", data.has_internships(), f"{counts['internships']} rows")

    # Opening again does NOT load the CSV a second time (so CRUD changes are kept)
    data.close()
    data = DataManager.open(EXAMPLE_DB, CSV_PATH)
    check("re-open keeps the same rows", data.table_counts()["internships"] == counts["internships"])

    try:
        run_examples(data)
    finally:
        # ---------- close (once at the end) ----------
        data.close()

    heading("Result")
    print(f"  final row counts: {final_counts(EXAMPLE_DB)}")
    if failures:
        print(f"  {failures} check(s) failed")
        sys.exit(1)
    print("  all checks passed")


def run_examples(data):
    # ---------- internships ----------
    heading("Internships")
    job = data.get_internship(1)                                 # Internship, or None
    check("get_internship(1)", job is not None,
          f"{job.get_job_title()} at {job.get_company_name()}" if job else "")
    check("get_internship(missing id) is None", data.get_internship(999999) is None)

    first_10 = data.list_internships(limit=10)                   # default limit is 50
    check("list_internships(limit=10)", len(first_10) == 10)

    hybrid = data.list_internships(limit=-1, work_mode="Hybrid")  # exact match, -1 = no limit
    check("exact filter work_mode='Hybrid'",
          len(hybrid) > 0 and all(j.get_work_mode() == "Hybrid" for j in hybrid), f"{len(hybrid)} jobs")

    found = data.list_internships(limit=5, partial=True, job_title="data")  # substring, any case
    check("partial filter job_title contains 'data'",
          len(found) > 0 and all("data" in j.get_job_title().lower() for j in found),
          ", ".join(j.get_job_title() for j in found[:3]))

    both = data.list_internships(limit=-1, partial=True, job_title="intern", work_mode="Hybrid")
    check("two filters at once", all(j.get_work_mode() == "Hybrid" for j in both), f"{len(both)} jobs")

    try:
        data.list_internships(salary=1000)                     # not a column
        check("unknown column is rejected", False)
    except ValueError:
        check("unknown column is rejected", True)

    new_job = data.create_internship({                            # job_id is made by SQLite
        "company_name": "Example Co", "company_type": "Start-ups", "industry": "Technology",
        "job_title": "Example Intern", "relevant_course": "Computing Science",
        "monthly_allowance": 1000, "work_mode": "Hybrid", "duration_months": 6,
        "required_skills": "Python, SQL", "location_district": "Tampines",
        "job_description": "Created by database_example.py",
    })
    new_id = new_job.get_job_id()
    check("create_internship", data.get_internship(new_id) is not None, f"job_id {new_id}")

    updated = data.update_internship(new_id, {"monthly_allowance": 1200})   # Internship, or None
    check("update_internship", updated is not None and updated.get_monthly_allowance() == 1200,
          "allowance 1000 -> 1200")
    check("update_internship(missing id) is None",
          data.update_internship(999999, {"monthly_allowance": 1}) is None)

    check("delete_internship", data.delete_internship(new_id) and data.get_internship(new_id) is None)
    check("delete_internship(missing id) is False", data.delete_internship(new_id) is False)

    # ---------- users (StudentProfile) ----------
    heading("Users")
    user = data.create_user("joe_tan", name="Joe", age=21, student_id="S123")
    user_id = user.get_login_details().get_user_id()            # use this id for everything below
    check("create_user", user.get_name() == "Joe", f"user_id {user_id}")
    check("get_user", data.get_user(user_id).get_login_details().get_username() == "joe_tan")
    check("get_user_by_username ignores case", data.get_user_by_username("JOE_TAN") is not None)
    check("get_user(missing id) is None", data.get_user(999999) is None)

    try:
        data.create_user("joe_tan")                               # usernames are unique
        check("duplicate username is rejected", False)
    except ValueError:
        check("duplicate username is rejected", True)

    # ---------- resume (StudentResume, one per user) ----------
    heading("Resume")
    check("load_resume before saving is None", data.load_resume(user_id) is None)

    resume = StudentResume(
        Courses="Information and Communications Technology (Software Engineering)",
        Year_of_Study=2, Duration_of_internship=6,
        available_internship_date="01/03/2027 - 31/08/2027",
        Skills=["Python", "SQL"], Preferred_role=["Data Analyst"],
        Minimum_monthly_salary=1500.0, Preferred_location=["East", "Central"],
        preferred_work_arrangement=["Hybrid"], industry_interest=["Fintech"],
        company_preference=["Start-ups"],
        Past_internships=[PastInternship("NYP", "IT intern", "Set up laptops", 3,
                                         "11/05/2024", "14/08/2024")],
    )
    data.save_resume(user_id, resume)
    loaded = data.load_resume(user_id)
    check("save_resume + load_resume keep every field",
          loaded.fetch_Student_Resume_details() == resume.fetch_Student_Resume_details())
    check("past internship survives",
          loaded.get_Past_internships()[0].get_company_name() == "NYP")

    resume.update_Student_Resume(Skills=["Python", "SQL", "Excel"])
    data.save_resume(user_id, resume)                            # saving again overwrites it
    check("save_resume again overwrites", data.load_resume(user_id).get_Skills() == ["Python", "SQL", "Excel"])
    check("only one resume row per user", data.table_counts()["resumes"] == 1)
    check("get_user comes with the resume",
          data.get_user(user_id).get_Student_Resume()[0].get_Skills() == ["Python", "SQL", "Excel"])

    # ---------- runs (RunSnapshot, the search history) ----------
    heading("Runs")
    # A run needs exactly 5 RunResult (rank 1 = best), each holding a Listing (Internship + Flags)
    results = []
    for rank, job in enumerate(data.list_internships(limit=5), start=1):
        flags = [Flags("Location does not meet user's preference", True)] if rank == 2 else []
        results.append(RunResult(rank, 90.0 - rank * 5, Listing(job, flags)))
    feedback = ["Learn Docker.", "Build a portfolio.", "Practise SQL joins."]

    run = data.save_run(user_id, data.load_resume(user_id), results, feedback)
    run_id = run.get_run_id()
    check("save_run", run_id is not None, f"run_id {run_id}, saved {run.get_created_at()}")
    check("results come back best first", [r.get_rank() for r in run.get_results()] == [1, 2, 3, 4, 5])
    check("scores kept", [r.get_score() for r in run.get_results()] == [85.0, 80.0, 75.0, 70.0, 65.0])
    check("flags kept",
          run.get_results()[1].get_listing().get_Flags()[0].get_flag_name()
          == "Location does not meet user's preference")
    check("feedback kept", run.get_feedback() == feedback)
    check("resume copy kept with the run", run.get_resume().get_Skills() == ["Python", "SQL", "Excel"])

    try:
        data.save_run(user_id, resume, results[:3], feedback)    # must be exactly 5
        check("run with 3 results is rejected", False)
    except ValueError:
        check("run with 3 results is rejected", True)

    for result in run.get_results():
        listing = result.get_listing()
        flag_names = [flag.get_flag_name() for flag in listing.get_Flags()]
        print(f"      #{result.get_rank()} {listing.get_internship().get_job_title()} "
              f"score {result.get_score()} flags {flag_names}")

    second = data.save_run(user_id, resume, results, ["Second run."])
    runs = data.list_runs(user_id)                               # newest first
    check("list_runs newest first", [r.get_run_id() for r in runs] == [second.get_run_id(), run_id])
    check("get_run", data.get_run(run_id, user_id).get_feedback() == feedback)

    # Another user can never read or delete this user's runs
    other_id = data.create_user("amy").get_login_details().get_user_id()
    check("other user can't get_run", data.get_run(run_id, other_id) is None)
    check("other user can't delete_run", data.delete_run(run_id, other_id) is False)
    check("other user has no runs", data.list_runs(other_id) == [])

    # Editing the resume later does not change old runs
    resume.update_Student_Resume(Skills=["Java"])
    data.save_resume(user_id, resume)
    check("old run keeps the old resume copy",
          data.get_run(run_id, user_id).get_resume().get_Skills() == ["Python", "SQL", "Excel"])

    # A job deleted after the run was saved comes back as RemovedInternship
    removed_job = data.create_internship({**data.get_internship(1).fetch_internship_details(),
                                          "job_title": "Job that gets deleted"})
    removed_results = [RunResult(1, 50.0, Listing(removed_job))] + results[1:]
    removed_run = data.save_run(user_id, resume, removed_results, ["Tip."])
    data.delete_internship(removed_job.get_job_id())
    top = data.get_run(removed_run.get_run_id(), user_id).get_results()[0].get_listing().get_internship()
    check("deleted job shows as RemovedInternship",
          isinstance(top, RemovedInternship) and top.get_job_title() == "Internship removed")

    check("delete_run", data.delete_run(second.get_run_id(), user_id)
          and data.get_run(second.get_run_id(), user_id) is None)

    # ---------- deleting a user ----------
    heading("Delete user")
    data.save_resume(other_id, StudentResume(Skills=["Excel"]))
    data.save_run(other_id, StudentResume(Skills=["Excel"]), results, ["Tip."])
    check("delete_user", data.delete_user(other_id) and data.get_user(other_id) is None)
    check("their resume and runs are deleted too",
          data.load_resume(other_id) is None and data.list_runs(other_id) == [])
    check("joe's data is untouched", data.load_resume(user_id) is not None
          and len(data.list_runs(user_id)) == 2)


def final_counts(path):
    """Open the finished file once more and return its row counts"""
    data = DataManager.open(path)
    try:
        return data.table_counts()
    finally:
        data.close()


if __name__ == "__main__":
    main()
