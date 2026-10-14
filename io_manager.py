import os
import json
from pathlib import Path
import re
from datetime import datetime, timezone
from dateutil.relativedelta import relativedelta
import textwrap
from zoneinfo import ZoneInfo

import data_manager
import logic_manager   # logic_manager.find_matches runs the AI and saves

STUDENT_PROFILE_JSON = Path(
    os.getenv(
        "STUDENT_PROFILE_JSON",
        str(Path(__file__).resolve().parent / "data" / "student_profile.json"),
    )
)

consoleWidth_60 = 60
consoleWidth_55 = 55
profileFieldWidth = 28
courseCount = 0

def prompt_input(message):
    print("\n" + "-" * consoleWidth_60)
    return input(f"{message.strip()}\n> ")

def display_message(*values, sep=" ", end="\n"):
    print(*values, sep=sep, end=end)

def display_error(message):
    print(f"Error: {message}")

#Menu output styles
def menuDisplayType(typeofmenu,studentprofile={}):
    
    def print_heading(title):
        print("\n" + "=" * consoleWidth_60)
        print(f"{title:^{consoleWidth_60}}")
        print("=" * consoleWidth_60)

    match typeofmenu:
        case "Starting":
            print_heading("INTERN LINK")
            print("Welcome to Intern Link.")
            print("Please enter your student profile to get started.")
            print("=" * consoleWidth_60)

        case "SecondTime":
            print_heading("INTERN LINK")
            print("  1. Update profile")
            print("  2. View past listings")
            print("  3. Delete History")
            print("  4. Search for internships")
            print("  5. Find internship matches (AI)")
            print("  6. Exit")
            print("=" * consoleWidth_60)

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
            singapore_areas_list = ["North","East","South","West","Central"]
            print_heading("PREFERRED LOCATIONS")
            for number, area in enumerate(singapore_areas_list, 1):
                print(f"  {number:>2}. {area}")
            print("=" * consoleWidth_60)

        case "PreferredWorkArrangement":
            Preferred_word_arragement = ["On-site","Hybrid","No Preference"]
            print_heading("PREFERRED WORK ARRANGEMENT")
            for number, word_arrangement in enumerate(Preferred_word_arragement, 1):
                print(f"  {number}. {word_arrangement}")

        case "CompanyPreference":
            company_preferences = [
                "Start-ups",
                "Multi-National Corporations (MNCs)",
                "Government",
                "Statutory Boards",
                "Small-to-Medium Enterprises (SMEs)" ,
            ]
            print_heading("COMPANY PREFERENCES")
            for number, preference in enumerate(company_preferences, 1):
                print(f"  {number:>2}. {preference}")
            print("=" * consoleWidth_60)

        case "UpdateDisplay":
            print_heading("YOUR STUDENT PROFILE")
            display_student_profile(studentprofile)
        
        case "FilterInternships":
            internship_fields_filterable = [
                "Company Name",
                "Company Type",
                "Industry",
                "Job Title",
                "Relevant Course",
                "Monthly Allowance",
                "Work Mode",
                "Duration Months",
                "Required Skills",
                "Location"
                ]

            print_heading("FILTER OPTIONS")
            for number, filter in enumerate(internship_fields_filterable, 1):
                print(f"  {number:>2}. {filter}")
            print("=" * consoleWidth_60)
            
        case _:
            print(f"Unknown menu type: {typeofmenu}")

# Formating for CLI display
def format_list(item):
    if isinstance(item, list) and item:
        return ", ".join(item)
    if isinstance(item, str) and item.strip():
        return item
    return "None specified"

