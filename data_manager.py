import csv
import json
import sqlite3
import os

# ---------- database setup ----------

INTERNSHIP_COLUMNS = [
    "job_id", "company_name", "company_type", "industry", "job_title", "relevant_course",
    "monthly_allowance", "work_mode", "duration_months", "required_skills",
    "location_district", "job_description",
]

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

    -- One row per AI run: JSON copy of the student profile at that moment.
    CREATE TABLE IF NOT EXISTS student_profiles (
        profile_id    INTEGER PRIMARY KEY AUTOINCREMENT,
        created_at    TEXT DEFAULT CURRENT_TIMESTAMP,
        profile_json  TEXT NOT NULL
    );

    -- One row per time the AI is run for a student.
    CREATE TABLE IF NOT EXISTS recommendation_runs (
        run_id            INTEGER PRIMARY KEY AUTOINCREMENT,
        created_at        TEXT DEFAULT CURRENT_TIMESTAMP,
        profile_id        INTEGER NOT NULL REFERENCES student_profiles(profile_id),
        overall_feedback  TEXT
    );

    -- One row per internship scored in a run.
    -- Match columns allow NULL = not enough info to assess that factor.
    -- job_id has no foreign key, so past results stay after an internship is deleted.
    CREATE TABLE IF NOT EXISTS match_results (
        result_id                 INTEGER PRIMARY KEY AUTOINCREMENT,
        run_id                    INTEGER NOT NULL
                                  REFERENCES recommendation_runs(run_id) ON DELETE CASCADE,
        job_id                    INTEGER NOT NULL,
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
    );
"""

def get_conn(db_path):
    conn = sqlite3.connect(db_path)
    conn.row_factory = sqlite3.Row  # rows behave like dicts
    conn.execute("PRAGMA foreign_keys = ON")  # SQLite has this off by default
    return conn

def init_db(conn):
    conn.executescript(SCHEMA_SQL)

def is_empty(conn, table):
    """True if the table has no rows (i.e. CSV has not been loaded yet)"""
    return conn.execute(f"SELECT COUNT(*) FROM {table}").fetchone()[0] == 0

def _insert(conn, table, data, replace=False):
    columns = ", ".join(data)
    marks = ", ".join(f":{k}" for k in data)
    verb = "INSERT OR REPLACE" if replace else "INSERT"
    return conn.execute(f"{verb} INTO {table} ({columns}) VALUES ({marks})", data)

def _editable_fields(data):
    """Keep only internship columns the user may set (job_id is made by SQLite)"""
    return {k: v for k, v in data.items() if k in INTERNSHIP_COLUMNS and k != "job_id"}

# ---------- loading the internships CSV ----------

def load_internships_csv(conn, path):
    """Load the internships CSV. Returns how many rows were loaded"""
    if not os.path.exists(path):
        raise FileNotFoundError(f"CSV not found: {path}")
    with open(path, newline="", encoding="utf-8-sig") as f:
        rows = list(csv.DictReader(f))
    with conn:
        for row in rows:
            row = {k: v for k, v in row.items() if k in INTERNSHIP_COLUMNS}  # keeps job_id
            _insert(conn, "internships", row, replace=True)
    return len(rows)

# ---------- internships CRUD ----------

def create_internship(conn, data: dict):
    """Insert a new internship. Returns the new job_id"""
    with conn:
        return _insert(conn, "internships", _editable_fields(data)).lastrowid

def get_internship(conn, job_id: int):
    row = conn.execute("SELECT * FROM internships WHERE job_id = ?", (job_id,)).fetchone()
    return dict(row) if row else None

def list_internships(conn, limit=50, **filters):
    """Example: list_internships(conn, work_mode="Remote", industry="Software"). limit=-1 means all"""
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

def delete_internship(conn, job_id: int):
    with conn:
        cur = conn.execute("DELETE FROM internships WHERE job_id = ?", (job_id,))
    return cur.rowcount > 0

# ---------- AI runs ----------

def save_run(conn, profile, internship_result, ai_output=None, overall_feedback=None):
    """Save one AI run: profile snapshot, the run, and one match row per internship. Returns run_id"""
    ai_by_id = {entry["InternshipID"]: entry for entry in (ai_output or {}).values()}
    with conn:  # all or nothing: any error rolls everything back
        profile_id = _insert(conn, "student_profiles",
                             {"profile_json": json.dumps(profile)}).lastrowid
        run_id = _insert(conn, "recommendation_runs",
                         {"profile_id": profile_id, "overall_feedback": overall_feedback}).lastrowid
        for result in internship_result.values():
            ai = ai_by_id.get(result["InternshipID"], {})
            row = {column: ai.get(key) for key, column in MATCH_FIELDS.items()}  # missing -> NULL
            row.update(run_id=run_id, job_id=result["InternshipID"],
                       overall_match_score=result.get("OverallMatchScore"),
                       advice=result.get("Advice"))
            _insert(conn, "match_results", row)
    return run_id

def get_run(conn, run_id):
    """One run with its profile and match results. None if run_id is unknown"""
    row = conn.execute("""
        SELECT r.run_id, r.created_at, r.overall_feedback, p.profile_json
        FROM recommendation_runs r JOIN student_profiles p ON p.profile_id = r.profile_id
        WHERE r.run_id = ?""", (run_id,)).fetchone()
    if row is None:
        return None
    run = dict(row)
    run["profile"] = json.loads(run.pop("profile_json"))
    run["matches"] = [dict(r) for r in conn.execute(
        "SELECT * FROM match_results WHERE run_id = ? ORDER BY result_id", (run_id,))]
    return run

def list_runs(conn, limit=-1):
    """Past runs, newest first, with how many internships each run scored. limit=-1 means all"""
    rows = conn.execute("""
        SELECT r.run_id, r.created_at, r.overall_feedback, COUNT(m.result_id) AS match_count
        FROM recommendation_runs r LEFT JOIN match_results m ON m.run_id = r.run_id
        GROUP BY r.run_id ORDER BY r.run_id DESC LIMIT ?""", (limit,))
    return [dict(r) for r in rows]
