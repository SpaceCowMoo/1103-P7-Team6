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

def setup_database():
    """Open the database, create the tables, and load the internships CSV for the first time"""
    required_data_links = {
        "INTERNSHIP_DATA": INTERNSHIP_DATA,
        "STUDENT_PROFILE_JSON": STUDENT_PROFILE_JSON,
        "INTERNSHIP_DB": DB_PATH,
    }
    missing_data_links = [name for name, value in required_data_links.items() if not value]
    if missing_data_links:
        sys.exit(f"Please set {', '.join(missing_data_links)} in your .env file")

    print("Starting up...")

    print("Checking for input files...")
    for data_path in (INTERNSHIP_DATA, STUDENT_PROFILE_JSON):
        if os.path.exists(data_path):
            print(f"{'':>5}Found: {data_path}")
        else:
            sys.exit(f"{'':>5}Missing: {data_path}")

    print(f"Opening database: {DB_PATH}")
    database_connection = data_manager.get_conn(DB_PATH)

    print("Creating tables (if they don't exist)...")
    data_manager.init_db(database_connection)

    if data_manager.is_empty(database_connection, "internships"):  # only load once, so CRUD changes are kept
        count = data_manager.load_internships_csv(database_connection, INTERNSHIP_DATA)
        print(f"Loaded {count} internships")
    else:
        print("Internships already in database, skipping CSV load")

    print("Setup complete!\n")
    time.sleep(1)
    return database_connection

# Demo is to test functions
def demo(database_connection):
    """Quick showcase of the database: internship CRUD, then save one demo match for testing"""
    print("===== Internship CRUD demo =====")
    # CREATE
    # will return new job id
    new_id = data_manager.create_internship(database_connection, {
        "company_name": "Test Co",
        "company_type": "Start-ups",
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
    print("\nRead:", data_manager.get_internship(database_connection, new_id))

    # UPDATE
    data_manager.update_internship(database_connection, new_id, {"monthly_allowance": 1200})
    print("\nUpdated:", data_manager.get_internship(database_connection, new_id))

    internship = data_manager.get_internship(database_connection, new_id)
    print("\nUpdated monthly allowance:", internship["monthly_allowance"])

    # LIST (with a filter)
    print("\nRemote jobs:", data_manager.list_internships(database_connection, work_mode="Remote"))

    # DELETE
    data_manager.delete_internship(database_connection, new_id)
    print("\nDeleted:", data_manager.get_internship(database_connection, new_id))  # None

    print("\n===== Match demo =====")
    # Only save a demo match when there are none yet, so restarting doesn't pile them up.
    # Delete it with menu option 3, restart, and it comes back for testing again.
    if data_manager.list_matches(database_connection):
        print("Matches already saved, skipping demo match\n")
        return

    # SAVE a match (goes through logic_manager, like the real AI flow does)
    # Fake AI result in the same format as ai_manager.run_ai_pipeline returns
    # The salary / work arrangement / location fields are what logic_manager's flags check
    demo_profile = {"student_profile": {
        "course_of_study": "Accountancy",
        "skills": ["Excel", "Audit"],
        "minimum_monthly_salary": "1500.00",
        "preferred_work_arrangement": ["Hybrid"],
        "preferred_location": ["Central", "South"],
    }}
    # The AI shortlists 5 to 10 internships; logic_manager keeps the best 5
    demo_ai_result = {
        "selected_internships": {
            "internships": [
                {"job_id": 1, "SkillsMatch": 40, "RoleMatch": 30, "IndustryInterestMatch": None,
                 "ExperienceMatch": None, "CompanyPreferenceMatch": None},
                {"job_id": 2, "SkillsMatch": 90, "RoleMatch": 80, "IndustryInterestMatch": None,
                 "ExperienceMatch": None, "CompanyPreferenceMatch": 50},
                {"job_id": 3, "SkillsMatch": 60, "RoleMatch": 50, "IndustryInterestMatch": 40,
                 "ExperienceMatch": None, "CompanyPreferenceMatch": None},
                {"job_id": 4, "SkillsMatch": 20, "RoleMatch": None, "IndustryInterestMatch": None,
                 "ExperienceMatch": None, "CompanyPreferenceMatch": None},
                {"job_id": 5, "SkillsMatch": 70, "RoleMatch": 70, "IndustryInterestMatch": 70,
                 "ExperienceMatch": None, "CompanyPreferenceMatch": None},
                {"job_id": 6, "SkillsMatch": 10, "RoleMatch": 10, "IndustryInterestMatch": None,
                 "ExperienceMatch": None, "CompanyPreferenceMatch": None},  # lowest, gets cut
            ]
        },
        "overall_feedback": {
            "points": [
                "Demo feedback: build up your IFRS knowledge.",
                "Demo feedback: practise data analytics in Excel.",
                "Demo feedback: add an audit project to your portfolio.",
            ]
        },
    }
    match_id = logic_manager.save_ai_result(database_connection, demo_profile, demo_ai_result)
    print("Saved demo match_id:", match_id)

    # READ the match back (profile snapshot + 5 jobs, best first)
    print("\nMatch:", data_manager.get_match(database_connection, match_id), "\n")

# Main app excution
def main():
    database_connection = setup_database()
    #demo(database_connection)

    loopmain = True
    while loopmain:
        student_profile = io_manager.get_student_profile_json()
        menutype_numerica = io_manager.menuprinter(student_profile)
        student_profile,loopmain =io_manager.menu_function_call_general(menutype_numerica,database_connection)

    database_connection.close()

if __name__ == "__main__": main()
