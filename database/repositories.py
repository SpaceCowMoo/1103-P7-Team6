# database/repositories.py
# One repository class per table. Each one turns rows into the team's objects
# and objects back into rows, so the rest of the app never writes SQL.
#
#   InternshipRepository  internships  -> Internship
#   UserRepository        users        -> StudentProfile (with StudentLoginDetails)
#   ResumeRepository      resumes      -> StudentResume
#   RunRepository         runs         -> RunSnapshot
#
# Shared rules (every repository keeps these):
#   get...()  returns one object, or None if it doesn't exist
#   delete()  returns True if a row was deleted, False if it didn't exist

import json
import sqlite3
from abc import ABC, abstractmethod

from Flags_class import Flags
from Internship_Class import Internship
from listing_Class import Listing
from run_models import RemovedInternship, RunResult, RunSnapshot
from Student_Login_detail import StudentLoginDetails
from Student_Profile_Class import StudentProfile
from Student_Resume_Class import StudentResume

from .connection import Database
from .serializers import ResumeSerializer

INTERNSHIP_COLUMNS = [
    "job_id", "company_name", "company_type", "industry", "job_title", "relevant_course",
    "monthly_allowance", "work_mode", "duration_months", "required_skills",
    "location_district", "job_description",
]
INTERNSHIP_NUMBER_COLUMNS = {"job_id", "monthly_allowance", "duration_months"}

RESULTS_PER_RUN = 5


class BaseRepository(ABC):
    """Shared helpers. Subclasses only add their own queries and _row_to_object"""

    def __init__(self, db: Database):
        self._db = db

    def _insert(self, table: str, data: dict, replace: bool = False) -> int:
        """Insert one dict as one row. Returns the new row id.
        Table and column names come from this file only, never from user input"""
        columns = ", ".join(data)
        marks = ", ".join("?" for _ in data)
        verb = "INSERT OR REPLACE" if replace else "INSERT"
        sql = f"{verb} INTO {table} ({columns}) VALUES ({marks})"
        return self._db.execute(sql, list(data.values())).lastrowid

    def _fetch_one(self, sql: str, params=()):
        return self._db.execute(sql, params).fetchone()

    def _fetch_all(self, sql: str, params=()):
        return self._db.execute(sql, params).fetchall()

    def _delete(self, sql: str, params=()) -> bool:
        with self._db.transaction():
            return self._db.execute(sql, params).rowcount > 0

    @abstractmethod
    def _row_to_object(self, row):
        """Turn one database row into one domain object"""


class InternshipRepository(BaseRepository):

    def create(self, fields: dict) -> int:
        """Insert a new internship. job_id is made by SQLite. Returns the new job_id"""
        with self._db.transaction():
            return self._insert("internships", self.__editable_fields(fields))

    def import_rows(self, rows: list[dict]):
        """Insert or replace many internships (with their job_id) in one transaction.
        Used by InternshipCsvLoader. Rows must already be validated"""
        with self._db.transaction():
            for row in rows:
                self._insert("internships", {k: row[k] for k in INTERNSHIP_COLUMNS}, replace=True)

    def get(self, job_id: int) -> Internship | None:
        row = self._fetch_one("SELECT * FROM internships WHERE job_id = ?", (job_id,))
        return self._row_to_object(row) if row else None

    def list_all(self, limit: int = 50, partial: bool = False, **filters) -> list[Internship]:
        """Internships matching the filters, by job_id. limit=-1 means no limit.
        partial=True matches text columns by substring, ignoring case"""
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
        return [self._row_to_object(row) for row in self._fetch_all(query, values)]

    def update(self, job_id: int, changes: dict) -> bool:
        """Update only the given fields. Returns True if a row was updated"""
        changes = self.__editable_fields(changes)
        if not changes:
            return False
        set_clause = ", ".join(f"{column} = ?" for column in changes)
        with self._db.transaction():
            cursor = self._db.execute(
                f"UPDATE internships SET {set_clause} WHERE job_id = ?",
                list(changes.values()) + [job_id],
            )
        return cursor.rowcount > 0

    def delete(self, job_id: int) -> bool:
        return self._delete("DELETE FROM internships WHERE job_id = ?", (job_id,))

    def _row_to_object(self, row) -> Internship:
        return Internship(**dict(row))

    @staticmethod
    def __editable_fields(data: dict) -> dict:
        """Keep only internship columns the user may set (job_id is made by SQLite)"""
        return {k: v for k, v in data.items() if k in INTERNSHIP_COLUMNS and k != "job_id"}


