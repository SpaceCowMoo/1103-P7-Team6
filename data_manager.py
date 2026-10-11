import csv
import json
import sqlite3
import os

# ---------- database setup ----------

INTERNSHIP_COLUMNS = [
    "job_id", "company_name", "industry", "job_title", "relevant_course",
    "monthly_allowance", "work_mode", "duration_months", "required_skills",
    "location_district", "job_description",
]

# top-level key in the student profile JSON; it is stripped before saving
PROFILE_WRAPPER_KEY = "Student_Profile"

# fix typos
PROFILE_KEY_FIXES = {
    "Cource_of_Study": "course_of_study",
    "Year_of_Study": "year_of_study",
    "Avaliable_Intership_date": "available_internship_date",
    "Preferred_month": "preferred_month",
    "Skills": "skills",
    "Preferred_Roles": "preferred_roles",
    "Minimum_monthly_Salary": "minimum_monthly_salary",
    "preferred_location": "preferred_location",
    "industry_interest": "industry_interest",
    "company_preference": "company_preference",
    "past_experience": "past_experience",
}

# AI output key -> database column
MATCH_FIELDS = {
    "SkillsMatch": "skills_match",
    "RoleMatch": "role_match",
    "IndustryInterestMatch": "industry_interest_match",
    "ExperienceMatch": "experience_match",
    "SalaryMatch": "salary_match",
    "WorkArrangementMatch": "work_arrangement_match",
    "LocationMatch": "location_match",
    "CompanyPreferenceMatch": "company_preference_match",
}

def get_conn(db_path):
    conn = sqlite3.connect(db_path)
    conn.row_factory = sqlite3.Row  # rows behave like dicts
    return conn

def init_db(conn):
    conn.execute("""
        CREATE TABLE IF NOT EXISTS internships (
            job_id             INTEGER PRIMARY KEY,
            company_name       TEXT NOT NULL,
            industry           TEXT NOT NULL,
            job_title          TEXT NOT NULL,
            relevant_course    TEXT NOT NULL,
            monthly_allowance  INTEGER NOT NULL,
            work_mode          TEXT NOT NULL,
            duration_months    INTEGER NOT NULL,
            required_skills    TEXT NOT NULL,
            location_district  TEXT NOT NULL,
            job_description    TEXT NOT NULL
        )
    """)

    # One row per time the AI is run for a student.
    # student_profile is a JSON copy of the profile at that moment.
    conn.execute("""
        CREATE TABLE IF NOT EXISTS recommendation_runs (
            run_id            INTEGER PRIMARY KEY AUTOINCREMENT,
            created_at        TEXT DEFAULT CURRENT_TIMESTAMP,
            student_profile   TEXT NOT NULL,
            overall_feedback  TEXT
        )
    """)

    # One row per internship scored in a run.
    # Match columns allow NULL = not enough info to assess that factor.
    conn.execute("""
        CREATE TABLE IF NOT EXISTS match_results (
            result_id                 INTEGER PRIMARY KEY AUTOINCREMENT,
            run_id                    INTEGER NOT NULL
                                      REFERENCES recommendation_runs(run_id) ON DELETE CASCADE,
            job_id                    INTEGER NOT NULL
                                      REFERENCES internships(job_id),
            skills_match              INTEGER,
            role_match                INTEGER,
            industry_interest_match   INTEGER,
            experience_match          INTEGER,
            salary_match              INTEGER,
            work_arrangement_match    INTEGER,
            location_match            INTEGER,
            company_preference_match  INTEGER,
            overall_match_score       REAL,
            advice                    TEXT
        )
    """)
    conn.commit()

def is_empty(conn, table):
    """True if the table has no rows (i.e. CSV has not been loaded yet)"""
    return conn.execute(f"SELECT COUNT(*) FROM {table}").fetchone()[0] == 0

# ---------- loading the internships CSV ----------

def load_internships_csv(conn, path):
    """Load the internships CSV. Returns how many rows were loaded"""
    if not os.path.exists(path):
        raise FileNotFoundError(f"CSV not found: {path}")
    with open(path, newline="", encoding="utf-8-sig") as f:
        rows = list(csv.DictReader(f))
    with conn:
        for row in rows:
            _insert(conn, row, replace=True)
    return len(rows)

# ---------- internships CRUD ----------

def _insert(conn, data, replace=False):
    data = {k: v for k, v in data.items() if k in INTERNSHIP_COLUMNS}
    columns = ", ".join(data)
    marks = ", ".join(f":{k}" for k in data)
    verb = "INSERT OR REPLACE" if replace else "INSERT"
    return conn.execute(f"{verb} INTO internships ({columns}) VALUES ({marks})", data)

def create_internship(conn, data: dict):
    """Insert a new internship. Returns the new job_id"""
    data = {k: v for k, v in data.items() if k != "job_id"}  # SQLite makes the id
    with conn:
        return _insert(conn, data).lastrowid

def get_internship(conn, job_id: int):
    row = conn.execute("SELECT * FROM internships WHERE job_id = ?", (job_id,)).fetchone()
    return dict(row) if row else None

def list_internships(conn, limit=50, **filters):
    """Example: list_internships(conn, work_mode="Remote", industry="Software")"""
    query = "SELECT * FROM internships WHERE 1=1"
    values = []
    for column, value in filters.items():
        if value is None:
            continue
        if column not in INTERNSHIP_COLUMNS:
            raise ValueError(f"Unknown column: {column}")
        query += f" AND {column} = ?"
        values.append(value)
    query += " LIMIT ?"
    values.append(limit)
    return [dict(r) for r in conn.execute(query, values).fetchall()]
 
def update_internship(conn, job_id: int, changes: dict):
    """Update only the given fields. Returns True if a row was updated"""
    changes = {k: v for k, v in changes.items() if k in INTERNSHIP_COLUMNS and k != "job_id"}
    if not changes:
        return False
    set_clause = ", ".join(f"{k} = ?" for k in changes)
    with conn:
        cur = conn.execute(
            f"UPDATE internships SET {set_clause} WHERE job_id = ?",
            list(changes.values()) + [job_id],
        )
    return cur.rowcount > 0
 
def delete_internship(conn, job_id: int):
    with conn:
        cur = conn.execute("DELETE FROM internships WHERE job_id = ?", (job_id,))
    return cur.rowcount > 0