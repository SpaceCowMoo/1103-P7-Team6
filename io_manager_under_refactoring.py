#general function for io manager
import os
import json
import math
from pathlib import Path
import re
from datetime import datetime, timezone
from dateutil.relativedelta import relativedelta
import textwrap
from zoneinfo import ZoneInfo

import data_manager
import logic_manager  
from asyncio import log

from Student_Login_detail import Student_login_details
from Student_Profile_Class import StudentProfile
from Student_Resume_Class import StudentResume
from Past_internship_done_class import PastInternship

consoleWidth_60 = 60
consoleWidth_55 = 55
profileFieldWidth = 28
courseCount = 0

INTERNSHIP_FILTER_LABELS = (
    "Job ID",
    "Company Name",
    "Company Type",
    "Industry",
    "Job Title",
    "Relevant Course",
    "Monthly Allowance",
    "Work Mode",
    "Duration Months",
    "Required Skills",
    "Location",
)

PROFILE_UPDATE_FIELDS = (
    "Course of study",
    "Year of study",
    "Available internship dates",
    "Skills",
    "Preferred roles",
    "Minimum monthly salary",
    "Preferred work arrangement",
    "Preferred location",
    "Industry interest",
    "Company preference",
    "Past experience",
)


INTERNSHIP_FILTER_FIELDS = {
    0: {"label": "Job ID", "column": "job_id"},
    1: {"label": "Company Name", "column": "company_name"},
    2: {"label": "Company Type", "column": "company_type"},
    3: {"label": "Industry", "column": "industry"},
    4: {"label": "Job Title", "column": "job_title"},
    5: {"label": "Relevant Course", "column": "relevant_course"},
    6: {"label": "Monthly Allowance", "column": "monthly_allowance"},
    7: {"label": "Work Mode", "column": "work_mode"},
    8: {"label": "Duration Months", "column": "duration_months"},
    9: {"label": "Required Skills", "column": "required_skills"},
    10: {"label": "Location", "column": "location_district"},
}


# Formating for CLI display
def format_list(item):
    if isinstance(item, list) and item:
        return ", ".join(item)
    if isinstance(item, str) and item.strip():
        return item
    return "None specified"

def display_message(*args):
    """Display a message to the user"""
    print(*args)

def display_error(message):
    """Display an error message to the user"""
    display_message("Error:", message)

def get_user_input(prompt):
    """Get input from the user"""
    return input(prompt)

def print_heading(title):
        print("\n" + "=" * consoleWidth_60)
        print(f"{title:^{consoleWidth_60}}")
        print("=" * consoleWidth_60)


#function for student login and profile creation
def load_login_details(username , password , user_id , user_role):
    login_details = StudentLoginDetails(user_id, user_role, username, password)
    return login_details

def loaded_temporary_login_details():
    """Load temporary login details for testing"""
    username = "test_user"
    password = "test_pass"
    user_id = "12345"
    user_role = "student"
    return load_login_details(username, password, user_id, user_role)

def load_student_profile_none():
    """Load a temporary student profile with no resume or listings for testing"""
    name = "John Doe"
    age = 20
    student_id = "S123456"
    return StudentProfile(name, age, student_id)

def menu_type(menu_name, student_profile: StudentProfile | None = None):
    match menu_name:
        case "Starting":
            print_heading("INTERN LINK")
            print("Welcome to Intern Link.")
            print("Please enter your student profile to get started.")
            print("=" * consoleWidth_60)

        case "login" | "Login":
            print("Welcome to Intern Link. Please log in to continue.")

        case  "Main_Menu":
            print_heading("INTERN LINK")
            print("  1. Update View Profile")
            print("  2. Update Resume")
            print("  3. View past listings")
            print("  4. Delete History")
            print("  5. Search for internships")
            print("  6. Find internship matches (AI)")
            print("  7. Exit")
            print("=" * consoleWidth_60)

        case "First_Resume":
            print("Welcome to InternLink. Please enter your first student resume.")

        case "CourseDisplay":
            course_sections = [
                ("Infocomm Technology", [
                    "Applied Artificial Intelligence",
                    "Applied Computing (Fintech)",
                    "Applied Computing Degree (via CSM Pathway)",
                    "Computer Engineering",
                    "Computer Science in Interactive Media and Game Development",
                    "Computer Science in Real-Time Interactive Simulation",
                    "Computing Science",
                    "Digital Art and Animation",
                    "Information and Communications Technology (Information Security)",
                    "Information and Communications Technology (Software Engineering)",
                    "User Experience and Game Design",
                ]),
                ("Engineering", [
                    "Aircraft Systems Engineering",
                    "Chemical Engineering",
                    "Civil Engineering",
                    "Digital Supply Chain",
                    "Electrical and Electronic Engineering",
                    "Electrical and Electronic Engineering Degree (via CSM Pathway)",
                    "Electrical Power Engineering",
                    "Electronics and Data Engineering",
                    "Engineering Systems",
                    "Infrastructure and Systems Engineering Degree (via CSM Pathway)",
                    "Mechanical Design and Manufacturing Engineering",
                    "Mechanical Engineering",
                    "Naval Architecture and Marine Engineering",
                    "Robotics Systems",
                    "Sustainable Built Environment",
                ]),
                ("Business, Communication and Design", [
                    "Accountancy",
                    "Aviation Management",
                    "Business and Infocomm Technology",
                    "Communication and Digital Media",
                    "Hospitality and Tourism Management",
                    "Integrated Studies in Technology and Management",
                    "Integrated Studies in Technology and Management with Specialisation in Supply Chain",
                ]),
                ("Food, Chemical and Biotechnology", [
                    "Dietetics and Nutrition",
                    "Food Business Management (Baking and Pastry Arts)",
                    "Food Business Management (Culinary Arts)",
                    "Food Technology",
                    "Pharmaceutical Engineering",
                ]),
                ("Health and Social Sciences", [
                    "Diagnostic Radiography",
                    "Nursing",
                    "Nursing (Pre-registration and Specialty Training)",
                    "Occupational Therapy",
                    "Physiotherapy",
                    "Radiation Therapy",
                    "Speech and Language Therapy",
                ]),
            ]
            print_heading("COURSES OF STUDY")
            course_number = 1
            for section, courses in course_sections:
                print(f"\n{section}")
                for course in courses:
                    print(f"  {course_number:>2}. {course}")
                    course_number += 1
            print("\n" + "=" * consoleWidth_60)

        case "LocationDisplay":
            singapore_areas_list = ["North", "East", "South", "West", "Central"]
            print_heading("PREFERRED LOCATIONS")
            for number, area in enumerate(singapore_areas_list, 1):
                print(f"  {number:>2}. {area}")
            print("=" * consoleWidth_60)

        case "PreferredWorkArrangement":
            work_arrangements = ["On-site", "Hybrid", "No Preference"]
            print_heading("PREFERRED WORK ARRANGEMENT")
            for number, word_arrangement in enumerate(work_arrangements, 1):
                print(f"  {number}. {word_arrangement}")

        case "CompanyPreference":
            company_preferences = [
                "Start-ups",
                "Multi-National Corporations (MNCs)",
                "Government",
                "Statutory Boards",
                "Small-to-Medium Enterprises (SMEs)",
            ]
            print_heading("COMPANY PREFERENCES")
            for number, preference in enumerate(company_preferences, 1):
                print(f"  {number:>2}. {preference}")
            print("=" * consoleWidth_60)

        case "UpdateDisplay":
            print_heading("YOUR STUDENT PROFILE")
            if student_profile is None:
                display_error("A student profile is required to display profile details.")
            else:
                print(f"Name: {student_profile.get_name()}")
                print(f"Age: {student_profile.get_age()}")
                print(f"Student ID: {student_profile.get_student_id()}")

        case "FilterInternships":
            print_heading("FILTER OPTIONS")
            for number, label in enumerate(INTERNSHIP_FILTER_LABELS):
                print(f"  {number:>2}. {label}")
            print("=" * consoleWidth_60)

        case _:
            print(f"Unknown menu type: {menu_name}")

