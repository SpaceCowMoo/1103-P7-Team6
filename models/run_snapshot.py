# RunSnapshot: one saved run of the matching tool (the search history):
# when it ran, a copy of the resume at that moment, the top 5 results and the AI feedback.
# Each result is a RunResult (models/run_result.py); a job deleted after the run was saved
# comes back as RemovedInternship (models/removed_internship.py).

import json
import sqlite3

from models.flags import Flags
from models.internship import Internship
from models.listing import Listing
from models.removed_internship import RemovedInternship
from models.run_result import RunResult
from models.student_resume import StudentResume

RESULTS_PER_RUN = 5


class RunSnapshot:
    """One saved run. The resume is a copy taken when the run happened,
    so later edits to the user's resume do not change it"""

    def __init__(
        self,
        run_id: int,
        user_id: int,
        created_at: str,
        resume: StudentResume,
        results: list[RunResult],
        feedback: list[str],
    ):
        self.__run_id = run_id
        self.__user_id = user_id
        self.__created_at = created_at
        self.__resume = resume
        self.__results = results
        self.__feedback = feedback

    def get_run_id(self):
        return self.__run_id

    def get_user_id(self):
        return self.__user_id

    def get_created_at(self):
        return self.__created_at

    def get_resume(self):
        return self.__resume

    def get_results(self):
        return self.__results

    def get_feedback(self):
        return self.__feedback

    def fetch_run_snapshot_details(self):
        return {
            "run_id": self.__run_id,
            "user_id": self.__user_id,
            "created_at": self.__created_at,
            "resume": self.__resume.fetch_Student_Resume_details(),
            "results": [result.fetch_run_result_details() for result in self.__results],
            "feedback": self.__feedback,
        }

    # ---------- database: read and write the runs table (the search history) ----------
    # db is the Database object from Database.open()
    # get/list need the user_id, so one user can never read another user's runs

    @classmethod
    def create(cls, db, user_id, resume, results, feedback):
        """Save one run with a copy of the resume. Returns the saved RunSnapshot

        results   exactly 5 RunResult, saved best rank first
        feedback  the AI feedback points, e.g. ["Learn SQL.", "Add a portfolio."]
        """
        if len(results) != RESULTS_PER_RUN:
            raise ValueError(f"A run needs exactly {RESULTS_PER_RUN} results, got {len(results)}")
        row = {
            "user_id": user_id,
            "resume_json": resume.to_json(),
            "feedback_json": json.dumps(list(feedback)),
        }
        for position, result in enumerate(sorted(results, key=RunResult.get_rank), start=1):
            listing = result.get_listing()
            row[f"job_id_{position}"] = listing.get_internship().get_job_id()
            row[f"score_{position}"] = result.get_score()
            row[f"flags_{position}"] = json.dumps(
                [flag.get_flag_name() for flag in listing.get_Flags() if flag.get_flag_value()]
            )
        try:
            with db.transaction():
                run_id = db.insert("runs", row)
        except sqlite3.IntegrityError as error:
            raise ValueError(f"No user with user_id {user_id}") from error
        return cls.get(db, run_id, user_id)

    @classmethod
    def get(cls, db, run_id, user_id):
        """One of this user's runs, or None"""
        row = db.fetch_one("SELECT * FROM runs WHERE run_id = ? AND user_id = ?", (run_id, user_id))
        return cls._from_row(db, row) if row else None

    @classmethod
    def list_for_user(cls, db, user_id):
        """All of this user's runs, newest first"""
        rows = db.fetch_all("SELECT * FROM runs WHERE user_id = ? ORDER BY run_id DESC", (user_id,))
        return [cls._from_row(db, row) for row in rows]

    def delete(self, db):
        """Delete this run. Returns True if it existed"""
        with db.transaction():
            cursor = db.execute("DELETE FROM runs WHERE run_id = ? AND user_id = ?",
                                (self.__run_id, self.__user_id))
        return cursor.rowcount > 0

    @classmethod
    def _from_row(cls, db, row):
        """One runs row -> RunSnapshot. Each job is read again from internships,
        or shown as RemovedInternship if it has been deleted since"""
        results = []
        for position in range(1, RESULTS_PER_RUN + 1):
            job_id = row[f"job_id_{position}"]
            job = Internship.get(db, job_id) or RemovedInternship(job_id)
            flags = [Flags(name, True) for name in json.loads(row[f"flags_{position}"])]
            results.append(RunResult(position, row[f"score_{position}"], Listing(job, flags)))
        return cls(
            run_id=row["run_id"],
            user_id=row["user_id"],
            created_at=row["created_at"],
            resume=StudentResume.from_json(row["resume_json"]),
            results=results,
            feedback=json.loads(row["feedback_json"]),
        )