# 2. Define a function to display the profile nicely
def display_student_profile(profile):
    raw_year = str(profile.get("year_of_study", "")).split(",", maxsplit=1)[0].strip()
    formatted_year = f"Year {raw_year}" if raw_year.isdigit() else raw_year

    past_exp = profile.get("past_experience", {})
    work_arrangement = profile.get("preferred_work_arrangement", "N/A")
    if (
        isinstance(work_arrangement, list)
        and {str(value).casefold() for value in work_arrangement}
        == {"on-site", "hybrid"}
    ):
        work_arrangement = "No Preference"
    else:
        work_arrangement = format_list(work_arrangement)


    duration = profile.get("duration")
    internship_dates = profile.get("available_internship_dates")
    if internship_dates and duration is not None:
        duration_text = f"{internship_dates} ({duration} months)"
    elif internship_dates:
        duration_text = internship_dates
    elif duration is not None:
        duration_text = f"{duration} months (date range not set)"
    else:
        duration_text = "N/A"

    width = 60
    content_width = width - 4

    def print_line(text=""):
        print(f"| {text:<{content_width}} |")

    def print_wrapped(text, indent="  "):
        lines = textwrap.wrap(
            str(text),
            width=content_width,
            initial_indent=indent,
            subsequent_indent=indent,
            break_on_hyphens=False,
        ) or [indent.rstrip()]
        for line in lines:
            print_line(line)

    def print_field(number, label, value):
        prefix = f"  {number}. {label}: "
        value = str(value) if value not in (None, "") else "Not specified"
        lines = textwrap.wrap(
            value,
            width=max(1, content_width - len(prefix)),
            subsequent_indent=" " * len(prefix),
            break_on_hyphens=False,
        ) or ["Not specified"]
        print_line(prefix + lines[0])
        for line in lines[1:]:
            print_line(line)

    def print_list_field(number, label, values):
        print_line(f"  {number}. {label}:")
        if isinstance(values, list):
            items = [str(value) for value in values if str(value).strip()]
        elif isinstance(values, str) and values.strip():
            items = [values]
        else:
            items = []
        if items:
            for item in items:
                print_wrapped(f"- {item}", indent="     ")
        else:
            print_wrapped("None specified", indent="     ")

    border = "+" + "-" * (width - 2) + "+"
    print("\n" + border)
    print_line("STUDENT PROFILE".center(content_width))
    print(border)

    print_line("ACADEMIC & AVAILABILITY")
    print_field(1, "Course", profile.get("course_of_study"))
    print_field(2, "Year", formatted_year)
    print_field(3, "Internship", duration_text)

    print(border)
    print_line("SKILLS & ROLES")
    print_list_field(4, "Skills", profile.get("skills", []))
    print_list_field(5, "Preferred roles", profile.get("preferred_roles", []))

    print(border)
    print_line("PREFERENCES")
    salary = profile.get("minimum_monthly_salary")
    salary_text = f"${salary}" if salary not in (None, "") else "Not specified"
    print_field(6, "Minimum salary", salary_text)
    print_field(7, "Work arrangement", work_arrangement)
    print_field(8, "Location", format_list(profile.get("preferred_location", [])))
    print_field(9, "Industry", format_list(profile.get("industry_interest", [])))
    print_list_field(10, "Company type", profile.get("company_preference", []))

    print(border)
    print_line("PAST EXPERIENCE")
    if isinstance(past_exp, dict) and past_exp:
        for job_title, details in past_exp.items():
            if not isinstance(details, dict):
                details = {}
            print_wrapped(f"- {job_title}")
            period = details.get("Date")
            if period:
                print_wrapped(f"Period: {period}", indent="      ")
            description = details.get(
                "Job_Decription", details.get("Job_Description")
            )
            if description:
                print_wrapped(f"Description: {description}", indent="      ")
    else:
        print_wrapped("None recorded")
    print(border + "\n")


#Input validation/correction functions
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
    return courses[course_of_study_id-1]

def validate_course_of_study(course):

    if not course:
        print("Invalid input. Please enter a number corresponding to your course of study.")
        return False
    elif course.isdigit()!= True:
        print("Invalid input. Please enter a number corresponding to your course of study.")
        return False 
    elif int(course) < 1 or int(course) > courseCount:
        print(f"Invalid input. Please enter a number between 1 and {courseCount}.")
        return False
    return True

def course_of_study_input(courseofStudy):
    course_of_study_words(10)
    is_valid = validate_course_of_study(courseofStudy)
    while is_valid == False:
        courseofStudy = prompt_input("Please enter your course of study (1-45):")
        is_valid = validate_course_of_study(courseofStudy)
    
    return course_of_study_words(int(courseofStudy))

def validate_Year_of_Study(year):
    match = re.fullmatch(r"(?:Year\s*)?([1-6])", year.strip(), re.IGNORECASE)
    while match is None:
        print("Invalid input. Please enter a year between 1 and 6.")
        year = prompt_input("Please enter your year of study (1-6):")
        match = re.fullmatch(r"(?:Year\s*)?([1-6])", year.strip(), re.IGNORECASE)
    return match.group(1)

def check_Internship_Duration_format(internshipDuration):
    if not internshipDuration :
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
        internshipDuration = prompt_input("Enter your available internship dates (DD/MM/YYYY - DD/MM/YYYY):")
        starting_date,ending_date,Total_month,is_valid = check_Internship_Duration_format(internshipDuration)
    return starting_date,ending_date,Total_month