#Login functions
def login_Username_verification(username,db):
    return StudentProfile.get_by_username(db, username) is not None

def login_Username_validation_outcome(db,username):
    student_profile = StudentProfile.get_by_username(db, username)
    return student_profile is not None, student_profile

def login_Password_verification(password,studentprofile:StudentProfile):
    if studentprofile is None:
        return False
    login_details = studentprofile.get_login_details()
    return login_details is not None and login_details.get_password() == password


def login_Password_validation_outcome(db, username, password):
    username_valid, student_profile = login_Username_validation_outcome(db, username)
    return username_valid and login_Password_verification(password, student_profile)


def login_verification(db,username, password):
    if login_Password_validation_outcome(db, username, password):
        display_message("Login successful!")
        return True
    display_error("Login failed. Please check your username and password.")
    return False

def login_loop(db):
    Timeout = 3
    while Timeout > 0:
        username = get_user_input("Enter your username: ")
        password = get_user_input("Enter your password: ")
        if login_verification(db,username, password):
            student_profile = StudentProfile.get_by_username(db, username)
            user_id = student_profile.get_login_details().get_user_id()
            return load_from_database(db, user_id, student_profile) ,user_id
        Timeout -= 1
        display_message("Please try again.")
    return None


# Check Student Profile functions
def check_student_profile(student_profile: StudentProfile):
    if student_profile is None:
        display_error("Student profile is None.")
        return False
    if not isinstance(student_profile, StudentProfile):
        display_error("Invalid student profile object.")
        return False
    display_message("Student profile is valid.")
    return True

def check_student_profile_details(student_profile: StudentProfile):
    if not check_student_profile(student_profile):
        return False
    details = student_profile.fetch_Student_Profile_details()
    if not details.get("name") or not details.get("age") or not details.get("student_id"):
        display_error("Student profile is missing required details.")
        return False
    display_message("Student profile details are valid.")
    return True

def check_student_profile_resume(student_profile: StudentProfile):
    if not check_student_profile(student_profile):
        return False
    resume_list = student_profile.get_Student_Resume()
    if not resume_list:
        display_error("No Student Resume was found , Creating a new one.")
        return False
    display_message("Student resumes was found")
    return True

#student resume validator

#Add student_resume

def standard_num_to_String_adder(values, input_id):
    if not Standard_number_checker("int", input_id):
        raise ValueError("The selection must be an integer.")
    input_id = int(input_id)
    if not Standard_numerical_range_checker(input_id, 1, len(values)):
        raise ValueError(f"The selection must be between 1 and {len(values)}.")
    return values[input_id - 1]

def Standard_Checker(inputs):
    if inputs is None:
        return False
    if isinstance(inputs, str):
        return bool(inputs.strip())
    if isinstance(inputs, (list, tuple, dict, set)):
        return bool(inputs)
    return True

def Standard_number_checker(validation_type: str, inputs):
    if not Standard_Checker(inputs):
        return False
    value = str(inputs).strip()
    if validation_type == "int":
        try:
            int(value)
        except (TypeError, ValueError, OverflowError):
            return False
    elif validation_type == "float":
        try:
            number = float(value)
        except (TypeError, ValueError, OverflowError):
            return False
        return math.isfinite(number)
    else:
        return False
    return True
        
def Standard_numerical_range_checker(
    inputs,
    lowernum: int | float = 0,
    highernum: int | float = 0,
):
    if not Standard_number_checker("float", inputs):
        return False
    number = float(inputs)
    if lowernum != 0 and number < lowernum:
        return False
    if highernum != 0 and number > highernum:
        return False
    return True


def course_of_study_words(course_of_study_id):
    courses = [
    "Applied Artificial Intelligence",
    "Applied Computing (Fintech)",
    "Applied Computing Degree (via CSM Pathway)",
    "Computer Engineering",
    "Computer Science in Interactive Media and Game Development",
    "Computer Science in Real-Time Interactive Simulation",
    "Computing Science",
    "Digital Art and Animation",
    "Information and Communications Technology (Information Security)",
    "Information and Communications Technology (Software Engineering)",
    "User Experience and Game Design",
    "Aircraft Systems Engineering",
    "Chemical Engineering",
    "Civil Engineering",
    "Digital Supply Chain",
    "Electrical and Electronic Engineering",
    "Electrical and Electronic Engineering Degree (via CSM Pathway)",
    "Electrical Power Engineering",
    "Electronics and Data Engineering",
    "Engineering Systems",
    "Infrastructure and Systems Engineering Degree (via CSM Pathway)",
    "Mechanical Design and Manufacturing Engineering",
    "Mechanical Engineering",
    "Naval Architecture and Marine Engineering",
    "Robotics Systems",
    "Sustainable Built Environment",
    "Accountancy",
    "Aviation Management",
    "Business and Infocomm Technology",
    "Communication and Digital Media",
    "Hospitality and Tourism Management",
    "Integrated Studies in Technology and Management",
    "Integrated Studies in Technology and Management with Specialisation in Supply Chain",
    "Dietetics and Nutrition",
    "Food Business Management (Baking and Pastry Arts)",
    "Food Business Management (Culinary Arts)",
    "Food Technology",
    "Pharmaceutical Engineering",
    "Diagnostic Radiography",
    "Nursing",
    "Nursing (Pre-registration and Specialty Training)",
    "Occupational Therapy",
    "Physiotherapy",
    "Radiation Therapy",
    "Speech and Language Therapy"
    ]
    global courseCount
    courseCount = len(courses)
    return standard_num_to_String_adder(courses, course_of_study_id)

def validate_course_of_study(course):
    if not Standard_Checker(course):
        print("Invalid input. Please enter a number corresponding to your course of study.")
        return False
    if not Standard_number_checker("int", course):
        print("Invalid input. Please enter a number corresponding to your course of study.")
        return False
    if not Standard_numerical_range_checker(int(course), 1, courseCount):
        print(f"Invalid input. Please enter a number between 1 and {courseCount}.")
        return False
    return True

