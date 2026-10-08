import csv
import sqlite3
import os

# ---------- database setup ----------

COLUMNS = [
    "job_id", "company_name", "industry", "job_title", "relevant_course",
    "monthly_allowance", "work_mode", "duration_months", "required_skills",
    "location_district", "job_description",
]

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
    conn.commit()

def is_empty(conn):
    """True if the table has no rows (i.e. CSV has not been loaded yet)"""
    return conn.execute("SELECT COUNT(*) FROM internships").fetchone()[0] == 0

def load_csv(conn, path):
    """Load CSV into the table. Existing job_ids are replaced"""
    if not os.path.exists(path):
        raise FileNotFoundError(f"CSV not found: {path}")
    
    with open(path, newline="", encoding="utf-8-sig") as f:
        rows = list(csv.DictReader(f))

    placeholders = ", ".join(f":{c}" for c in COLUMNS)
    with conn:
        conn.executemany(
            f"INSERT OR REPLACE INTO internships ({', '.join(COLUMNS)}) VALUES ({placeholders})",
            rows,
        )
    return len(rows)

# ---------- CRUD ----------

def create_internship(conn, data: dict):
    """Insert a new internship. Returns the new job_id"""
    data = {k: v for k, v in data.items() if k in COLUMNS and k != "job_id"}
    cols = ", ".join(data)
    marks = ", ".join(f":{k}" for k in data)
    with conn:
        cur = conn.execute(f"INSERT INTO internships ({cols}) VALUES ({marks})", data)
    return cur.lastrowid

def get_internship(conn, job_id: int):
    row = conn.execute("SELECT * FROM internships WHERE job_id = ?", (job_id,)).fetchone()
    return dict(row) if row else None

def list_internships(conn, company_name=None, industry=None, job_title=None, relevant_course=None, monthly_allowance=None, work_mode=None, duration_months=None, required_skills=None, location_district=None, limit=50):
    """List internships, optionally filtered by course and/or work_mode"""
    query = "SELECT * FROM internships WHERE 1=1"
    params = []
    if company_name:
        query += " AND company_name = ?"
        params.append(company_name)
    if industry:
        query += " AND industry = ?"
        params.append(industry)
    if job_title:
        query += " AND job_title = ?"
        params.append(job_title)
    if relevant_course:
        query += " AND relevant_course = ?"
        params.append(relevant_course)
    if work_mode:
        query += " AND work_mode = ?"
        params.append(work_mode)
    if monthly_allowance:
        query += " AND monthly_allowance = ?"
        params.append(monthly_allowance)
    if duration_months:
        query += " AND duration_months = ?"
        params.append(duration_months)
    if required_skills:
        query += " AND required_skills = ?"
        params.append(required_skills)
    if location_district:
        query += " AND location_district = ?"
        params.append(location_district)
    query += " ORDER BY job_id LIMIT ?"
    params.append(limit)
    return [dict(r) for r in conn.execute(query, params).fetchall()]

def update_internship(conn, job_id: int, changes: dict):
    """Update only the given fields. Returns True if a row was updated"""
    changes = {k: v for k, v in changes.items() if k in COLUMNS and k != "job_id"}
    if not changes:
        return False
    set_clause = ", ".join(f"{k} = :{k}" for k in changes)
    changes["job_id"] = job_id
    with conn:
        cur = conn.execute(f"UPDATE internships SET {set_clause} WHERE job_id = :job_id", changes)
    return cur.rowcount > 0

def delete_internship(conn, job_id: int):
    with conn:
        cur = conn.execute("DELETE FROM internships WHERE job_id = ?", (job_id,))
    return cur.rowcount > 0