def Confirming_input(confirmation):
    while confirmation.strip().casefold() not in {"y", "n"}:
        confirmation = prompt_input("Please enter only Y or N:")
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
        if not skillsinput:
            print("Invalid input. Please try again.")
        elif skillsinput.isdigit():
            print("You entered a number.")
            if Confirming_input(prompt_input("Is this correct? (Y/N):")):
                return skillsinput
        elif len(skillsinput) == 1:
            print("You entered a single character.")
            if Confirming_input(prompt_input("Is this correct? (Y/N):")):
                return skillsinput
        else:
            return skillsinput

        skillsinput = prompt_input("Enter a skill (or type 'exit' to finish):")

def continuousloopskills(skillsinput):
    skillslist = []
    while True:
        skillinput = validate_skill(skillsinput)
        skillinput = skillinput.strip()
        if skillinput.casefold() == "exit":
            return skillslist
        append_unique_value(skillslist, skillinput, "Skill")
        skillsinput = prompt_input("Enter another skill (or type 'exit' to finish):")

def validate_Preferred_role(preferred_role):
    areusure = True 
    if not preferred_role:
        areusure = True
        print("Please enter a value.")
        return areusure
    elif preferred_role.isdigit() == True:
        print("You entered a number.")
        areusure = Confirming_input(prompt_input("Is this preferred role correct? (Y/N):"))
        return areusure
    elif len(preferred_role) == 1:
        print("You entered a single character. Is this correct?")
        areusure = Confirming_input(prompt_input("Is this preferred role correct? (Y/N):"))
        return areusure
    else:
        return areusure 

def checking_Preferred_role_input(Preferred_role):
    is_valid = validate_Preferred_role(Preferred_role)
    while is_valid == False:
        Preferred_role = prompt_input("Enter a preferred role (or type 'exit' to finish):")
        is_valid = validate_Preferred_role(Preferred_role)
    return is_valid,Preferred_role

def continoous_Preferred_role(Preferred_role):
    Preferred_rolelist = []
    is_valid,Preferred_role = checking_Preferred_role_input(Preferred_role)
    if Preferred_role.strip().lower() == "exit":
        return Preferred_rolelist
    append_unique_value(Preferred_rolelist, Preferred_role, "Preferred role")
    while True:
        Preferred_role = prompt_input("Enter another preferred role (or type 'exit' to finish):")
        _, Preferred_role = checking_Preferred_role_input(Preferred_role)
        if Preferred_role.lower().strip() == "exit":
            return Preferred_rolelist
        append_unique_value(Preferred_rolelist, Preferred_role, "Preferred role")

def validating_minimum_monthly_salary(minimum_month_salary):
    if not minimum_month_salary:
        print("Please enter a value.")
        return False
    elif minimum_month_salary.lower().strip() == "exit":
        return True
    elif minimum_month_salary.isdigit() ==False:
        print("Please enter a number.")
        return False
    minimum_month_salary = float(minimum_month_salary)
    if minimum_month_salary<0 :
        print("The number cannot be negative. Please input again")
        return False
    elif minimum_month_salary == 0:
        print("The value you entered is 0. Please input again.")
        return False
    elif minimum_month_salary>10000:
        print("The value you entered is greater than 10,000. Please input again")
        return False
    else:
        return True

def minimum_monthly_salary_checker(minimum_monthly_salary):
    is_valid = validating_minimum_monthly_salary(minimum_monthly_salary)
    while is_valid == False:
        minimum_monthly_salary = prompt_input("Enter your expected monthly salary (or type 'exit' to skip):")
        is_valid = validating_minimum_monthly_salary(minimum_monthly_salary)
    if minimum_monthly_salary.isdigit() == True:
        return f"{float(minimum_monthly_salary):.2f}"
    else:
        return 0.00

def validating_preferred_work_location(preferred_work_locations):
    if not preferred_work_locations:
        print("Invalid value.")
        return False
    elif preferred_work_locations.lower().strip() == "exit":
        return True
    elif preferred_work_locations.isdigit() == False:
        print("Please enter a number.")
        return False
    preferred_work_locations = int(preferred_work_locations)
    if preferred_work_locations<1 or preferred_work_locations>3:
        print("Please enter a valid number.")
        return False
    else:
        return True

def validating_perferred_work_location_input(preferred_work_locations):
    is_valid = validating_preferred_work_location(preferred_work_locations)
    while is_valid == False:
        preferred_work_locations = prompt_input(
            "Enter a preferred work arrangement (1-3, or type 'exit' to finish):"
        )
        is_valid = validating_preferred_work_location(preferred_work_locations)
    return preferred_work_locations.strip(), is_valid