def course_of_study_input(courseofStudy):
    course_of_study_words(10)
    is_valid = validate_course_of_study(courseofStudy)
    while is_valid == False:
        courseofStudy = get_user_input("Please enter your course of study (1-45):")
        is_valid = validate_course_of_study(courseofStudy)
    
    return course_of_study_words(int(courseofStudy))

def validate_Year_of_Study(year):
    while True:
        match = None
        if Standard_Checker(year):
            match = re.fullmatch(r"(?:Year\s*)?([1-6])", year.strip(), re.IGNORECASE)
        if (
            match is not None
            and Standard_number_checker("int", match.group(1))
            and Standard_numerical_range_checker(int(match.group(1)), 1, 6)
        ):
            return match.group(1)
        print("Invalid input. Please enter a year between 1 and 6.")
        year = get_user_input("Please enter your year of study (1-6):")

def check_Internship_Duration_format(internshipDuration):
    if not Standard_Checker(internshipDuration):
        print("Invalid input. Please enter the duration of your available internships in the format 'DD/MM/YYYY - DD/MM/YYYY'.")
        return "Invalid","Invalid","Invalid",False
    internshipDuration = internshipDuration.split("-")
    try:
        startingdate = datetime.strptime(internshipDuration[0].strip(), "%d/%m/%Y")
        endingdate =datetime.strptime(internshipDuration[1].strip(), "%d/%m/%Y")
        if startingdate < datetime.now() or endingdate< datetime.now():
            print("Internship dates cannot be in the past.")
            return "Invalid","Invalid","Invalid",False
        if startingdate>endingdate or endingdate<startingdate:
            print("The end date must be on or after the start date.")
            return "Invalid","Invalid","Invalid",False
        diff = relativedelta(endingdate, startingdate)
        total_months = (diff.years * 12) + diff.months
        if total_months<3:
            print("Duration of Internship dates must be more than 3 months.")
            return "Invalid","Invalid","Invalid",False
        else:
            return startingdate,endingdate,total_months,True
    except Exception:
        print("Invalid input. Please enter the duration of your available internships in the format 'DD/MM/YYYY - DD/MM/YYYY'.")
        return "Invalid","Invalid","Invalid",False

def internship_duration_checker(internshipDuration):
    starting_date,ending_date,Total_month,is_valid = check_Internship_Duration_format(internshipDuration)
    
    while is_valid == False:
        internshipDuration = get_user_input("Enter your available internship dates (DD/MM/YYYY - DD/MM/YYYY):")
        starting_date,ending_date,Total_month,is_valid = check_Internship_Duration_format(internshipDuration)
    return starting_date,ending_date,Total_month

def Confirming_input(confirmation):
    while (
        not Standard_Checker(confirmation)
        or str(confirmation).strip().casefold() not in {"y", "n"}
    ):
        confirmation = get_user_input("Please enter only Y or N:")
    return confirmation.strip().casefold() == "y"

def append_unique_value(values, value, field_name):
    normalized_value = value.strip().casefold()
    if any(existing.strip().casefold() == normalized_value for existing in values):
        print(f"{field_name} already added; duplicates are not allowed.")
        return False
    values.append(value.strip())
    return True

def validate_skill(skillsinput):
    while True:
        if not Standard_Checker(skillsinput):
            print("Invalid input. Please try again.")
        elif Standard_number_checker("int", skillsinput):
            print("You entered a number.")
            if Confirming_input(get_user_input("Is this correct? (Y/N):")):
                return skillsinput
        elif len(skillsinput) == 1:
            print("You entered a single character.")
            if Confirming_input(get_user_input("Is this correct? (Y/N):")):
                return skillsinput
        else:
            return skillsinput

        skillsinput = get_user_input("Enter a skill (or type 'exit' to finish):")

#def exitChecker(skillsinput,skillslist):
    


def continuousloopskills(skillsinput):
    skillslist = []
    # Validate exit method
    while True:
        skillinput = validate_skill(skillsinput)
        skillinput = skillinput.strip()
        if skillinput.casefold() == "exit" and len(skillslist) <= 0:
            print("[MANDATORY] Please input in a skill.")
        elif skillinput.casefold() == "exit" and len(skillslist) > 0:
            return skillslist
        else:
            append_unique_value(skillslist, skillinput, "Skill")
        skillsinput = get_user_input("Enter another skill (type 'exit' to finish):")

def validate_Preferred_role(preferred_role):
    if not Standard_Checker(preferred_role):
        print("Please enter a value.")
        return False
    if Standard_number_checker("int", preferred_role):
        print("You entered a number.")
        return Confirming_input(get_user_input("Is this preferred role correct? (Y/N):"))
    if len(preferred_role.strip()) == 1:
        print("You entered a single character. Is this correct?")
        return Confirming_input(get_user_input("Is this preferred role correct? (Y/N):"))
    return True

def checking_Preferred_role_input(Preferred_role):
    is_valid = validate_Preferred_role(Preferred_role)
    while is_valid == False:
        Preferred_role = get_user_input("Enter a preferred role (or type 'exit' to finish):")
        is_valid = validate_Preferred_role(Preferred_role)
    return is_valid,Preferred_role

def continoous_Preferred_role(Preferred_role):
    Preferred_rolelist = []
    is_valid,Preferred_role = checking_Preferred_role_input(Preferred_role)
    if Preferred_role.strip().lower() == "exit":
        return Preferred_rolelist
    append_unique_value(Preferred_rolelist, Preferred_role, "Preferred role")
    while True:
        Preferred_role = get_user_input("Enter another preferred role (or type 'exit' to finish):")
        _, Preferred_role = checking_Preferred_role_input(Preferred_role)
        if Preferred_role.lower().strip() == "exit":
            return Preferred_rolelist
        append_unique_value(Preferred_rolelist, Preferred_role, "Preferred role")

def validating_minimum_monthly_salary(minimum_month_salary):
    if not Standard_Checker(minimum_month_salary):
        print("Please enter a value.")
        return False
    if minimum_month_salary.lower().strip() == "exit":
        return True
    if not Standard_number_checker("float", minimum_month_salary):
        print("Please enter a number.")
        return False
    minimum_month_salary = float(minimum_month_salary)
    if not Standard_numerical_range_checker(minimum_month_salary, 0.01, 10000):
        if minimum_month_salary <= 0:
            print("The number must be greater than 0. Please input again.")
        else:
            print("The value you entered is greater than 10,000. Please input again.")
        return False
    return True

def minimum_monthly_salary_checker(minimum_monthly_salary):
    is_valid = validating_minimum_monthly_salary(minimum_monthly_salary)
    while is_valid == False:
        minimum_monthly_salary = get_user_input("Enter your expected monthly salary (or type 'exit' to skip):")
        is_valid = validating_minimum_monthly_salary(minimum_monthly_salary)
    if minimum_monthly_salary.strip().casefold() != "exit":
        return f"{float(minimum_monthly_salary):.2f}"
    return 0.00

