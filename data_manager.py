# data_manager.py
# DataManager: the one class that reads and writes stored data (one of the 4 managers).
# It turns database rows into model objects (models/) and back, so the model classes
# never run SQL. The SQLite connection, schema and transactions are in storage/database.py.
#
#   data = DataManager.open(DB_PATH, INTERNSHIP_DATA)   # once at startup
#   ...
#   data.close()                                        # once at the end
#
# Tables (see storage/database.py):
#   internships  the internship listings (loaded once from data/internships.csv)
#   users        one row per user account
#   resumes      the user's resume (one per user), stored as JSON
#   runs         one row per run of the matching tool (the search history)
#
# Show the row count of every table:
#   python data_manager.py                                 uses INTERNSHIP_DB / INTERNSHIP_DATA from .env
#   python data_manager.py data/test.db data/internships.csv

from __future__ import annotations

import csv
import json
import os
import sqlite3
import sys

from models.flags import Flags
from models.internship import Internship
from models.listing import Listing
from models.past_internship import PastInternship
from models.removed_internship import RemovedInternship
from models.run_result import RunResult
from models.run_snapshot import RESULTS_PER_RUN, RunSnapshot
from models.student_login_details import StudentLoginDetails
from models.student_profile import StudentProfile
from models.student_resume import StudentResume
from storage.database import Database

# Columns of the internships table (and internships.csv), in order
INTERNSHIP_COLUMNS = [
    "job_id", "company_name", "company_type", "industry", "job_title", "relevant_course",
    "monthly_allowance", "work_mode", "duration_months", "required_skills",
    "location_district", "job_description",
]
INTERNSHIP_NUMBER_COLUMNS = {"job_id", "monthly_allowance", "duration_months"}