def num_to_string_work_location(preferred_work_arrangement):
    Preferred_word_arragement_list = ["On-site","Hybrid","No Preference"]
    preferred_work_arrangement = int(preferred_work_arrangement)
    if preferred_work_arrangement == 4:
            return "4"
    return Preferred_word_arragement_list[(preferred_work_arrangement-1)]

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
        arrangement = arrangements[int(response) - 1]
        append_unique_value(selected, arrangement, "Work arrangement")
        response = prompt_input(
            "Choose another work arrangement (1-3, or type 'exit' to finish):"
        )

def pre_work_location_input_validation(preferred_work_locations):
    preferred_work_locations,isvalid = validating_perferred_work_location_input(preferred_work_locations)
    if isvalid != False:
        preferred_work_locations = int(preferred_work_locations)
        preferred_work_locations = num_to_string_work_location(preferred_work_locations)
    return preferred_work_locations

def validating_preferred_locations(preferredlocations):
    if not preferredlocations:
        print("Invalid value.")
        return False
    elif  preferredlocations.lower().strip() == "exit":
        return True
    elif preferredlocations.isdigit() == False:
        print("Please enter a number.")
        return False
    preferredlocations = int(preferredlocations)
    if preferredlocations<1 or preferredlocations>5:
        print("Please enter a valid number.")
        return False
    else:
        
        return True

def validating_perferred_location_input(preferredlocations):
    is_valid = validating_preferred_locations(preferredlocations)
    while is_valid == False:
        preferredlocations = prompt_input("Choose a preferred location (1-5, or type 'exit' to finish):")
        is_valid = validating_preferred_locations(preferredlocations)
    return preferredlocations

def preferredlocations_number_to_string(preferredlocationnumber):
    singapore_areas_list = ["North","East","South","West","Central"]
    preferredlocationnumber = int(preferredlocationnumber)
    return singapore_areas_list[(preferredlocationnumber-1)]

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
        response = prompt_input(
            "Choose another preferred location (1-5, or type 'exit' to finish):"
        )
        
def validate_Industry_interest(Industrial_intrest):
    if not Industrial_intrest:
        print("Please enter a valid response.")
        return False
    elif Industrial_intrest.strip().lower() == "exit":
        return True
    elif Industrial_intrest.isdigit()==True:
        print("You entered a number.")
        return Confirming_input(prompt_input("Is this industry interest correct? (Y/N):"))
    elif len(Industrial_intrest)==1:
        print("You entered a single character.")
        return Confirming_input(prompt_input("Is this industry interest correct? (Y/N):"))
    return True

def Industrial_input_checker(industrial_interest):
    is_valid = validate_Industry_interest(industrial_interest)
    while is_valid == False:
        industrial_interest = prompt_input("Enter an industry interest (or type 'exit' to finish):")
        is_valid = validate_Industry_interest(industrial_interest)
    return industrial_interest,is_valid

def industrial_input_list_adder(industrial_interest):
    industrial_interestlist = []
    while True:
        industrial_interest, _ = Industrial_input_checker(industrial_interest)
        if industrial_interest.strip().casefold() == "exit":
            return industrial_interestlist
        append_unique_value(industrial_interestlist, industrial_interest, "Industry interest")
        industrial_interest = prompt_input("Enter another industry interest (or type 'exit' to finish):")

def validate_company_preference(company_perference):
    if not company_perference:
        print("Please enter a value.")
        return False
    elif company_perference.lower().strip() == "exit":
        return True
    elif company_perference.isdigit() == False:
        print("Please enter a number.")
        return False
    company_perference = int(company_perference)
    if not 1 <= company_perference <= 5:
        print("Please enter a number between 1 and 5.")
        return False
    return True

def company_preference_number_to_String(company_preference):
    company_preferenceslist = [
    "Start-ups",
    "Multi-National Corporations (MNCs)",
    "Government",
    "Statutory Boards",
    "Small-to-Medium Enterprises (SMEs)"
]
    return company_preferenceslist[int(company_preference)-1] 

def company_preference_checker(company_preference):
    is_valid = validate_company_preference(company_preference)
    while is_valid == False:
        company_preference = prompt_input("Choose a company preference (1-5, or type 'exit' to skip):")
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
        print("\nSelected locations:", ", ".join(selected) or "None")
        response = prompt_input(
            "Choose another company preference (1-5, or type 'exit' to finish):"
        )