def validating_preferred_work_location(preferred_work_locations):
    if not Standard_Checker(preferred_work_locations):
        print("Invalid value.")
        return False
    if preferred_work_locations.lower().strip() == "exit":
        return True
    if not Standard_number_checker("int", preferred_work_locations):
        print("Please enter a number.")
        return False
    if not Standard_numerical_range_checker(int(preferred_work_locations), 1, 3):
        print("Please enter a valid number.")
        return False
    return True

def validating_perferred_work_location_input(preferred_work_locations):
    is_valid = validating_preferred_work_location(preferred_work_locations)
    while is_valid == False:
        preferred_work_locations = get_user_input(
            "Enter a preferred work arrangement (1-3, or type 'exit' to finish):"
        )
        is_valid = validating_preferred_work_location(preferred_work_locations)
    return preferred_work_locations.strip(), is_valid

def num_to_string_work_location(preferred_work_arrangement):
    preferred_word_arrangement = ["On-site", "Hybrid", "No Preference"]
    return standard_num_to_String_adder(
        preferred_word_arrangement, preferred_work_arrangement
    )

def preferred_work_location_looper(preferred_work_arrangement):
    arrangements = ["On-site", "Hybrid", "No Preference"]
    selected = []
    response = preferred_work_arrangement.strip()

    if response.casefold() == "exit":
        return [arrangements[0],arrangements[1]]

    while True:
        response, _ = validating_perferred_work_location_input(response)
        if response.casefold() == "exit":
            return selected
        if int(response)==3:
            selected = [arrangements[0],arrangements[1]]
            return selected
        arrangement = standard_num_to_String_adder(arrangements, response)
        append_unique_value(selected, arrangement, "Work arrangement")
        response = get_user_input(
            "Choose another work arrangement (1-3, or type 'exit' to finish):"
        )

def pre_work_location_input_validation(preferred_work_locations):
    preferred_work_locations,isvalid = validating_perferred_work_location_input(preferred_work_locations)
    if isvalid != False:
        preferred_work_locations = int(preferred_work_locations)
        preferred_work_locations = num_to_string_work_location(preferred_work_locations)
    return preferred_work_locations

def validating_preferred_locations(preferredlocations):
    if not Standard_Checker(preferredlocations):
        print("Invalid value.")
        return False
    if preferredlocations.lower().strip() == "exit":
        return True
    if not Standard_number_checker("int", preferredlocations):
        print("Please enter a number.")
        return False
    if not Standard_numerical_range_checker(int(preferredlocations), 1, 5):
        print("Please enter a valid number.")
        return False
    return True

def validating_perferred_location_input(preferredlocations):
    is_valid = validating_preferred_locations(preferredlocations)
    while is_valid == False:
        preferredlocations = get_user_input("Choose a preferred location (1-5, or type 'exit' to finish):")
        is_valid = validating_preferred_locations(preferredlocations)
    return preferredlocations

def preferredlocations_number_to_string(preferredlocationnumber):
    singapore_areas_list = ["North","East","South","West","Central"]
    return standard_num_to_String_adder(singapore_areas_list, preferredlocationnumber)

def preferredlocation_listadder(preferredlocations):
    locations = ["North", "East", "South", "West", "Central"]
    selected = []
    response = preferredlocations.strip()

    if response.casefold() == "exit":
        return locations

    while True:
        response = validating_perferred_location_input(response)
        if response.casefold() == "exit":
            print("Selected locations:", ", ".join(selected) or "None")
            return selected

        location = preferredlocations_number_to_string(response)
        append_unique_value(selected, location, "Preferred location")
        print("\nSelected locations:", ", ".join(selected))
        response = get_user_input(
            "Choose another preferred location (1-5, or type 'exit' to finish):"
        )
        
def validate_Industry_interest(Industrial_intrest):
    if not Standard_Checker(Industrial_intrest):
        print("Please enter a valid response.")
        return False
    if Industrial_intrest.strip().lower() == "exit":
        return True
    if Standard_number_checker("int", Industrial_intrest):
        print("You entered a number.")
        return Confirming_input(get_user_input("Is this industry interest correct? (Y/N):"))
    if len(Industrial_intrest.strip()) == 1:
        print("You entered a single character.")
        return Confirming_input(get_user_input("Is this industry interest correct? (Y/N):"))
    return True

def Industrial_input_checker(industrial_interest):
    is_valid = validate_Industry_interest(industrial_interest)
    while is_valid == False:
        industrial_interest = get_user_input("Enter an industry interest (or type 'exit' to finish):")
        is_valid = validate_Industry_interest(industrial_interest)
    return industrial_interest,is_valid

def industrial_input_list_adder(industrial_interest):
    industrial_interestlist = []
    while True:
        industrial_interest, _ = Industrial_input_checker(industrial_interest)
        if industrial_interest.strip().casefold() == "exit":
            return industrial_interestlist
        append_unique_value(industrial_interestlist, industrial_interest, "Industry interest")
        industrial_interest = get_user_input("Enter another industry interest (or type 'exit' to finish):")

def validate_company_preference(company_perference):
    if not Standard_Checker(company_perference):
        print("Please enter a value.")
        return False
    if company_perference.lower().strip() == "exit":
        return True
    if not Standard_number_checker("int", company_perference):
        print("Please enter a number.")
        return False
    if not Standard_numerical_range_checker(int(company_perference), 1, 5):
        print("Please enter a number between 1 and 5.")
        return False
    return True

def company_preference_number_to_String(company_preference):
    company_preferenceslist = [
        "Start-ups",
        "Multi-National Corporations (MNCs)",
        "Government",
        "Statutory Boards",
        "Small-to-Medium Enterprises (SMEs)",
    ]
    return standard_num_to_String_adder(company_preferenceslist, company_preference)

def company_preference_checker(company_preference):
    is_valid = validate_company_preference(company_preference)
    while is_valid == False:
        company_preference = get_user_input("Choose a company preference (1-5, or type 'exit' to skip):")
        is_valid = validate_company_preference(company_preference)
    return company_preference

def company_preference_looper(company_preference):
    preferences = [
        "Start-ups",
        "Multi-National Corporations (MNCs)",
        "Government",
        "Statutory Boards",
        "Small-to-Medium Enterprises (SMEs)",
    ]
    selected = []
    response = company_preference.strip()

    if response.casefold() == "exit":
        return preferences

    while True:
        response = company_preference_checker(response)
        if response.casefold() == "exit":
            return selected

        preference = company_preference_number_to_String(response)
        append_unique_value(selected, preference, "Company preference")
        print("\nSelected Company Preferences:", ", ".join(selected) or "None")
        response = get_user_input(
            "Choose another company preference (1-5, or type 'exit' to finish):"
        )

# Check if user inputs an empty string for job_title and job_discription
def validate_job_string_input(job_string, variable_name):
    while not Standard_Checker(job_string):
        print(f"Please enter a value for {variable_name}.")
        job_string = get_user_input(f"Enter {variable_name}:")
    return job_string.strip()