class DataManager:
    """Reads and writes Internship, StudentProfile (user), StudentResume and RunSnapshot objects"""

    def __init__(self, db: Database):
        self.__db = db

    @classmethod
    def open(cls, db_path: str, csv_path: str | None = None) -> "DataManager":
        """Open the database and create missing tables. If csv_path is given and there are
        no internships yet, load them from the CSV (only the first time, so CRUD changes are kept).
        db_path=":memory:" gives a throwaway database (good for tests)"""
        db = Database.open(db_path)
        try:
            data = cls(db)
            if csv_path is not None and not data.has_internships():
                data.load_internships_csv(csv_path)
        except Exception:
            db.close()
            raise
        return data

    def close(self):
        self.__db.close()

    def table_counts(self) -> dict[str, int]:
        """Row count of every table, e.g. {"internships": 654, "users": 2, ...}"""
        return self.__db.table_counts()

    # ---------- internships ----------

    def has_internships(self) -> bool:
        return not self.__db.is_empty("internships")

    def load_internships_csv(self, path: str) -> int:
        """Load every row of internships.csv. Returns how many rows were loaded.
        Nothing is saved if any row is invalid"""
        if not os.path.exists(path):
            raise FileNotFoundError(f"CSV not found: {path}")
        with open(path, newline="", encoding="utf-8-sig") as file:
            rows = list(csv.DictReader(file))
        # Line 1 is the header, so the first data row is line 2
        validated = [self._validate_csv_row(row, line) for line, row in enumerate(rows, start=2)]
        with self.__db.transaction():
            for row in validated:
                self.__db.insert("internships", row, replace=True)
        return len(validated)

    def get_internship(self, job_id) -> Internship | None:
        """One internship, or None if the job_id doesn't exist"""
        row = self.__db.fetch_one("SELECT * FROM internships WHERE job_id = ?", (job_id,))
        return Internship(**dict(row)) if row else None

    def list_internships(self, limit=50, partial=False, **filters) -> list[Internship]:
        """Internships matching the filters, by job_id. limit=-1 means no limit.
        partial=True matches text columns by substring, ignoring case
        e.g. data.list_internships(limit=-1, work_mode="Hybrid")"""
        query = "SELECT * FROM internships WHERE 1=1"
        values = []
        for column, value in filters.items():
            if value is None:
                continue
            if column not in INTERNSHIP_COLUMNS:
                raise ValueError(f"Unknown column: {column}")
            if partial and column not in INTERNSHIP_NUMBER_COLUMNS:
                query += f" AND {column} LIKE ? COLLATE NOCASE"
                values.append(f"%{value}%")
            else:
                query += f" AND {column} = ?"
                values.append(value)
        query += " ORDER BY job_id ASC LIMIT ?"
        values.append(limit)
        return [Internship(**dict(row)) for row in self.__db.fetch_all(query, values)]

    def create_internship(self, fields: dict) -> Internship:
        """Save a new internship (job_id is made by SQLite). Returns the new Internship"""
        with self.__db.transaction():
            job_id = self.__db.insert("internships", self._editable_fields(fields))
        return self.get_internship(job_id)

    def update_internship(self, job_id, changes: dict) -> Internship | None:
        """Save changes to one internship, e.g. {"monthly_allowance": 1200}.
        Returns the updated Internship, or None if nothing was updated"""
        changes = self._editable_fields(changes)
        if not changes:
            return None
        set_clause = ", ".join(f"{column} = ?" for column in changes)
        with self.__db.transaction():
            cursor = self.__db.execute(f"UPDATE internships SET {set_clause} WHERE job_id = ?",
                                       [*changes.values(), job_id])
        return self.get_internship(job_id) if cursor.rowcount > 0 else None

    def delete_internship(self, job_id) -> bool:
        """Delete one internship. Returns True if it existed"""
        with self.__db.transaction():
            cursor = self.__db.execute("DELETE FROM internships WHERE job_id = ?", (job_id,))
        return cursor.rowcount > 0

    # ---------- users (StudentProfile + StudentLoginDetails) ----------
    # The user's id is in the login details: user.get_login_details().get_user_id()

    def create_user(self, username, name=None, age=None, student_id=None,
                    user_role="student", password_hash=None) -> StudentProfile:
        """Save a new user and return it. Raises ValueError if the username is blank or taken.
        password_hash is StudentLoginDetails.hash_password(password), never the password itself"""
        username = username.strip()
        if not username:
            raise ValueError("Username cannot be blank")
        try:
            with self.__db.transaction():
                user_id = self.__db.insert("users", {
                    "username": username,
                    "password_hash": password_hash,
                    "user_role": user_role,
                    "name": name,
                    "age": age,
                    "student_id": student_id,
                })
        except sqlite3.IntegrityError as error:
            raise ValueError(f"Username already taken: {username}") from error
        return self.get_user(user_id)

    def get_user(self, user_id) -> StudentProfile | None:
        """One user with their resume (if they saved one), or None"""
        row = self.__db.fetch_one("SELECT * FROM users WHERE user_id = ?", (user_id,))
        return self._user_from_row(row) if row else None

    def get_user_by_username(self, username) -> StudentProfile | None:
        """One user with their resume, or None. Ignores upper/lower case"""
        row = self.__db.fetch_one("SELECT * FROM users WHERE username = ?", (username.strip(),))
        return self._user_from_row(row) if row else None

    def delete_user(self, user_id) -> bool:
        """Delete a user, and their resume and runs too. Returns True if it existed"""
        with self.__db.transaction():
            cursor = self.__db.execute("DELETE FROM users WHERE user_id = ?", (user_id,))
        return cursor.rowcount > 0

    # ---------- resumes (one per user) ----------

    def save_resume(self, user_id, resume: StudentResume):
        """Save this as the user's resume. Overwrites the one they had before"""
        try:
            with self.__db.transaction():
                self.__db.execute(
                    """INSERT INTO resumes (user_id, resume_json) VALUES (?, ?)
                       ON CONFLICT(user_id) DO UPDATE SET
                           resume_json = excluded.resume_json,
                           updated_at = datetime('now')""",
                    (user_id, self._resume_to_json(resume)),
                )
        except sqlite3.IntegrityError as error:
            raise ValueError(f"No user with user_id {user_id}") from error

    def load_resume(self, user_id) -> StudentResume | None:
        """The user's resume, or None if they haven't saved one yet"""
        row = self.__db.fetch_one("SELECT resume_json FROM resumes WHERE user_id = ?", (user_id,))
        return self._resume_from_json(row["resume_json"]) if row else None

    # ---------- runs (the search history) ----------
    # get/list/delete need the user_id, so one user can never read another user's runs

    def save_run(self, user_id, resume: StudentResume, results: list[RunResult],
                 feedback: list[str]) -> RunSnapshot:
        """Save one run with a copy of the resume. Returns the saved RunSnapshot

        results   exactly 5 RunResult, saved best rank first
        feedback  the AI feedback points, e.g. ["Learn SQL.", "Add a portfolio."]
        """
        if len(results) != RESULTS_PER_RUN:
            raise ValueError(f"A run needs exactly {RESULTS_PER_RUN} results, got {len(results)}")
        row = {
            "user_id": user_id,
            "resume_json": self._resume_to_json(resume),
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
            with self.__db.transaction():
                run_id = self.__db.insert("runs", row)
        except sqlite3.IntegrityError as error:
            raise ValueError(f"No user with user_id {user_id}") from error
        return self.get_run(run_id, user_id)

    def get_run(self, run_id, user_id) -> RunSnapshot | None:
        """One of this user's runs, or None"""
        row = self.__db.fetch_one("SELECT * FROM runs WHERE run_id = ? AND user_id = ?",
                                  (run_id, user_id))
        return self._run_from_row(row) if row else None

    def list_runs(self, user_id) -> list[RunSnapshot]:
        """All of this user's runs, newest first"""
        rows = self.__db.fetch_all("SELECT * FROM runs WHERE user_id = ? ORDER BY run_id DESC",
                                   (user_id,))
        return [self._run_from_row(row) for row in rows]

    def delete_run(self, run_id, user_id) -> bool:
        """Delete one of this user's runs. Returns True if it existed"""
        with self.__db.transaction():
            cursor = self.__db.execute("DELETE FROM runs WHERE run_id = ? AND user_id = ?",
                                       (run_id, user_id))
        return cursor.rowcount > 0

    # ---------- row <-> object helpers (used only inside this class) ----------

    def _user_from_row(self, row) -> StudentProfile:
        """One users row -> StudentProfile with its StudentLoginDetails and resume"""
        login_details = StudentLoginDetails(
            user_id=row["user_id"],
            user_role=row["user_role"],
            username=row["username"],
            password=row["password_hash"],
        )
        resume = self.load_resume(row["user_id"])
        return StudentProfile(name=row["name"], age=row["age"], student_id=row["student_id"],
                              Student_Resume=[resume] if resume else [],
                              login_details=login_details)

    def _run_from_row(self, row) -> RunSnapshot:
        """One runs row -> RunSnapshot. Each job is read again from internships,
        or shown as RemovedInternship if it has been deleted since"""
        results = []
        for position in range(1, RESULTS_PER_RUN + 1):
            job_id = row[f"job_id_{position}"]
            job = self.get_internship(job_id) or RemovedInternship(job_id)
            flags = [Flags(name, True) for name in json.loads(row[f"flags_{position}"])]
            results.append(RunResult(position, row[f"score_{position}"], Listing(job, flags)))
        return RunSnapshot(
            run_id=row["run_id"],
            user_id=row["user_id"],
            created_at=row["created_at"],
            resume=self._resume_from_json(row["resume_json"]),
            results=results,
            feedback=json.loads(row["feedback_json"]),
        )

    @staticmethod
    def _resume_to_json(resume: StudentResume) -> str:
        """StudentResume -> JSON text for the resume_json column"""
        return json.dumps(resume.fetch_Student_Resume_details())

    @staticmethod
    def _resume_from_json(text: str) -> StudentResume:
        """JSON text from the resume_json column -> StudentResume with its PastInternship list.
        The keys are the ones StudentResume.fetch_Student_Resume_details() writes"""
        data = json.loads(text)
        past_internships = [PastInternship(**item) for item in data.pop("Past_internships", [])]
        return StudentResume(**data, Past_internships=past_internships)

    @staticmethod
    def _editable_fields(data: dict) -> dict:
        """Keep only internship columns the user may set (job_id is made by SQLite)"""
        return {k: v for k, v in data.items() if k in INTERNSHIP_COLUMNS and k != "job_id"}

    @staticmethod
    def _validate_csv_row(row, line_number) -> dict:
        """Check one CSV row. Returns only the internship columns, with numbers as int"""
        if None in row:  # more values than header columns
            raise ValueError(f"Line {line_number}: too many fields")
        missing = [column for column in INTERNSHIP_COLUMNS if row.get(column) is None]
        if missing:
            raise ValueError(f"Line {line_number}: missing fields: {', '.join(missing)}")

        for field in set(INTERNSHIP_COLUMNS) - INTERNSHIP_NUMBER_COLUMNS:
            if not row[field].strip():
                raise ValueError(f"Line {line_number}: {field} is blank")
        try:
            numbers = {column: int(row[column]) for column in INTERNSHIP_NUMBER_COLUMNS}
        except ValueError as error:
            raise ValueError(f"Line {line_number}: invalid numeric value") from error
        if numbers["job_id"] <= 0 or numbers["monthly_allowance"] < 0 or numbers["duration_months"] <= 0:
            raise ValueError(f"Line {line_number}: numeric value is out of range")

        cleaned = {column: row[column] for column in INTERNSHIP_COLUMNS}
        cleaned.update(numbers)
        return cleaned


def main():
    """Create (or open) the database and show how many rows each table has"""
    from dotenv import load_dotenv

    load_dotenv()
    db_path = sys.argv[1] if len(sys.argv) > 1 else os.getenv("INTERNSHIP_DB", "data/internlink.db")
    csv_path = sys.argv[2] if len(sys.argv) > 2 else os.getenv("INTERNSHIP_DATA", "data/internships.csv")

    print(f"Database: {db_path}")
    print(f"CSV:      {csv_path}")
    data = DataManager.open(db_path, csv_path)
    try:
        for table, count in data.table_counts().items():
            print(f"  {table:<12} {count} rows")
    finally:
        data.close()


if __name__ == "__main__":
    main()