# Check if user inputs an empty string for job_title and job_discription
def validate_job_string_input(job_string, variable_name):
    while not job_string.strip():
        print(f"Please enter a value for {variable_name}.")
        job_string = prompt_input(f"Enter {variable_name}:")
    return job_string.strip()

def validate_past_experience(job_period_past):
    
    today_date = datetime.combine(datetime.today(), datetime.min.time())
    formated_today = today_date.strftime("%d/%m/%Y")

    while True:
        try:
            start_text, end_text = job_period_past.split("-", maxsplit=1)
            start_date = datetime.strptime(start_text.strip(), "%d/%m/%Y")
            end_date = datetime.strptime(end_text.strip(), "%d/%m/%Y")
            if start_date > end_date:
                print("Start date is a date after end date")
            elif start_date > today_date or end_date > today_date:
                print(f"Please set a date before {formated_today}")
            else:
                break
        except ValueError:
            pass
        print("Enter the experience dates as DD/MM/YYYY - DD/MM/YYYY.")
        job_period_past = prompt_input("Enter the period worked (DD/MM/YYYY - DD/MM/YYYY):")
            
    return job_period_past.strip()

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
        response = prompt_input("Enter 'Y' to add past experience or 'N' to skip:").strip().lower()

    while response == "y":
        job_title = validate_job_string_input(
            prompt_input("Enter your job title:"), "job title"
        )
        while any(existing.casefold() == job_title.strip().casefold() for existing in experiences):
            print("That job title has already been added; enter a different title.")
            job_title = validate_job_string_input(
                prompt_input("Enter a different job title:"), "job title"
            )
        dateofhiring = prompt_input("Enter the period worked (DD/MM/YYYY - DD/MM/YYYY):")
        dateofhiring = validate_past_experience(dateofhiring)
        jobdiscription = prompt_input("Enter a short job description:")
        jobdiscription = validate_job_string_input(
            jobdiscription, "job description"
        )

        experiences[job_title] = {
            "Date": dateofhiring,
            "Job_Decription": jobdiscription,
        }
        response = prompt_input("Do you have another past experience? (Y/N):").strip().lower()
        while response not in {"y", "n"}:
            response = prompt_input("Enter 'Y' to add another or 'N' to finish:").strip().lower()

    return arrange_pass_experiences(experiences)


def Get_User_Input():
    loopmanger = True
    while loopmanger:

        #Mandatory Fields
        

        #Course of Study Input
        menuDisplayType("CourseDisplay")
        userCourse = prompt_input("Please enter your course of study (1-45):")
        courseOfStudy = course_of_study_input(userCourse)

        # Year of Study Input
        yearOfStudy = prompt_input(
            "Enter your year of study (1-6):"
        )
        userYear = validate_Year_of_Study(yearOfStudy)

        #Available internship duration input
        internshipDuration = prompt_input(
            "Enter your available internship dates (DD/MM/YYYY - DD/MM/YYYY):"
        )
        starting_date,ending_date,Total_month = internship_duration_checker(internshipDuration)

        #skills
        Skills = continuousloopskills(prompt_input("Enter a skill:"))


        #optional Input

        #Preferred roles (e.g Marketing Assistant, Data Analyst), 
        preferedroles = continoous_Preferred_role(
            prompt_input("Enter a preferred role (or type 'exit' to skip):")
        )
        
        
    
        # Minimum expected monthly salary, 
        Minimummonthsalary = minimum_monthly_salary_checker(
            prompt_input("Enter your expected monthly salary (or type 'exit' to skip):")
        )
        
        
        # Preferred location, 

        menuDisplayType("PreferredWorkArrangement")
        preferred_work_arrangement = preferred_work_location_looper(
            prompt_input(
                "Choose a work arrangement (1-3, or type 'exit' to choose all):"
            )
        )

        menuDisplayType("LocationDisplay")
        preferedlocation = preferredlocation_listadder(
            prompt_input("Choose a preferred location (1-5 to choose individually, or type 'exit' to choose All):")
        )
    
        
        # Industry interests (e.g fintech, cybersecurity), 
        Industry_interest = industrial_input_list_adder(
            prompt_input("Enter an industry interest (or type 'exit' to skip):")
        )
    
        # Company preference (e.g start-up, MNCs),
        menuDisplayType("CompanyPreference") 
        Company_preference = company_preference_looper(
            prompt_input(
                "Choose a company preference (1-5, or type 'exit' to choose all):"
            )
        )

        # Past experience (e.g previous SWE internship)
        past_experience = looping_past_experience(
            prompt_input("Do you have past work experience? (Y/N):")
        )

        user_input = {
            "student_profile":{
                "course_of_study":courseOfStudy,
                "year_of_study":userYear,
                "duration":Total_month,
                "available_internship_dates":(
                    f"{starting_date:%d/%m/%Y} - {ending_date:%d/%m/%Y}"
                ),
                "skills":Skills,
                "preferred_roles":preferedroles,
                "minimum_monthly_salary":Minimummonthsalary,
                "preferred_work_arrangement":preferred_work_arrangement,
                "preferred_location":preferedlocation,
                "industry_interest":Industry_interest,
                "company_preference":Company_preference,
                "past_experience":past_experience,
            }
        }
        return user_input