def validate_past_experience(job_period_past):
    while True:
        try:
            start_text, end_text = job_period_past.split("-", maxsplit=1)
            start_date = datetime.strptime(start_text.strip(), "%d/%m/%Y")
            end_date = datetime.strptime(end_text.strip(), "%d/%m/%Y")
            today = datetime.today().date()
            if start_date > end_date:
                print("Start date is a date after end date")
            elif start_date.date() > today or end_date.date() > today:
                print(f"Please set dates on or before {today:%d/%m/%Y}")
            else:
                diff = relativedelta(end_date, start_date)
                duration = (diff.years * 12) + diff.months
                return job_period_past.strip(), duration
        except ValueError:
            pass
        print("Enter the experience dates as DD/MM/YYYY - DD/MM/YYYY.")
        job_period_past = get_user_input("Enter the period worked (DD/MM/YYYY - DD/MM/YYYY):")

def arrange_pass_experiences(experiences):
    return dict(
        sorted(
            experiences.items(),
            key=lambda experience: datetime.strptime(
                experience[1]["Date"].split("-", maxsplit=1)[0].strip(),
                "%d/%m/%Y",
            ),
        )
    )

def looping_past_experience(pass_experience_input):
    experiences = {}
    response = pass_experience_input.strip().lower()

    while response not in {"y", "n"}:
        response = get_user_input("Enter 'Y' to add past experience or 'N' to skip:").strip().lower()

    while response == "y":
        company_name = validate_job_string_input(
            get_user_input("Enter your company name:"), "company name"
        )
        job_title = validate_job_string_input(
            get_user_input("Enter your job title:"), "job title"
        )
        while any(existing.casefold() == job_title.strip().casefold() for existing in experiences):
            print("That job title has already been added; enter a different title.")
            job_title = validate_job_string_input(
                get_user_input("Enter a different job title:"), "job title"
            )
        dateofhiring = get_user_input("Enter the period worked (DD/MM/YYYY - DD/MM/YYYY):")
        dateofhiring, duration = validate_past_experience(dateofhiring)
        jobdiscription = get_user_input("Enter a short job description:")
        jobdiscription = validate_job_string_input(
            jobdiscription, "job description"
        )

        experiences[job_title] = {
            "company_name": company_name,
            "job_title": job_title,
            "Date": dateofhiring,
            "Duration": duration,
            "Job_Decription": jobdiscription,
        }
        response = get_user_input("Do you have another past experience? (Y/N):").strip().lower()
        while response not in {"y", "n"}:
            response = get_user_input("Enter 'Y' to add another or 'N' to finish:").strip().lower()

    return arrange_pass_experiences(experiences)


def convert_past_experience_to_internships(past_experience):
    if not isinstance(past_experience, dict):
        raise TypeError("past_experience must be a dictionary.")

    internships = {}
    for job_title, details in past_experience.items():
        if not isinstance(details, dict):
            raise ValueError(f"Past experience for {job_title!r} must be a dictionary.")

        company_name = details.get("company_name")
        role = details.get("job_title", job_title)
        date_range = details.get("Date")
        description = details.get("Job_Description", details.get("Job_Decription"))
        if not all((company_name, role, date_range, description)):
            raise ValueError(f"Past experience for {job_title!r} is missing required details.")

        try:
            start_text, end_text = date_range.split("-", maxsplit=1)
            start_date = datetime.strptime(start_text.strip(), "%d/%m/%Y")
            end_date = datetime.strptime(end_text.strip(), "%d/%m/%Y")
            if start_date > end_date:
                raise ValueError("The start date must be on or before the end date.")
            stored_duration = details.get("Duration")
            if stored_duration is None:
                difference = relativedelta(end_date, start_date)
                duration = (difference.years * 12) + difference.months
            else:
                duration = int(stored_duration)
        except (AttributeError, TypeError, ValueError) as error:
            raise ValueError(
                f"Past experience for {job_title!r} has invalid dates or duration."
            ) from error

        internships[job_title] = PastInternship(
            company_name.strip(),
            role.strip(),
            description.strip(),
            duration,
            start_date.strftime("%d/%m/%Y"),
            end_date.strftime("%d/%m/%Y"),
        )
    return internships


def Get_User_Input():
    loopmanger = True
    while loopmanger:

        #Mandatory Fields
        

        #Course of Study Input
        menu_type("CourseDisplay")
        userCourse = get_user_input("Please enter your course of study (1-45):")
        courseOfStudy = course_of_study_input(userCourse)

        # Year of Study Input
        yearOfStudy = get_user_input(
            "Enter your year of study (1-6):"
        )
        userYear = validate_Year_of_Study(yearOfStudy)

        #Available internship duration input
        internshipDuration = get_user_input(
            "Enter your available internship dates (DD/MM/YYYY - DD/MM/YYYY):"
        )
        starting_date,ending_date,Total_month = internship_duration_checker(internshipDuration)

        #skills
        Skills = continuousloopskills(get_user_input("Enter a skill:"))


        #optional Input

        #Preferred roles (e.g Marketing Assistant, Data Analyst), 
        preferedroles = continoous_Preferred_role(
            get_user_input("Enter a preferred role (or type 'exit' to skip):")
        )
        
        
    
        # Minimum expected monthly salary, 
        Minimummonthsalary = minimum_monthly_salary_checker(
            get_user_input("Enter your expected monthly salary (or type 'exit' to skip):")
        )
        
        
        # Preferred location, 

        menu_type("PreferredWorkArrangement")
        preferred_work_arrangement = preferred_work_location_looper(
            get_user_input(
                "Choose a work arrangement (1-3, or type 'exit' to choose all):"
            )
        )

        menu_type("LocationDisplay")
        preferedlocation = preferredlocation_listadder(
            get_user_input("Choose a preferred location (1-5 to choose individually, or type 'exit' to choose All):")
        )
    
        
        # Industry interests (e.g fintech, cybersecurity), 
        Industry_interest = industrial_input_list_adder(
            get_user_input("Enter an industry interest (or type 'exit' to skip):")
        )
    
        # Company preference (e.g start-up, MNCs),
        menu_type("CompanyPreference")
        Company_preference = company_preference_looper(
            get_user_input(
                "Choose a company preference (1-5, or type 'exit' to choose all):"
            )
        )

        # Past experience (e.g previous SWE internship)
        past_experience = looping_past_experience(
            get_user_input("Do you have past work experience? (Y/N):")
        )

        past_internships = convert_past_experience_to_internships(past_experience)
        user_input = StudentResume(
            Courses=courseOfStudy,
            Year_of_Study=int(userYear),
            Duration_of_internship=Total_month,
            available_internship_date=(
                f"{starting_date:%d/%m/%Y} - {ending_date:%d/%m/%Y}"
            ),
            Skills=Skills,
            Preferred_role=preferedroles,
            Minimum_monthly_salary=float(Minimummonthsalary),
            Preferred_location=preferedlocation,
            preferred_work_arrangement=preferred_work_arrangement,
            industry_interest=Industry_interest,
            company_preference=Company_preference,
            Past_internships=list(past_internships.values()),
        )
        return user_input

def check_Student_profile_add(
    student_profile: StudentProfile,
    student_resume: StudentResume,
) -> bool:
    if student_resume in student_profile.get_Student_Resume():
        display_message("Student resume was successfully added.")
        return True
    display_error("Student resume failed to add.")
    return False


