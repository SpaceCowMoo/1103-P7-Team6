import os
import sys
import time

from dotenv import load_dotenv
load_dotenv()

import io_manager
import data_manager
import logic_manager

INTERNSHIP_DATA = os.getenv("INTERNSHIP_DATA")
STUDENT_PROFILE_JSON = os.getenv("STUDENT_PROFILE_JSON")
DB_PATH = os.getenv("INTERNSHIP_DB")

def setup():
    """Open the database, create the tables, and load the internships CSV for the first time"""
    required = {
        "INTERNSHIP_DATA": INTERNSHIP_DATA,
        "STUDENT_PROFILE_JSON": STUDENT_PROFILE_JSON,
        "INTERNSHIP_DB": DB_PATH,
    }
    missing = [name for name, value in required.items() if not value]
    if missing:
        sys.exit(f"Please set {', '.join(missing)} in your .env file")

    print("Starting up...")

    print("Checking for input files...")
    for path in (INTERNSHIP_DATA, STUDENT_PROFILE_JSON):
        if os.path.exists(path):
            print(f"  Found: {path}")
        else:
            sys.exit(f"  Missing: {path}")

    print(f"Opening database: {DB_PATH}")
    os.makedirs(os.path.dirname(DB_PATH), exist_ok=True)
    conn = data_manager.get_conn(DB_PATH)

    print("Creating tables (if they don't exist)...")
    data_manager.init_db(conn)

    if data_manager.is_empty(conn, "internships"):  # only load once, so CRUD changes are kept
        count = data_manager.load_internships_csv(conn, INTERNSHIP_DATA)
        print(f"Loaded {count} internships")
    else:
        print("Internships already in database, skipping CSV load")

    print("Setup complete!\n")
    time.sleep(1)
    return conn

def demo(conn):
    # CREATE
    # will return new job id
    new_id = data_manager.create_internship(conn, {
        "company_name": "Test Co",
        "industry": "Test",
        "job_title": "Demo Intern",
        "relevant_course": "ICT",
        "monthly_allowance": 1000,
        "work_mode": "Remote",
        "duration_months": "3",
        "required_skills": "Python",
        "location_district": "Punggol",
        "job_description": "FOR AI"

    })
    print("Created job_id:", new_id)

    # READ
    print("\nRead:", data_manager.get_internship(conn, new_id))

    # UPDATE
    data_manager.update_internship(conn, new_id, {"monthly_allowance": 1200})
    print("\nUpdated:", data_manager.get_internship(conn, new_id))

    internship = data_manager.get_internship(conn, new_id)
    print("\nUpdated Filtered:", internship["monthly_allowance"])

    # LIST (with a filter)
    print("\nRemote jobs:", data_manager.list_internships(conn, work_mode="Remote"))

    # DELETE
    data_manager.delete_internship(conn, new_id)
    print("\nDeleted:", data_manager.get_internship(conn, new_id))  # None

def main():
    conn = setup()
    demo(conn)

    loopmain = True
    while loopmain:
        student_profile,loopedboolean = io_manager.get_student_profile_json()
        loopmain,student_profile = io_manager.student_profile_load_check_linker(loopedboolean,student_profile)
        menutype_numerica = io_manager.menuprinter(student_profile)
        student_profile,loopmain =io_manager.menu_function_call_general(menutype_numerica)

    conn.close()

if __name__ == "__main__": main()