# loading json file
def read_student_profile_json():
    STUDENT_PROFILE_JSON.parent.mkdir(parents=True, exist_ok=True)

    with open(STUDENT_PROFILE_JSON, "r", encoding="utf-8") as file:
        contents = file.read()

    if not contents.strip():
        print("Student profile file is empty; starting with a new profile.")
        return {}

    try:
        student_profile = json.loads(contents)
    except json.JSONDecodeError as error:
        raise ValueError(
            f"Invalid JSON in student profile {STUDENT_PROFILE_JSON}: {error}"
        ) from error

    print("Student profile loaded successfully")
    return student_profile

def create_a_student_profile_json():
    STUDENT_PROFILE_JSON.parent.mkdir(parents=True, exist_ok=True)
    if not STUDENT_PROFILE_JSON.is_file():
        with open(STUDENT_PROFILE_JSON, "w", encoding="utf-8") as file:
            json.dump({}, file)


# JSON REFERENCE
def get_student_profile_json():
    try:
        student_profile = read_student_profile_json()
    except FileNotFoundError:
        print("Student profile file not found; creating a new profile")
        create_a_student_profile_json()
        student_profile = read_student_profile_json()
        print("Student profile created successfully")
    return student_profile

def add_student_profile_json(student_profile):
    STUDENT_PROFILE_JSON.parent.mkdir(parents=True, exist_ok=True)
    with open(STUDENT_PROFILE_JSON, "w", encoding="utf-8") as file:
        json.dump(student_profile, file, indent=4)

def update_student_profile_json(studentprofile):
    if not isinstance(studentprofile, dict) or not isinstance(
        studentprofile.get("student_profile"), dict
    ):
        raise ValueError("studentprofile must contain a student_profile dictionary")

    selected_fields = update_chooser()
    if not selected_fields:
        print("Profile update cancelled; no changes were made.")
        return studentprofile

    updated_studentprofile = studentprofile.copy()
    updated_studentprofile["student_profile"] = update_Student_profile(
        selected_fields,
        studentprofile["student_profile"],
    )
    add_student_profile_json(updated_studentprofile)
    print("Student profile updated successfully.")
    return updated_studentprofile

def menu_numeric(student_profile):
    if not student_profile:
        return "1001"
    else:
        return "1002"

def menuprinter(student_profile):
    if not student_profile:
        # User to create profile student_profile.json is empty
        menuDisplayType("Starting")
        return "1001"
    else:
        # Use latest user profile
        menuDisplayType("SecondTime")
        return "1002"

def menu_function_caller_first_time():
    user_input = Get_User_Input()
    add_student_profile_json(user_input)
    student_profile = get_student_profile_json()
    return student_profile

def validater_chooser_spilt(update_chooser):
    return [choice.strip() for choice in update_chooser.split(",")]

def validate_update_choose(update_chooser_list):
    if not update_chooser_list:
        return False
    for update_chooser in update_chooser_list:
        if not update_chooser.isdigit():
            print("Please enter field numbers separated by commas.")
            return False
        if not 1 <= int(update_chooser) <= 12:
            print("Choose a field number from 1 to 11, or 12 to update all.")
            return False
    if "12" in update_chooser_list and len(update_chooser_list) > 1:
        print("Choose 12 by itself to update all fields.")
        return False
    return True

def loop_correct_update_chooer(input_update_chooser):
    while True:
        if input_update_chooser.strip().casefold() == "exit":
            return []
        list_chooser = validater_chooser_spilt(input_update_chooser)
        if validate_update_choose(list_chooser):
            if "12" in list_chooser:
                return [str(field_number) for field_number in range(1, 12)]
            return list(dict.fromkeys(list_chooser))
        input_update_chooser = prompt_input(
            "Choose fields 1-11, 12 to update all, or type 'exit' to cancel:"
        )