def add_student_resume(studentprofile: StudentProfile) -> bool:
    if not isinstance(studentprofile, StudentProfile):
        display_error("Invalid student profile object.")
        return False

    new_resume = Get_User_Input()
    if not isinstance(new_resume, StudentResume):
        raise TypeError("Get_User_Input must return a StudentResume.")

    studentprofile.add_Student_Resume(new_resume)
    return check_Student_profile_add(studentprofile, new_resume)

#option 1 View All Profile
def view_All_profile(student_profile: StudentProfile) -> bool:
    if not isinstance(student_profile, StudentProfile):
        display_error("Invalid student profile object.")
        return False

    profile_details = student_profile.fetch_Student_Profile_details_for_user()
    for field, value in profile_details.items():
        display_message(f"{field}: {value}")
    return True

#option 2 Update profile
def getting_Student_resume(student_profile: StudentProfile,) -> list[StudentResume]:
    student_resumes = student_profile.get_Student_Resume()
    for option_number, student_resume in enumerate(student_resumes, start=1):
        details = student_resume.fetch_Student_Resume_details()
        display_message(f"{option_number}. {details}")
    return student_resumes

def update_input_validator(inputs):
    while True:
        if not Standard_Checker(inputs):
            display_error("Please enter a field option.")
        elif not Standard_number_checker("int", inputs):
            display_error("Please enter a whole number.")
        elif not Standard_numerical_range_checker(int(inputs), 1, 13):
            display_error("Choose a field from 1 to 11, 12 for all, or 13 to cancel.")
        else:
            return int(inputs)
        inputs = get_user_input(
            "Choose fields 1-11, 12 to update all, or type 13 to cancel:"
        )


def update_input_choser(
    option_number: int,
    chosen_fields: list[int],
) -> tuple[list[int], bool]:
    if option_number == 12:
        return list(range(1, len(PROFILE_UPDATE_FIELDS) + 1)), True
    if option_number == 13:
        return [], True
    if option_number in chosen_fields:
        display_error("That field is already selected.")
    else:
        chosen_fields.append(option_number)
    return chosen_fields, False


def update_input_choser_input() -> list[int]:
    chosen_fields: list[int] = []
    for option_number, field in enumerate(PROFILE_UPDATE_FIELDS, start=1):
        display_message(f"{option_number}. {field}")
    display_message("12. Update all fields")
    display_message("13. Cancel")

    while True:
        option_number = update_input_validator(
            get_user_input("Choose a field to update:")
        )
        chosen_fields, finished = update_input_choser(option_number, chosen_fields)
        if finished:
            return chosen_fields
        if not Confirming_input(get_user_input("Update another field? (Y/N):")):
            return chosen_fields


def updateprofile(
    update_input_choserlist: list[int],
    student_resume: StudentResume,
) -> StudentResume:
    if not isinstance(student_resume, StudentResume):
        raise TypeError("student_resume must be a StudentResume.")

    if 12 in update_input_choserlist:
        update_input_choserlist = list(range(1, len(PROFILE_UPDATE_FIELDS) + 1))

    updated_fields = {}
    for changed_input in update_input_choserlist:
        if (
            not Standard_number_checker("int", changed_input)
            or not Standard_numerical_range_checker(
                int(changed_input), 1, len(PROFILE_UPDATE_FIELDS)
            )
        ):
            raise ValueError(f"Unknown resume field option: {changed_input!r}")

        field_number = int(changed_input)
        if field_number == 1:
            menu_type("CourseDisplay")
            updated_fields["Courses"] = course_of_study_input(
                get_user_input("Please enter your course of study (1-45):")
            )
        elif field_number == 2:
            year_of_study = get_user_input("Enter your year of study (1-6):")
            updated_fields["Year_of_Study"] = int(
                validate_Year_of_Study(year_of_study)
            )
        elif field_number == 3:
            internship_duration = get_user_input(
                "Enter your available internship dates (DD/MM/YYYY - DD/MM/YYYY):"
            )
            starting_date, ending_date, total_months = internship_duration_checker(
                internship_duration
            )
            updated_fields["Duration_of_internship"] = total_months
            updated_fields["available_internship_date"] = (
                f"{starting_date:%d/%m/%Y} - {ending_date:%d/%m/%Y}"
            )
        elif field_number == 4:
            updated_fields["Skills"] = continuousloopskills(
                get_user_input("Enter a skill (or type 'exit' to finish):")
            )
        elif field_number == 5:
            updated_fields["Preferred_role"] = continoous_Preferred_role(
                get_user_input("Enter a preferred role (or type 'exit' to finish):")
            )
        elif field_number == 6:
            salary = minimum_monthly_salary_checker(
                get_user_input(
                    "Enter your expected monthly salary (or type 'exit' to skip):"
                )
            )
            updated_fields["Minimum_monthly_salary"] = float(salary)
        elif field_number == 7:
            menu_type("PreferredWorkArrangement")
            updated_fields["preferred_work_arrangement"] = (
                preferred_work_location_looper(
                    get_user_input(
                        "Choose a work arrangement (1-3, or type 'exit' to choose all):"
                    )
                )
            )
        elif field_number == 8:
            menu_type("LocationDisplay")
            updated_fields["Preferred_location"] = preferredlocation_listadder(
                get_user_input(
                    "Choose a preferred location (1-5, or type 'exit' to choose all):"
                )
            )
        elif field_number == 9:
            updated_fields["industry_interest"] = industrial_input_list_adder(
                get_user_input("Enter an industry interest (or type 'exit' to skip):")
            )
        elif field_number == 10:
            menu_type("CompanyPreference")
            updated_fields["company_preference"] = company_preference_looper(
                get_user_input(
                    "Choose a company preference (1-5, or type 'exit' to choose all):"
                )
            )
        elif field_number == 11:
            past_experience = looping_past_experience(
                get_user_input("Do you have past work experience? (Y/N):")
            )
            past_internships = convert_past_experience_to_internships(past_experience)
            updated_fields["Past_internships"] = list(past_internships.values())

    student_resume.update_Student_Resume(**updated_fields)
    return student_resume


def update_profile(student_profile: StudentProfile):
    if not isinstance(student_profile, StudentProfile):
        display_error("Invalid student profile object.")
        return None

    student_resumes = getting_Student_resume(student_profile)
    if not student_resumes:
        display_error("There are no resumes to update.")
        return None

    resume_number = get_user_input(
        f"Choose a resume to update (1-{len(student_resumes)}):"
    )
    while (
        not Standard_Checker(resume_number)
        or not Standard_number_checker("int", resume_number)
        or not Standard_numerical_range_checker(
            int(resume_number), 1, len(student_resumes)
        )
    ):
        display_error(f"Choose a resume number from 1 to {len(student_resumes)}.")
        resume_number = get_user_input(
            f"Choose a resume to update (1-{len(student_resumes)}):"
        )

    chosen_fields = update_input_choser_input()
    if not chosen_fields:
        display_message("Resume update cancelled.")
        return None
    return updateprofile(chosen_fields, student_resumes[int(resume_number) - 1])

