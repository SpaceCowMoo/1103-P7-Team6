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
#
# The OLD functions at the bottom of this file (get_conn, save_match, get_match, ...) are kept
# only until logic_manager and io_manager switch to DataManager. Then delete that section.

from __future__ import annotations

import csv
import json
import os
import sqlite3
import sys
from typing import TYPE_CHECKING

from models.flags import Flags
from models.internship import Internship
from models.listing import Listing
from models.past_internship import PastInternship
from models.removed_internship import RemovedInternship
from models.run_result import RunResult
from models.run_snapshot import RESULTS_PER_RUN, RunSnapshot
from models.student_login_details import StudentLoginDetails
from storage.database import TABLES, Database

# Import these models locally in row conversion methods to keep model dependencies lazy.
if TYPE_CHECKING:
    from models.student_profile import StudentProfile
    from models.student_resume import StudentResume

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
        return {table: self.__db.count(table) for table in TABLES}

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
                    user_role="student") -> StudentProfile:
        """Save a new user and return it. Raises ValueError if the username is blank or taken"""
        username = username.strip()
        if not username:
            raise ValueError("Username cannot be blank")
        try:
            with self.__db.transaction():
                user_id = self.__db.insert("users", {
                    "username": username,
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
        from models.student_profile import StudentProfile

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
        from models.student_resume import StudentResume

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


# =====================================================================================
# OLD FUNCTIONS: kept only until logic_manager.py and io_manager.py switch to DataManager.
# They use a plain sqlite3 connection (`conn`) and two old tables, student_profiles and matches.
# Every function takes `conn` as its first argument; app.setup_database() opens it.
# When nothing calls them any more, delete everything from here down to `if __name__`.
# =====================================================================================

# If you change the tables, delete the .db file so they get created again.
SCHEMA_SQL = """
    CREATE TABLE IF NOT EXISTS internships (
        job_id             INTEGER PRIMARY KEY,
        company_name       TEXT NOT NULL,
        company_type       TEXT NOT NULL,
        industry           TEXT NOT NULL,
        job_title          TEXT NOT NULL,
        relevant_course    TEXT NOT NULL,
        monthly_allowance  INTEGER NOT NULL,
        work_mode          TEXT NOT NULL,
        duration_months    INTEGER NOT NULL,
        required_skills    TEXT NOT NULL,
        location_district  TEXT NOT NULL,
        job_description    TEXT NOT NULL
    );

    -- One row per saved match: JSON copy of the student profile at that moment.
    CREATE TABLE IF NOT EXISTS student_profiles (
        profile_id    INTEGER PRIMARY KEY AUTOINCREMENT,
        created_at    TEXT DEFAULT (datetime('now')),
        profile_json  TEXT NOT NULL
    );

    -- One row per saved match: the top 5 job ids (best first), their scores and flags.
    -- job_id_N has no foreign key, so a match stays readable after an internship is deleted.
    -- flags_N is a JSON list of text, e.g. '["Salary below expected minimum by >$200"]'
    -- overall_feedback is JSON too, e.g. '{"points": ["...", "..."]}' (the AI format)
    CREATE TABLE IF NOT EXISTS matches (
        match_id          INTEGER PRIMARY KEY AUTOINCREMENT,
        profile_id        INTEGER NOT NULL REFERENCES student_profiles(profile_id),
        job_id_1          INTEGER NOT NULL,
        job_id_2          INTEGER NOT NULL,
        job_id_3          INTEGER NOT NULL,
        job_id_4          INTEGER NOT NULL,
        job_id_5          INTEGER NOT NULL,
        score_1           REAL NOT NULL,
        score_2           REAL NOT NULL,
        score_3           REAL NOT NULL,
        score_4           REAL NOT NULL,
        score_5           REAL NOT NULL,
        flags_1           TEXT NOT NULL,
        flags_2           TEXT NOT NULL,
        flags_3           TEXT NOT NULL,
        flags_4           TEXT NOT NULL,
        flags_5           TEXT NOT NULL,
        overall_feedback  TEXT,
        created_at        TEXT DEFAULT (datetime('now'))
    );
"""

def get_conn(db_path):
    """Open the database. Rows come back like dicts: row["job_title"]"""
    conn = sqlite3.connect(db_path)
    conn.row_factory = sqlite3.Row
    conn.execute("PRAGMA foreign_keys = ON")  # SQLite has this off by default
    return conn

def init_db(conn):
    """Create the 3 tables if they don't exist yet. Safe to call every startup"""
    conn.executescript(SCHEMA_SQL)

def is_empty(conn, table):
    """True if the table has no rows (e.g. the CSV has not been loaded yet)"""
    return conn.execute(f"SELECT COUNT(*) FROM {table}").fetchone()[0] == 0

# ---------- small helpers (used only inside this file) ----------

def _insert(conn, table, data, replace=False):
    """Insert one dict as one row. {"a": 1, "b": 2} -> INSERT INTO table (a, b) VALUES (1, 2)"""
    columns = ", ".join(data)
    marks = ", ".join(f":{k}" for k in data)
    verb = "INSERT OR REPLACE" if replace else "INSERT"
    return conn.execute(f"{verb} INTO {table} ({columns}) VALUES ({marks})", data)

# Validate data within internships.csv
def _validate_internship_row(row, line_number):
    # If 1st row fields mismatch with data of 2nd row and beyond
    if None in row:
        raise ValueError(f"Line {line_number}: too many fields")
    missing = [column for column in INTERNSHIP_COLUMNS if row.get(column) is None]
    # If field is missing
    if missing:
        raise ValueError(f"Line {line_number}: missing fields: {', '.join(missing)}")

    text_fields = set(INTERNSHIP_COLUMNS) - {
        "job_id", "monthly_allowance", "duration_months"
    }
    # Check Text values
    for field in text_fields:
        if not row[field].strip():
            raise ValueError(f"Line {line_number}: {field} is blank")
    # Check values not text
    try:
        row["job_id"] = int(row["job_id"])
        row["monthly_allowance"] = int(row["monthly_allowance"])
        row["duration_months"] = int(row["duration_months"])
    except ValueError as error:
        raise ValueError(f"Line {line_number}: invalid numeric value") from error
    if row["job_id"] <= 0 or row["monthly_allowance"] < 0 or row["duration_months"] <= 0:
        raise ValueError(f"Line {line_number}: numeric value is out of range")

    return row

def _editable_fields(data):
    """Keep only internship columns the user may set (job_id is made by SQLite)"""
    return {k: v for k, v in data.items() if k in INTERNSHIP_COLUMNS and k != "job_id"}

def _match_to_dict(row):
    """One matches row -> dict, with flags_N and overall_feedback turned back from JSON into Python"""
    match = dict(row)
    for i in range(1, 6):
        match[f"flags_{i}"] = json.loads(match[f"flags_{i}"])
    match["overall_feedback"] = json.loads(match["overall_feedback"])
    return match

# ---------- loading the internships CSV ----------

def load_internships_csv(conn, path):
    """Load the internships CSV. Returns how many rows were loaded"""
    if not os.path.exists(path):
        raise FileNotFoundError(f"CSV not found: {path}")
    with open(path, newline="", encoding="utf-8-sig") as f:
        rows = list(csv.DictReader(f))
    with conn:
        for line_number, internship_row in enumerate(rows, start=2):
            row_validated = _validate_internship_row(internship_row, line_number)
            internship_row = {key: value for key, value in row_validated.items() if key in INTERNSHIP_COLUMNS}
            _insert(conn, "internships", internship_row, replace=True)
            
    return len(rows)

# ---------- internships ----------

def create_internship(conn, data):
    """Insert a new internship. Returns the new job_id"""
    with conn:
        return _insert(conn, "internships", _editable_fields(data)).lastrowid

def get_internship(conn, job_id):
    """One internship as a dict, or None if the job_id doesn't exist"""
    row = conn.execute("SELECT * FROM internships WHERE job_id = ?", (job_id,)).fetchone()
    return dict(row) if row else None


def list_internships(conn, limit=50, partial=False, **filters):
    """List internships with exact filters, or substring matching for text when partial=True."""
    query = "SELECT * FROM internships WHERE 1=1"
    values = []
    for column, value in filters.items():
        if value is None:
            continue
        if column not in INTERNSHIP_COLUMNS:
            raise ValueError(f"Unknown column: {column}")
        if partial and column not in {"job_id", "monthly_allowance", "duration_months"}:
            query += f" AND {column} LIKE ? COLLATE NOCASE"
            values.append(f"%{value}%")
        else:
            query += f" AND {column} = ?"
            values.append(value)
    query += " ORDER BY job_id ASC LIMIT ?"
    values.append(limit)
    return [dict(r) for r in conn.execute(query, values).fetchall()]

def update_internship(conn, job_id, changes):
    """Update only the given fields. Returns True if a row was updated"""
    changes = _editable_fields(changes)
    if not changes:
        return False
    set_clause = ", ".join(f"{k} = ?" for k in changes)
    with conn:
        cur = conn.execute(
            f"UPDATE internships SET {set_clause} WHERE job_id = ?",
            list(changes.values()) + [job_id],
        )
    return cur.rowcount > 0

def delete_internship(conn, job_id):
    """Delete one internship. Returns True if it existed"""
    with conn:
        cur = conn.execute("DELETE FROM internships WHERE job_id = ?", (job_id,))
    return cur.rowcount > 0

# ---------- matches ----------

def save_match(conn, profile, job_ids, scores, flags, overall_feedback):
    """Save one profile snapshot and one match row. Returns the new match_id

    profile           {"student_profile": {...}} as io_manager loads it
    job_ids           5 job ids, best first            e.g. [12, 4, 30, 7, 2]
    scores            5 scores, same order              e.g. [82.3, 70.0, 51.2, 35.0, 20.0]
    flags             5 lists of flag text, same order  e.g. [["Location does not ..."], [], ...]
    overall_feedback  the AI feedback as given, e.g. {"points": ["...", "..."]}
    """
    if len(job_ids) != 5 or len(scores) != 5 or len(flags) != 5:
        raise ValueError("save_match needs exactly 5 job ids, 5 scores and 5 flag lists")
    with conn:  # all or nothing: if the match insert fails, the profile insert is undone
        profile_id = _insert(conn, "student_profiles",
                             {"profile_json": json.dumps(profile)}).lastrowid
        row = {"profile_id": profile_id, "overall_feedback": json.dumps(overall_feedback)}
        for i in range(5):
            row[f"job_id_{i + 1}"] = job_ids[i]
            row[f"score_{i + 1}"] = scores[i]
            row[f"flags_{i + 1}"] = json.dumps(flags[i])
        return _insert(conn, "matches", row).lastrowid

def get_match(conn, match_id):
    """One match with its profile snapshot and a list of 5 jobs (best first). None if not found

    {"match_id": 1, "created_at": "2026-10-12 12:26:37",
     "overall_feedback": {"points": [...]}, "profile": {"student_profile": {...}},
     "jobs": [{"job_id": 12, "score": 82.3, "flags": ["..."]}, ... 5 items]}
    """
    row = conn.execute("""
        SELECT m.*, p.profile_json
        FROM matches m JOIN student_profiles p ON p.profile_id = m.profile_id
        WHERE m.match_id = ?""", (match_id,)).fetchone()
    if row is None:
        return None
    match = _match_to_dict(row)
    jobs = []
    for i in range(1, 6):
        jobs.append({"job_id": match[f"job_id_{i}"], "score": match[f"score_{i}"],
                     "flags": match[f"flags_{i}"]})
    return {
        "match_id": match["match_id"],
        "created_at": match["created_at"],
        "overall_feedback": match["overall_feedback"],
        "profile": json.loads(row["profile_json"]),
        "jobs": jobs,
    }

def list_matches(conn):
    """Every match as a flat dict (job_id_1, score_1, flags_1, ...), newest first"""
    rows = conn.execute("SELECT * FROM matches ORDER BY match_id DESC")
    return [_match_to_dict(r) for r in rows]

def delete_match(conn, match_id):
    """Delete a match and its profile snapshot. Returns True if it existed"""
    row = conn.execute("SELECT profile_id FROM matches WHERE match_id = ?",
                       (match_id,)).fetchone()
    if row is None:
        return False
    with conn:  # delete the match first, because it points at the profile
        conn.execute("DELETE FROM matches WHERE match_id = ?", (match_id,))
        conn.execute("DELETE FROM student_profiles WHERE profile_id = ?",
                     (row["profile_id"],))
    return True


if __name__ == "__main__":
    main()