def update_Student_profile(input_chooser_update,student_profile):
    updated_profile = student_profile.copy()
    for changedinput in input_chooser_update:
        field_number = int(changedinput)
        if field_number == 1:
            menuDisplayType("CourseDisplay")
            userCourse = prompt_input("Please enter your course of study (1-45):")
            updated_profile["course_of_study"] = course_of_study_input(userCourse)
        elif field_number == 2:
            year_of_study = prompt_input("Enter your year of study (1-6):")
            updated_profile["year_of_study"] = validate_Year_of_Study(year_of_study)
        elif field_number == 3:
            internship_duration = prompt_input(
                "Enter your available internship dates (DD/MM/YYYY - DD/MM/YYYY):"
            )
            starting_date, ending_date, total_months = internship_duration_checker(
                internship_duration
            )
            updated_profile["duration"] = total_months
            updated_profile["available_internship_dates"] = (
                f"{starting_date:%d/%m/%Y} - {ending_date:%d/%m/%Y}"
            )
        elif field_number == 4:
            updated_profile["skills"] = continuousloopskills(
                prompt_input("Enter a skill (or type 'exit' to finish):")
            )
        elif field_number == 5:
            updated_profile["preferred_roles"] = continoous_Preferred_role(
                prompt_input("Enter a preferred role (or type 'exit' to finish):")
            )
        elif field_number == 6:
            updated_profile["minimum_monthly_salary"] = minimum_monthly_salary_checker(
                prompt_input("Enter your expected monthly salary (or type 'exit' to skip):")
            )
        elif field_number == 7:
            menuDisplayType("PreferredWorkArrangement")
            updated_profile["preferred_work_arrangement"] = preferred_work_location_looper(
                prompt_input(
                    "Choose a work arrangement (1-3, or type 'exit' to choose all):"
                )
            )
        elif field_number == 8:
            menuDisplayType("LocationDisplay")
            updated_profile["preferred_location"] = preferredlocation_listadder(
                prompt_input(
                    "Choose a preferred location (1-5, or type 'exit' to choose all):"
                )
            )
        elif field_number == 9:
            updated_profile["industry_interest"] = industrial_input_list_adder(
                prompt_input("Enter an industry interest (or type 'exit' to skip):")
            )
        elif field_number == 10:
            menuDisplayType("CompanyPreference")
            updated_profile["company_preference"] = company_preference_looper(
                prompt_input(
                    "Choose a company preference (1-5, or type 'exit' to choose all):"
                )
            )
        elif field_number == 11:
            updated_profile["past_experience"] = looping_past_experience(
                prompt_input("Do you have past work experience? (Y/N):")
            )
    return updated_profile


def update_chooser():
    return loop_correct_update_chooer(
        prompt_input(
            "Enter field numbers separated by commas (1-11), 12 to update all, "
            "or type 'exit' to cancel:"
        )
    )



def checking_user_update(studentprofile):
    if Confirming_input(prompt_input("Would you like to update your profile? (Y/N):")):
        updated_student_profile = update_student_profile_json(studentprofile)
        return updated_student_profile
    else:
        print("Returning back to the mainpage")
        return studentprofile
        
def update_user_menu(studentprofile):
    if not isinstance(studentprofile, dict) or not isinstance(
        studentprofile.get("student_profile"), dict
        ):
        raise ValueError("studentprofile must contain a student_profile dictionary")
    
    profile = studentprofile["student_profile"]
    print("Current student profile:")
    menuDisplayType("UpdateDisplay",profile)
    return checking_user_update(studentprofile)


def input_validator_option(functionnumber):
    if functionnumber.isdigit()==False:
        print("Your input is not an integer. Please try again.")
        return False
    functionnumber = int(functionnumber)
    if(functionnumber<1):
        print("Your input is incorrect please Try again")
        return False
    elif (functionnumber >6):
        print("Your input is incorrect please Try again")
        return False
    return True

def inputlooper(functionnumber):
    Trueorfalse = input_validator_option(functionnumber)
    while not Trueorfalse :
        functionnumber = prompt_input("Choose an option (1-6):")
        Trueorfalse = input_validator_option(functionnumber)
    return int(functionnumber)