def id_input(message):
    profile_id = get_user_input(message)
    while True:
        try:
            return int(profile_id)
        except ValueError:
            print("Please enter an integer")
        profile_id = get_user_input(message)

def continueorno():
    response = input("View the next listing? (Y/N): ").strip().lower()
    while response not in {"y", "n"}:
        response = input("Please enter Y or N: ").strip().lower()
    return response == "y"

def print_card(title, fields, width=60):
    print("\n" + "=" * width)
    print(f"{title:^{width}}")
    print("=" * width)
    for label, value in fields:
        if value is None or value == "":
            value = "Not specified"
        value_lines = str(value).splitlines() or ["Not specified"]
        prefix = f"{label}: "
        continuation = " " * len(prefix)
        print(textwrap.fill(
            f"{prefix}{value_lines[0]}",
            width=width,
            subsequent_indent=continuation,
        ))
        for value_line in value_lines[1:]:
            print(textwrap.fill(
                value_line,
                width=width,
                initial_indent=continuation,
                subsequent_indent=continuation,
            ))
    print("=" * width)

def display_internship(internship):
    print_card("INTERNSHIP LISTING", [
        ("ID", internship.get("job_id")),
        ("Company", internship.get("company_name")),
        ("Company Type", internship.get("company_type")),
        ("Role", internship.get("job_title")),
        ("Industry", internship.get("industry")),
        ("Relevant Course", internship.get("relevant_course")),
        ("Monthly Allowance", f"${internship['monthly_allowance']}" if internship.get("monthly_allowance") is not None else None),
        ("Work Arrangement", internship.get("work_mode")),
        ("Duration", f"{internship['duration_months']} months" if internship.get("duration_months") is not None else None),
        ("Required Skills", internship.get("required_skills")),
        ("Location", internship.get("location_district")),
        ("Description", internship.get("job_description")),
    ])


def format_feedback(feedback):
    # AI feedback is {"points": [...]}, print one point per line
    return "\n".join(f"- {point}" for point in feedback["points"])

def display_run_summary(match,recommandationtype="PAST RECOMMENDATION RUN"):
    top_job = match["jobs"][0]   # jobs are best first
    created_at = datetime.fromisoformat(match["created_at"])
    if created_at.tzinfo is None:
        created_at = created_at.replace(tzinfo=timezone.utc)
    singapore_datetime = created_at.astimezone(ZoneInfo("Asia/Singapore"))

    print_card(f"{recommandationtype} ", [
        ("Match ID", match.get("match_id")),
        ("Created (SGT)", singapore_datetime.strftime("%d %b %Y, %I:%M %p")),
        ("Top Job ID", top_job["job_id"]),
        ("Top Score", f"{top_job['score']:.1f}"),
        ("Feedback", format_feedback(match.get("overall_feedback"))),
    ])

def display_run_details(conn, match,reccomandationtype="PAST RECOMMENDATION RUN"):
    display_run_summary(match,reccomandationtype)
    #display_student_profile(match["profile"]["student_profile"])
    for rank, job in enumerate(match["jobs"], 1):
        internship = data_manager.get_internship(conn, job["job_id"])
        if internship is None:   # internship was deleted after the match was saved
            internship = {"job_title": "Internship removed", "company_name": None}
        #- JOB {job['job_id']}
        print_card(f"MATCH {rank} - JOB {job['job_id']} ", [
            ("Role", internship.get("job_title")),
            ("Company", internship.get("company_name")),
            ("Overall Score", f"{job['score']:.1f}"),
            ("Flags", format_list(job["flags"]) if job["flags"] else "None"),
        ])

def print_listing_pages(listings, display_listing):
    if not listings:
        print("No listings found")
        return

    for index, listing in enumerate(listings):
        display_listing(listing)
        if index < len(listings) - 1 and not continueorno():
            break

def list_all_Listing(conn):
    # list_matches gives every match newest first, get_match fills in the "jobs" list
    past_runs = [data_manager.get_match(conn, match["match_id"]) for match in data_manager.list_matches(conn)]
    print_listing_pages(past_runs, display_run_summary)

def get_latest_one(conn):
    latest_runs = data_manager.list_matches(conn)   # newest first, so [0] is the latest
    latest_run = data_manager.get_match(conn, latest_runs[0]["match_id"]) if latest_runs else None
    if latest_run is None:
        print("No past listing found")
        return None
    display_run_details(conn, latest_run)
    return latest_run

def view_past_listing(conn):
    run_id = id_input(
        "Enter a match ID to view (-1 for the latest match, or -2 to browse all matches,-3 to exit):"
    )
    if run_id == -1:
        get_latest_one(conn)
    elif run_id == -2:
        list_all_Listing(conn)
    elif run_id == -3:
        None
    else:
        run = data_manager.get_match(conn, run_id)   # None if the id doesn't exist
        if run is None:
            print("No past listing found with that id")
        else:
            display_run_details(conn, run)

def list_all_internship(conn, search_type):
    active_filters = {}
    
    # Show All internships
    if search_type == -1:
        internships = data_manager.list_internships(conn, limit=-1)
    
    elif search_type in INTERNSHIP_FILTER_FIELDS:
        while True:
            field = INTERNSHIP_FILTER_FIELDS[search_type]
            column = field["column"]

            search_item = get_user_input("Search: ").strip()
            active_filters[column] = search_item                
            
            for field in INTERNSHIP_FILTER_FIELDS.values():
                column = field["column"]
                if column in active_filters:
                    print(f"Current filters: {field['label']}, Item to find: {active_filters[column]}")
            if not Confirming_input(get_user_input("Add another filter? (Y/N):")):
                break

            menu_type("FilterInternships")
            while True:
                search_type = id_input(
                    "Choose another field (1-10), -1 to search, or -2 to cancel:"
                )
                if search_type == -2:
                    return None
                if search_type == -1 or search_type in INTERNSHIP_FILTER_FIELDS:
                    break
                print("Please input a number between 0 and 10, -1 to search, or -2 to cancel")
            if search_type == -1:
                break

        is_partial_search = search_type != 0
        internships = data_manager.list_internships(
            conn,
            limit=-1,
            partial= is_partial_search,
            **active_filters,
        )
        
    else:
        print("Error: something went wrong")
        return []

    print_listing_pages(internships, display_internship)
    return internships

def search_internship(conn):
    menu_type("FilterInternships")
    
    while True:
        search_type = id_input(
            "Enter a search field (0-10), -1 to view all, or -2 to exit:"
        )
        if search_type == -1 or 0 <= search_type <= 10:
            return list_all_internship(conn, search_type)
        if search_type == -2:
            return None
        else:
            print("Please input a number between 0 and 10, or -1 to view all")

#option 4 delete listing:

def delete_run_id_checker(deleted_run_id,conn):
    # Johann: valid input is -1, -2, or a match_id that exists.
    # The input is text, so check it is a number before int() (isdigit() alone rejects "-1")
    match_ids = [match["match_id"] for match in data_manager.list_matches(conn)]
    if deleted_run_id.strip().lstrip("-").isdigit()==False:
        print("Please enter a number.")
        return False
    deleted_run_id = int(deleted_run_id)
    if deleted_run_id in (-1, -2,-3) or deleted_run_id in match_ids:
        return True
    else:
        print("No past listing found with that id.")
        return False

