# database/connection.py
# Database: owns the SQLite connection and the table definitions.
# The classes that get stored (Internship, StudentProfile, StudentResume, RunSnapshot)
# each have their own get/create/save/delete methods and are given this object as `db`.
#
#   db = Database.open(DB_PATH, INTERNSHIP_DATA)   # once at startup
#   ...
#   db.close()                                      # once at the end
#
# No migrations: if you change SCHEMA_SQL, delete the .db file and start the app again.
# The tables are created again and internships are reloaded from the CSV.

import sqlite3
from contextlib import contextmanager

from Internship_Class import Internship

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

    -- One row per user account.
    -- password_hash is empty for now; it gets filled in when login is added.
    -- COLLATE NOCASE: "Joe" and "joe" count as the same username.
    CREATE TABLE IF NOT EXISTS users (
        user_id        INTEGER PRIMARY KEY AUTOINCREMENT,
        username       TEXT NOT NULL UNIQUE COLLATE NOCASE,
        password_hash  TEXT,
        user_role      TEXT NOT NULL DEFAULT 'student',
        name           TEXT,
        age            INTEGER,
        student_id     TEXT,
        created_at     TEXT DEFAULT (datetime('now'))
    );

    -- The user's current resume (one per user), overwritten when they edit it.
    -- resume_json is StudentResume.to_json()
    CREATE TABLE IF NOT EXISTS resumes (
        user_id      INTEGER PRIMARY KEY REFERENCES users(user_id) ON DELETE CASCADE,
        resume_json  TEXT NOT NULL,
        updated_at   TEXT DEFAULT (datetime('now'))
    );

    -- One row per run of the matching tool (the search history).
    -- resume_json is a copy of the resume at run time, so editing the resume later
    -- does not change old runs.
    -- job_id_N has no foreign key, so a run stays readable after an internship is deleted.
    -- flags_N is a JSON list of flag names, e.g. '["Salary below expected minimum by >$200"]'
    -- feedback_json is a JSON list of feedback points, e.g. '["...", "..."]'
    CREATE TABLE IF NOT EXISTS runs (
        run_id         INTEGER PRIMARY KEY AUTOINCREMENT,
        user_id        INTEGER NOT NULL REFERENCES users(user_id) ON DELETE CASCADE,
        resume_json    TEXT NOT NULL,
        job_id_1       INTEGER NOT NULL,
        job_id_2       INTEGER NOT NULL,
        job_id_3       INTEGER NOT NULL,
        job_id_4       INTEGER NOT NULL,
        job_id_5       INTEGER NOT NULL,
        score_1        REAL NOT NULL,
        score_2        REAL NOT NULL,
        score_3        REAL NOT NULL,
        score_4        REAL NOT NULL,
        score_5        REAL NOT NULL,
        flags_1        TEXT NOT NULL,
        flags_2        TEXT NOT NULL,
        flags_3        TEXT NOT NULL,
        flags_4        TEXT NOT NULL,
        flags_5        TEXT NOT NULL,
        feedback_json  TEXT NOT NULL,
        created_at     TEXT DEFAULT (datetime('now'))
    );

    CREATE INDEX IF NOT EXISTS idx_runs_user_id ON runs(user_id);
"""

# Only these names may be put into SQL text (table names can't be ? parameters)
TABLES = ("internships", "users", "resumes", "runs")


class Database:
    """One SQLite connection. Rows come back like dicts: row["job_title"]"""

    def __init__(self, db_path: str):
        self.__connection = sqlite3.connect(db_path)
        self.__connection.row_factory = sqlite3.Row
        self.__connection.execute("PRAGMA foreign_keys = ON")  # SQLite has this off by default

    @classmethod
    def open(cls, db_path: str, csv_path: str | None = None) -> "Database":
        """Open the database, create missing tables, and load the CSV if internships is empty.
        db_path=":memory:" gives a throwaway database (good for tests)"""
        db = cls(db_path)
        try:
            db.create_schema()
            if csv_path is not None and db.is_empty("internships"):
                Internship.load_csv(db, csv_path)  # only the first time, so CRUD changes are kept
        except Exception:
            db.close()
            raise
        return db

    def create_schema(self):
        """Create the tables if they don't exist yet. Safe to call every startup"""
        self.__connection.executescript(SCHEMA_SQL)

    # ---------- helpers used by the stored classes ----------

    def execute(self, sql: str, params=()):
        """Run one SQL statement with ? parameters. Returns the cursor"""
        return self.__connection.execute(sql, params)

    def fetch_one(self, sql: str, params=()):
        """The first row, or None"""
        return self.execute(sql, params).fetchone()

    def fetch_all(self, sql: str, params=()):
        """Every row, as a list"""
        return self.execute(sql, params).fetchall()

    def insert(self, table: str, data: dict, replace: bool = False) -> int:
        """Insert one dict as one row. Returns the new row id.
        {"a": 1, "b": 2} -> INSERT INTO table (a, b) VALUES (?, ?)
        The dict keys must be column names written in code, never user input.
        Call it inside `with db.transaction():` so it gets saved"""
        if table not in TABLES:
            raise ValueError(f"Unknown table: {table}")
        columns = ", ".join(data)
        marks = ", ".join("?" for _ in data)
        verb = "INSERT OR REPLACE" if replace else "INSERT"
        return self.execute(f"{verb} INTO {table} ({columns}) VALUES ({marks})",
                            list(data.values())).lastrowid

    @contextmanager
    def transaction(self):
        """All or nothing: commits at the end, or rolls back if an error is raised inside"""
        with self.__connection:
            yield

    # ---------- table info ----------

    def count(self, table: str) -> int:
        """How many rows the table has"""
        if table not in TABLES:
            raise ValueError(f"Unknown table: {table}")
        return self.fetch_one(f"SELECT COUNT(*) FROM {table}")[0]

    def is_empty(self, table: str) -> bool:
        return self.count(table) == 0

    def table_counts(self) -> dict[str, int]:
        """Row count of every table, e.g. {"internships": 654, "users": 2, ...}"""
        return {table: self.count(table) for table in TABLES}

    def close(self):
        self.__connection.close()