# Option 2 and 3: simple lookups by id
def id_input(message):
    profile_id = prompt_input(message)
    while True:
        try:
            return int(profile_id)
        except ValueError:
            print("Please enter an integer")
        profile_id = prompt_input(message)

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
    filter_columns = {
        1: "company_name",
        2: "company_type",
        3: "industry",
        4: "job_title",
        5: "relevant_course",
        6: "monthly_allowance",
        7: "work_mode",
        8: "duration_months",
        9: "required_skills",
        10: "location_district",
    }

    if search_type == -1:
        internships = data_manager.list_internships(conn, limit=-1)
    elif search_type in filter_columns:
        search_item = prompt_input("Search: ")
        column = filter_columns[search_type]
        internships = data_manager.list_internships(
            conn,
            limit=-1,
            partial=True,
            **{column: search_item},
        )
    else:
        print("Error: something went wrong")
        return []

    print_listing_pages(internships, display_internship)
    return internships

def search_internship(conn):
    menuDisplayType("FilterInternships")
    while True:
        search_type = id_input(
            "Enter a search field (1-10), -1 to view all, or -2 to exit:"
        )
        if search_type == -1 or 1 <= search_type <= 10:
            return list_all_internship(conn, search_type)
        if search_type == -2:
            return None
        else:
            print("Please input a number between 1 and 10, or -1 to view all")

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
        deleted_run_id = prompt_input("Enter the match ID to delete (-1 for the latest, -2 to delete all,-3 to exit) :")
        is_valid = delete_run_id_checker(deleted_run_id,conn)
    return int(deleted_run_id)

def deleteListing(conn): 
    past_runs = data_manager.list_matches(conn)   # newest first
    if not past_runs:
        print("No past listing found")
        return None
    list_all_Listing(conn)
    deleted_run_id = delete_run_id_checking_Correcter(prompt_input("Enter the match ID to delete (-1 for the latest, -2 to delete all,-3 to exit):"),conn)
    if deleted_run_id == -3:
        return deleted_run_id
    elif deleted_run_id == -1:
        to_delete = [past_runs[0]["match_id"]]
    elif deleted_run_id == -2:
        to_delete = [match["match_id"] for match in past_runs]
    else:
        to_delete = [deleted_run_id]
    if Confirming_input(prompt_input(f"Delete {len(to_delete)} listing(s)? This cannot be undone (Y/N):")):
        for match_id in to_delete:
            data_manager.delete_match(conn, match_id)   # also deletes that match's profile snapshot
        print(f"Deleted {len(to_delete)} listing(s).")
    else:
        print("Nothing was deleted.")
    return deleted_run_id

#option 5 find internship matches:
def find_internship_matches(conn, studentprofile):
    print("Finding your top 5 internships. This can take a minute...")
    try:
        # DB NOTE (Johann): runs the AI, scores + flags each job, saves it, returns the new match_id
        match_id = logic_manager.find_matches(conn, studentprofile)
    except Exception as error:
        # e.g. no GEMINI_API_KEY, no internet, or the AI gave a bad answer: go back to the menu
        print(f"Could not find matches: {error}")
        return None
    print(f"Saved as match {match_id}. You can view it again with option 2.")
    display_run_details(conn, data_manager.get_match(conn, match_id),"Recommandation Run Result")
    return match_id

def inputmenucaller_1002(functionnumber,conn,studentprofile={}):
    if functionnumber == 1:
        student_profile = update_user_menu(studentprofile)
        return True,student_profile
    elif functionnumber == 2:
        view_past_listing(conn)
        return True,studentprofile
    elif functionnumber == 3:
        deleteListing(conn)
        return True,studentprofile
    elif functionnumber == 4:
        search_internship(conn)
        return True,studentprofile
    elif functionnumber == 5:
        find_internship_matches(conn, studentprofile)
        return True,studentprofile
    elif functionnumber == 6:
        add_student_profile_json(studentprofile)
        print("Have a good day. Thanks!")
        return False,studentprofile

def menu_caller_loop_1102(student_profile,conn):
    continues = True
    while continues:
        menutypenumerical = menuprinter(student_profile)
        functionnumber = inputlooper(prompt_input("Choose an option (1-6):"))
        continues,student_profile = inputmenucaller_1002(int(functionnumber),conn,student_profile)
    return student_profile,continues

def menu_function_call_general(student_profile,menutypenumerical,conn):
    if menutypenumerical == "1001":
        student_profile = menu_function_caller_first_time()
        menutypenumerical = menuprinter(student_profile)
        return student_profile,True
    if menutypenumerical == "1002":
        student_profile,continues = menu_caller_loop_1102(student_profile,conn)
        return student_profile,continues