class UserRepository(BaseRepository):
    """User accounts. No login yet, so StudentLoginDetails.password is None"""

    def create(self, username: str, name: str | None = None, age: int | None = None,
               student_id: str | None = None, user_role: str = "student") -> StudentProfile:
        """Add a new user. Raises ValueError if the username is taken"""
        try:
            with self._db.transaction():
                user_id = self._insert("users", {
                    "username": username.strip(),
                    "user_role": user_role,
                    "name": name,
                    "age": age,
                    "student_id": student_id,
                })
        except sqlite3.IntegrityError as error:
            raise ValueError(f"Username already taken: {username}") from error
        return self.get_by_id(user_id)

    def get_by_id(self, user_id: int) -> StudentProfile | None:
        row = self._fetch_one("SELECT * FROM users WHERE user_id = ?", (user_id,))
        return self._row_to_object(row) if row else None

    def get_by_username(self, username: str) -> StudentProfile | None:
        """Case-insensitive, because the column is COLLATE NOCASE"""
        row = self._fetch_one("SELECT * FROM users WHERE username = ?", (username,))
        return self._row_to_object(row) if row else None

    def delete(self, user_id: int) -> bool:
        """Also deletes the user's resume and runs (ON DELETE CASCADE)"""
        return self._delete("DELETE FROM users WHERE user_id = ?", (user_id,))

    def _row_to_object(self, row) -> StudentProfile:
        login = StudentLoginDetails(
            user_id=row["user_id"],
            user_role=row["user_role"],
            username=row["username"],
            password=row["password_hash"],
        )
        return StudentProfile(
            name=row["name"],
            age=row["age"],
            student_id=row["student_id"],
            login_details=login,
        )


class ResumeRepository(BaseRepository):
    """Each user's one current resume"""

    def get(self, user_id: int) -> StudentResume | None:
        row = self._fetch_one("SELECT * FROM resumes WHERE user_id = ?", (user_id,))
        return self._row_to_object(row) if row else None

    def save(self, user_id: int, resume: StudentResume):
        """Insert the resume, or overwrite it if the user already has one"""
        try:
            with self._db.transaction():
                self._db.execute(
                    """INSERT INTO resumes (user_id, resume_json) VALUES (?, ?)
                       ON CONFLICT(user_id) DO UPDATE SET
                           resume_json = excluded.resume_json,
                           updated_at = datetime('now')""",
                    (user_id, ResumeSerializer.to_json(resume)),
                )
        except sqlite3.IntegrityError as error:
            raise ValueError(f"No user with user_id {user_id}") from error

    def delete(self, user_id: int) -> bool:
        return self._delete("DELETE FROM resumes WHERE user_id = ?", (user_id,))

    def _row_to_object(self, row) -> StudentResume:
        return ResumeSerializer.from_json(row["resume_json"])


class RunRepository(BaseRepository):
    """Saved runs (search history). Every method needs the user_id,
    so one user can never read or delete another user's runs"""

    def __init__(self, db: Database, internships: InternshipRepository):
        super().__init__(db)
        self.__internships = internships

    def save(self, user_id: int, resume: StudentResume,
             results: list[RunResult], feedback: list[str]) -> int:
        """Save one run with a copy of the resume. Returns the new run_id

        results   exactly 5 RunResult, saved best rank first
        feedback  the AI feedback points, e.g. ["Learn SQL.", "Add a portfolio."]
        """
        if len(results) != RESULTS_PER_RUN:
            raise ValueError(f"A run needs exactly {RESULTS_PER_RUN} results, got {len(results)}")
        row = {
            "user_id": user_id,
            "resume_json": ResumeSerializer.to_json(resume),
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
            with self._db.transaction():
                return self._insert("runs", row)
        except sqlite3.IntegrityError as error:
            raise ValueError(f"No user with user_id {user_id}") from error

    def get(self, run_id: int, user_id: int) -> RunSnapshot | None:
        row = self._fetch_one("SELECT * FROM runs WHERE run_id = ? AND user_id = ?",
                              (run_id, user_id))
        return self._row_to_object(row) if row else None

    def list_for_user(self, user_id: int) -> list[RunSnapshot]:
        """The user's runs, newest first"""
        rows = self._fetch_all("SELECT * FROM runs WHERE user_id = ? ORDER BY run_id DESC",
                               (user_id,))
        return [self._row_to_object(row) for row in rows]

    def delete(self, run_id: int, user_id: int) -> bool:
        return self._delete("DELETE FROM runs WHERE run_id = ? AND user_id = ?",
                            (run_id, user_id))

    def _row_to_object(self, row) -> RunSnapshot:
        results = []
        for position in range(1, RESULTS_PER_RUN + 1):
            job_id = row[f"job_id_{position}"]
            internship = self.__internships.get(job_id) or RemovedInternship(job_id)
            flags = [Flags(name, True) for name in json.loads(row[f"flags_{position}"])]
            results.append(RunResult(position, row[f"score_{position}"], Listing(internship, flags)))
        return RunSnapshot(
            run_id=row["run_id"],
            user_id=row["user_id"],
            created_at=row["created_at"],
            resume=ResumeSerializer.from_json(row["resume_json"]),
            results=results,
            feedback=json.loads(row["feedback_json"]),
        )
