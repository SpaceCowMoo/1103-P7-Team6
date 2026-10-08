import os
import sys

from dotenv import load_dotenv
load_dotenv()

import io_manager
import data_manager

INTERNSHIP_DATA = os.getenv("INTERNSHIP_DATA")
DB_PATH = os.getenv("INTERNSHIP_DB")

def setup():
    """Open the database, create the table, and load the CSV the first time"""
    if not INTERNSHIP_DATA or not DB_PATH:
        sys.exit("Please set INTERNSHIP_DATA and INTERNSHIP_DB in your .env file")

    conn = data_manager.get_conn(DB_PATH)
    data_manager.init_db(conn)
 
    if data_manager.is_empty(conn):  # only load once, so CRUD changes are kept
        try:
            count = data_manager.load_csv(conn, INTERNSHIP_DATA)
            print(f"Loaded {count} internships")
        except FileNotFoundError as e:
            conn.close()
            sys.exit(str(e))
 
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
    
    userinput = io_manager.Get_User_Input()

    conn.close()

main()
