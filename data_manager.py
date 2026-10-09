import csv
import sqlite3
import os

# ---------- database setup ----------

INTERNSHIP_COLUMNS = [
    "job_id", "company_name", "industry", "job_title", "relevant_course",
    "monthly_allowance", "work_mode", "duration_months", "required_skills",
    "location_district", "job_description",
]

STUDENT_COLUMNS = [
    "input_id", "course_of_study", "year_of_study", "internship_duration",
    "prefer_month", "skills", "prefer_role", "min_monthly_salary",
    "preferred_location", "industry_interests", "company_preference",
    "past_experience",
]

# Temp: clean student csv headers
STUDENT_CSV_HEADERS = {
    "Input_ID": "input_id",
    "Course_of_Study": "course_of_study",
    "Year_of_Study": "year_of_study",
    "Internship_Duration": "internship_duration",
    "Prefer_month": "prefer_month",
    "Skills": "skills",
    "Prefer_Role": "prefer_role",
    "Minimum_monthly_salary": "min_monthly_salary",
    "Preferred_location": "preferred_location",
    "Industry_interests": "industry_interests",
    "Company_preference": "company_preference",
    "Past_experience": "past_experience",
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
    # Lists like skills / roles are stored as text, e.g. '["Python", "Java"]'
    conn.execute("""
        CREATE TABLE IF NOT EXISTS student_profiles (
            input_id             TEXT PRIMARY KEY,
            course_of_study      TEXT NOT NULL,
            year_of_study        TEXT NOT NULL,
            internship_duration  TEXT NOT NULL,
            prefer_month         TEXT NOT NULL,
            skills               TEXT NOT NULL,
            prefer_role          TEXT NOT NULL,
            min_monthly_salary   INTEGER NOT NULL,
            preferred_location   TEXT NOT NULL,
            industry_interests   TEXT NOT NULL,
            company_preference   TEXT NOT NULL,
            past_experience      TEXT NOT NULL
        )
    """)
    conn.commit()

def is_empty(conn, table):
    """True if the table has no rows (i.e. CSV has not been loaded yet)"""
    return conn.execute(f"SELECT COUNT(*) FROM {table}").fetchone()[0] == 0

# ---------- loading CSV files ----------

def read_csv(path):
    """Read a CSV file and return a list of dicts (one per row)"""
    if not os.path.exists(path):
        raise FileNotFoundError(f"CSV not found: {path}")
    with open(path, newline="", encoding="utf-8-sig") as f:
        return list(csv.DictReader(f))

def load_internships_csv(conn, path):
    """Load the internships CSV. Returns how many rows were loaded"""
    rows = read_csv(path)
    for row in rows:
        _insert(conn, "internships", INTERNSHIP_COLUMNS, row, replace=True)
    return len(rows)
 
 
def load_students_csv(conn, path):
    """Load the student profiles CSV. Returns how many rows were loaded"""
    rows = read_csv(path)
    for row in rows:
        # rename CSV headers to database column names
        student = {STUDENT_CSV_HEADERS[h]: row[h] for h in STUDENT_CSV_HEADERS}
        _insert(conn, "student_profiles", STUDENT_COLUMNS, student, replace=True)
    return len(rows)

# ---------- helpers used by the CRUD functions ----------

def _insert(conn, table, allowed_columns, data, replace=False):
    """Insert one row. Only keys in allowed_columns are used. Returns the new row id"""
    data = {k: v for k, v in data.items() if k in allowed_columns}
    columns = ", ".join(data)
    marks = ", ".join(f":{k}" for k in data)
    verb = "INSERT OR REPLACE" if replace else "INSERT"
    with conn:  # "with conn" saves (commits) automatically
        cur = conn.execute(f"{verb} INTO {table} ({columns}) VALUES ({marks})", data)
    return cur.lastrowid
 
 
def _get(conn, table, key_column, key):
    row = conn.execute(f"SELECT * FROM {table} WHERE {key_column} = ?", (key,)).fetchone()
    return dict(row) if row else None
 
 
def _list(conn, table, allowed_columns, filters, limit):
    """Return rows where every filter matches, e.g. filters={"work_mode": "Remote"}"""
    query = f"SELECT * FROM {table} WHERE 1=1"
    values = []
    for column, value in filters.items():
        if value is None:
            continue  # no filter given for this column
        if column not in allowed_columns:
            raise ValueError(f"Unknown column: {column}")
        query += f" AND {column} = ?"
        values.append(value)
    query += " LIMIT ?"
    values.append(limit)
    return [dict(r) for r in conn.execute(query, values).fetchall()]
 
 
def _update(conn, table, allowed_columns, key_column, key, changes):
    """Update only the given fields. Returns True if a row was updated"""
    changes = {k: v for k, v in changes.items() if k in allowed_columns and k != key_column}
    if not changes:
        return False
    set_clause = ", ".join(f"{k} = ?" for k in changes)
    values = list(changes.values()) + [key]
    with conn:
        cur = conn.execute(f"UPDATE {table} SET {set_clause} WHERE {key_column} = ?", values)
    return cur.rowcount > 0
 
 
def _delete(conn, table, key_column, key):
    with conn:
        cur = conn.execute(f"DELETE FROM {table} WHERE {key_column} = ?", (key,))
    return cur.rowcount > 0

# ---------- internships CRUD ----------
 
def create_internship(conn, data: dict):
    """Insert a new internship. Returns the new job_id"""
    data = {k: v for k, v in data.items() if k != "job_id"}  # SQLite makes the id
    return _insert(conn, "internships", INTERNSHIP_COLUMNS, data)
 
def get_internship(conn, job_id: int):
    return _get(conn, "internships", "job_id", job_id)
 
def list_internships(conn, limit=50, **filters):
    """Example: list_internships(conn, work_mode="Remote", industry="Software")"""
    return _list(conn, "internships", INTERNSHIP_COLUMNS, filters, limit)
 
def update_internship(conn, job_id: int, changes: dict):
    return _update(conn, "internships", INTERNSHIP_COLUMNS, "job_id", job_id, changes)
 
def delete_internship(conn, job_id: int):
    return _delete(conn, "internships", "job_id", job_id)

# ---------- student profiles CRUD ----------
 
def create_student(conn, data: dict):
    """Insert a new student input profile"""
    _insert(conn, "student_profiles", STUDENT_COLUMNS, data)
    return data["input_id"]
 
def get_student(conn, input_id: str):
    return _get(conn, "student_profiles", "input_id", input_id)
 
def list_students(conn, limit=50, **filters):
    """Example: list_students(conn, company_preference="MNC")"""
    return _list(conn, "student_profiles", STUDENT_COLUMNS, filters, limit)
 
def update_student(conn, input_id: str, changes: dict):
    return _update(conn, "student_profiles", STUDENT_COLUMNS, "input_id", input_id, changes)
 
def delete_student(conn, input_id: str):
    return _delete(conn, "student_profiles", "input_id", input_id)