def delete_run_id_checking_Correcter(deleted_run_id,conn):
    is_valid = delete_run_id_checker(deleted_run_id,conn)
    while not is_valid:
        deleted_run_id = get_user_input("Enter the match ID to delete (-1 for the latest, -2 to delete all,-3 to exit) :")
        is_valid = delete_run_id_checker(deleted_run_id,conn)
    return int(deleted_run_id)

def deleteListing(conn): 
    past_runs = data_manager.list_matches(conn)   # newest first
    if not past_runs:
        print("No past listing found")
        return None
    list_all_Listing(conn)
    deleted_run_id = delete_run_id_checking_Correcter(get_user_input("Enter the match ID to delete (-1 for the latest, -2 to delete all,-3 to exit):"),conn)
    if deleted_run_id == -3:
        return deleted_run_id
    elif deleted_run_id == -1:
        to_delete = [past_runs[0]["match_id"]]
    elif deleted_run_id == -2:
        to_delete = [match["match_id"] for match in past_runs]
    else:
        to_delete = [deleted_run_id]
    if Confirming_input(get_user_input(f"Delete {len(to_delete)} listing(s)? This cannot be undone (Y/N):")):
        for match_id in to_delete:
            data_manager.delete_match(conn, match_id)   # also deletes that match's profile snapshot
        print(f"Deleted {len(to_delete)} listing(s).")
    else:
        print("Nothing was deleted.")
    return deleted_run_id


def _student_resume_to_profile(resume: StudentResume) -> dict:
    details = resume.fetch_Student_Resume_details()
    past_experience = {}
    for internship in details["Past_internships"]:
        role = internship["role"]
        company = internship["company_name"]
        key = role
        suffix = 2
        while key in past_experience:
            key = f"{role} ({company} {suffix})"
            suffix += 1
        past_experience[key] = {
            "company_name": company,
            "Date": f"{internship['start_date']} - {internship['end_date']}",
            "Duration": internship["duration"],
            "Job_Decription": internship["description"],
        }

    return {
        "course_of_study": details["Courses"],
        "year_of_study": str(details["Year_of_Study"]),
        "duration": details["Duration_of_internship"],
        "available_internship_dates": details["available_internship_date"],
        "skills": details["Skills"],
        "preferred_roles": details["Preferred_role"],
        "minimum_monthly_salary": details["Minimum_monthly_salary"],
        "preferred_work_arrangement": details["preferred_work_arrangement"],
        "preferred_location": details["Preferred_location"],
        "industry_interest": details["industry_interest"],
        "company_preference": details["company_preference"],
        "past_experience": past_experience,
    }


def _student_profile_to_match_input(student_profile: StudentProfile) -> dict:
    if not isinstance(student_profile, StudentProfile):
        raise TypeError("Expected a StudentProfile.")
    resumes = student_profile.get_Student_Resume()
    if not resumes:
        raise ValueError("Student profile has no resume to match.")
    return {"student_profile": _student_resume_to_profile(resumes[-1])}


#option 6 find internship matches:
def find_internship_matches(conn, studentprofile):
    print("Finding your top 5 internships. This can take a minute...")
    try:
        # DB NOTE (Johann): runs the AI, scores + flags each job, saves it, returns the new match_id
        match_input = _student_profile_to_match_input(studentprofile)
        match_id = logic_manager.find_matches(conn, match_input)
    except Exception as error:
        # e.g. no GEMINI_API_KEY, no internet, or the AI gave a bad answer: go back to the menu
        print(f"Could not find matches: {error}")
        return None
    print(f"Saved as match {match_id}. You can view it again with option 3.")
    display_run_details(conn, data_manager.get_match(conn, match_id),"Recommandation Run Result")
    return match_id

#Json and database linking 
def load_from_database(db, user_id, student_profile: StudentProfile):
    resume = StudentResume.load(db, user_id)
    if resume is not None:
        student_profile.add_Student_Resume(resume)
    return student_profile

def Save_to_database(db, user_id, student_profile: StudentProfile) -> bool:
    """Persist the latest in-memory resume as the user's current resume."""
    if not isinstance(student_profile, StudentProfile):
        display_error("Invalid student profile object.")
        return False
    resumes = student_profile.get_Student_Resume()
    if not resumes:
        display_error("Student profile has no resume to save.")
        return False
    resume = resumes[-1]
    if not isinstance(resume, StudentResume):
        raise TypeError("Student profile contains an invalid resume object.")
    resume.save(db, user_id)
    display_message("Student resume saved.")
    return True
#menu function

def menu_validator(inputs):
    while not Standard_Checker(inputs) or  not Standard_number_checker("int",inputs) or not Standard_numerical_range_checker(int(inputs),1,7):
        if not Standard_Checker(inputs):
            display_error("Incorrect Input")
            inputs = get_user_input("Enter your input")
        elif not Standard_number_checker("int",inputs):
            display_error("Incorrect Input , not a integer")
            inputs = get_user_input("Enter your input")
        elif not Standard_numerical_range_checker(int(inputs),1,7):
            display_error("Incorrect Input,Please Enter between the option 1 to 7")
            inputs = get_user_input("Enter your input")
    return int(inputs)

def user_input_process(inputs:int,db,conn,userid,Student_profile:StudentProfile):
    match inputs:
        case 1:
            view_All_profile(Student_profile)
            Save_to_database(db,userid,Student_profile)
            return False
        case 2:
            update_profile(Student_profile)
            Save_to_database(db,userid,Student_profile)
            return False
        case 3:
            view_past_listing(conn)
            return False
        case 4:
            deleteListing(conn)
            return False
        case 5:
            search_internship(conn)
            return False
        case 6:
            find_internship_matches(conn, Student_profile)
            return False
        case 7:
            display_message("Goodbye and have a good day .")
            Save_to_database(db,userid,Student_profile)
            return True

def menu_input(Student_profile,db,conn,user_id):
    user_input = ""
    menu_type("Main_Menu")
    looper = False 
    while not looper:
        user_input = get_user_input("Enter your input")
        user_input = menu_validator(user_input)
        looper = user_input_process(user_input,db,conn,user_id,Student_profile)
    return looper

def Student_profile_menu_decide(Student_profile,conn,db,user_id):
    if not check_student_profile(Student_profile) or not check_student_profile_details(Student_profile):
        return display_error("Please Check Your Student Profile")
    if not check_student_profile_resume(Student_profile):
        menu_type("First_Resume")
        if not add_student_resume(Student_profile):
            return False
        return menu_input(Student_profile,db,conn,user_id)
    else:
        return menu_input(Student_profile,db,conn,user_id)

def main(db,conn):
    menu_type("login")
    login_result = login_loop(db)
    if login_result is None:
        return None
    student_profile, user_id = login_result
    return Student_profile_menu_decide(student_profile, conn,db,user_id)