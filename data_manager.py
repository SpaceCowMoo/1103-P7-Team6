# data_manager.py
# Everything that talks to the SQLite database lives here.
#
# There are 3 tables:
#   internships       - the internship listings (loaded once from the CSV)
#   student_profiles  - a copy (snapshot) of the student profile, saved each time the AI runs
#   matches           - the AI result: top 5 job ids, their scores, their flags and the AI feedback
#
# Every function takes `conn` (the database connection) as its first argument.
# app.setup() opens the connection once and passes it around.

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
        created_at    TEXT DEFAULT CURRENT_TIMESTAMP,
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
        created_at        TEXT DEFAULT CURRENT_TIMESTAMP
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
        for row in rows:
            row = {k: v for k, v in row.items() if k in INTERNSHIP_COLUMNS}  # keeps job_id
            _insert(conn, "internships", row, replace=True)
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

def list_internships(conn, limit=50, **filters):
    """Example: list_internships(conn, work_mode="Hybrid"). limit=-1 means all"""
    query = "SELECT * FROM internships WHERE 1=1"
    values = []
    for column, value in filters.items():
        if value is None:
            continue
        if column not in INTERNSHIP_COLUMNS:
            raise ValueError(f"Unknown column: {column}")
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
