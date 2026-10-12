import os
import json
from pathlib import Path
import re
from datetime import datetime
from dateutil.relativedelta import relativedelta
import textwrap

import data_manager

STUDENT_PROFILE_JSON = Path(
    os.getenv(
        "STUDENT_PROFILE_JSON",
        str(Path(__file__).resolve().parent / "data" / "student_profile.json"),
    )
)

consoleWidth_60 = 60
consoleWidth_55 = 55
profileFieldWidth = 28

def prompt_input(message):
    print("\n" + "-" * consoleWidth_60)
    return input(f"{message.strip()}\n> ")

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
            print("  5. Exit")
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

        case "locationdisplay":
            singapore_areas_list = ["North","East","South","West","Central"]
            print_heading("PREFERRED LOCATIONS")
            for number, area in enumerate(singapore_areas_list, 1):
                print(f"  {number:>2}. {area}")
            print("=" * consoleWidth_60)

        case "Preferred_Word_Arrangement":
            Preferred_word_arragement = ["On-site","Hybrid","No Preference"]
            print_heading("PREFERRED WORK ARRANGEMENT")
            for number, word_arrangement in enumerate(Preferred_word_arragement, 1):
                print(f"  {number}. {word_arrangement}")

        case "company_preference":
            company_preferences = [
                "Start-ups",
                "Multi-National Corporations (MNCs)",
                "Government",
                "Statutory Boards",
                "Small-to-Medium Enterprises (SMEs)" ,
            ]
            print_heading("COMPANY PREFERENCES")
            for number, preference in enumerate(company_preferences, 1):
                print(f"  {number}. {preference}")
            print("=" * consoleWidth_60)

        case "update_display":
            print_heading("YOUR STUDENT PROFILE")
            display_student_profile(studentprofile)

        case _:
            print(f"Unknown menu type: {typeofmenu}")

#User input functions
# ISSUE NOT USED YET
def quitMenu():
    print("Are you sure you want to quit?")
    print("Exiting application")

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

    # Handle past_experience if it's an empty dictionary
    past_exp = profile.get("past_experience", {})
    exp_text = "None recorded" if not past_exp else str(past_exp)

    # Print the UI box
    print("\n" + "=" * consoleWidth_55)
    print(f"{'✨ YOUR STUDENT PROFILE ✨':^{consoleWidth_55}}")
    print("=" * consoleWidth_55)

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
    print(f"1,{'Course of Study:':<{profileFieldWidth}} {profile.get('course_of_study', 'N/A')}")
    print(f"2,{'Year of Study:':<{profileFieldWidth}} {formatted_year}")
    print(f"3,{'Internship Duration:':<{profileFieldWidth}} {duration_text}")
    print(f"4,{'Skills:':<{profileFieldWidth}} {format_list(profile.get('skills', []))}")
    print(f"5,{'Preferred Roles:':<{profileFieldWidth}} {format_list(profile.get('preferred_roles', []))}")
    print(f"6,{'Minimum Monthly Salary:':<{profileFieldWidth}} ${profile.get('minimum_monthly_salary', '0.00')}")
    print(f"7,{'Preferred Work Arrangement:':<{profileFieldWidth}} {profile.get('preferred_work_arrangement', 'N/A')}")
    print(f"8,{'Preferred Location:':<{profileFieldWidth}} {format_list(profile.get('preferred_location', []))}")
    print(f"9,{'Industry Interest:':<{profileFieldWidth}} {format_list(profile.get('industry_interest', []))}")
    print(f"10,{'Company Preference:':<{profileFieldWidth}} {format_list(profile.get('company_preference', []))}")
    print(f"11,{'Past Experience:':<{profileFieldWidth}} {exp_text}")
    print("=" * consoleWidth_55 + "\n")


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
    return courses[course_of_study_id-1]

def validate_course_of_study(course):
    if not course:
        print("Invalid input. Please enter a number corresponding to your course of study.")
        return False
    elif course.isdigit()!= True:
        print("Invalid input. Please enter a number corresponding to your course of study.")
        return False 
    elif int(course) < 1 or int(course) > 45:
        print("Invalid input. Please enter a number between 1 and 45.")
        return False
    return True

def course_of_study_input(courseofStudy):
    is_valid = validate_course_of_study(courseofStudy)
    while is_valid == False:
        #course_of_study_menu()
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
        return "Invalid","Invalid",False
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
        return "Invalid","Invalid",False

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

def skill_validation(skillsinput):
    areusure = True
    if not skillsinput:
        print("Invalid input. Please try again.")
        areusure = False
        return areusure
    elif skillsinput.isdigit()==True:
        print("You entered a number.")
        areusure = Confirming_input(prompt_input("Is this correct? (Y/N):"))
        return areusure
    elif len(skillsinput) == 1:
        print("You entered a single character.")
        areusure = Confirming_input(prompt_input("Is this correct? (Y/N):"))
        return areusure
    return areusure

def skill_validate(skillsinput):
    is_valid = skill_validation(skillsinput)
    while is_valid == False:
        skillsinput = prompt_input("Enter a skill (or type 'exit' to finish):")
        is_valid = skill_validation(skillsinput)
    return skillsinput , is_valid

def continuousloopskills(skillsinput):
    skillslist = []
    while True:
        skillinput, _ = skill_validate(skillsinput)
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
        print("The number cannot be negative.")
        return False
    elif minimum_month_salary == 0:
        print("The value you entered is 0.")
        return False
    elif minimum_month_salary>10000:
        print("The value you entered is greater than 10,000.")
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
    return preferredlocations,is_valid

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
        response, _ = validating_perferred_location_input(response)
        if response.casefold() == "exit":
            return selected

        location = preferredlocations_number_to_string(response)
        append_unique_value(selected, location, "Preferred location")
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
    "Multi-National Corporations (MNCs)",
    "Small-to-Medium Enterprises (SMEs)",
    "Start-ups",
    "Government",
]
    return company_preferenceslist[int(company_preference)-1] 

def company_preference_checker(company_preference):
    is_valid = validate_company_preference(company_preference)
    while is_valid == False:
        company_preference = prompt_input("Choose a company preference (1-5, or type 'exit' to skip):")
        is_valid = validate_company_preference(company_preference)
    return company_preference,is_valid

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
        response, _ = company_preference_checker(response)
        if response.casefold() == "exit":
            return selected

        preference = company_preference_number_to_String(response)
        append_unique_value(selected, preference, "Company preference")
        response = prompt_input(
            "Choose another company preference (1-5, or type 'exit' to finish):"
        )

def validate_pass_experience(job_title,dateofhiring,jobdiscription):
    while not job_title.strip():
        print("Please enter a job title.")
        job_title = prompt_input("Enter your job title:")

    while True:
        try:
            start_text, end_text = dateofhiring.split("-", maxsplit=1)
            start_date = datetime.strptime(start_text.strip(), "%d/%m/%Y")
            end_date = datetime.strptime(end_text.strip(), "%d/%m/%Y")
            if start_date <= end_date:
                break
        except ValueError:
            pass
        print("Enter the experience dates as DD/MM/YYYY - DD/MM/YYYY.")
        dateofhiring = prompt_input("Enter the period worked (DD/MM/YYYY - DD/MM/YYYY):")

    while not jobdiscription.strip():
        print("Please enter a job description.")
        jobdiscription = prompt_input("Enter a short job description:")

    return job_title.strip(), dateofhiring.strip(), jobdiscription.strip()

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

def looping_pass_experience(pass_experience_input):
    experiences = {}
    response = pass_experience_input.strip().lower()

    while response not in {"have", "exit"}:
        response = prompt_input("Enter 'Have' to add past experience or 'Exit' to skip:").strip().lower()

    while response == "have":
        job_title = prompt_input("Enter your job title:")
        while any(existing.casefold() == job_title.strip().casefold() for existing in experiences):
            print("That job title has already been added; enter a different title.")
            job_title = prompt_input("Enter a different job title:")
        dateofhiring = prompt_input("Enter the period worked (DD/MM/YYYY - DD/MM/YYYY):")
        jobdiscription = prompt_input("Enter a short job description:")
        job_title, dateofhiring, jobdiscription = validate_pass_experience(
            job_title, dateofhiring, jobdiscription
        )
        experiences[job_title] = {
            "Date": dateofhiring,
            "Job_Decription": jobdiscription,
        }
        response = prompt_input("Do you have another past experience? (Have/Exit):").strip().lower()
        while response not in {"have", "exit"}:
            response = prompt_input("Enter 'Have' to add another or 'Exit' to finish:").strip().lower()

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

        menuDisplayType("Preferred_Word_Arrangement")
        preferred_work_arrangement = preferred_work_location_looper(
            prompt_input(
                "Choose a work arrangement (1-3, or type 'exit' to choose all):"
            )
        )

        menuDisplayType("locationdisplay")
        preferedlocation = preferredlocation_listadder(
            prompt_input("Choose a preferred location (1-5 to choose individually, or type 'exit' to choose All):")
        )
    
        
        # Industry interests (e.g fintech, cybersecurity), 
        Industry_interest = industrial_input_list_adder(
            prompt_input("Enter an industry interest (or type 'exit' to skip):")
        )
    
        # Company preference (e.g start-up, MNCs),
        menuDisplayType("company_preference") 
        Company_preference = company_preference_looper(
            prompt_input(
                "Choose a company preference (1-5, or type 'exit' to choose all):"
            )
        )

        # Past experience (e.g previous SWE internship)
        past_experience = looping_pass_experience(
            prompt_input("Do you have past work experience? (Have/Exit):")
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

# loading json file (Idk but data manager should be handeling this)
def initialize_student_profile_Json():
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
    
# Is the True statement even needed?
def get_student_profile_json():
    try:
        student_profile = initialize_student_profile_Json()
    except FileNotFoundError:
        print("Student profile file not found; creating a new profile")
        create_a_student_profile_json()
        student_profile = initialize_student_profile_Json()
        print("Student profile created successfully")
    return student_profile, True

def loadingScreenMenu(fileloadingchecker,menutype):
    if menutype == "loadingScreenMenu":
        print(
            "The program is trying to reload the student profile. "
            f"Attempt {fileloadingchecker} of 3."
        )
    elif menutype =="FalseToLoadMessage":
        print("Could not load student_profile.json. Please check that the file is valid.")

def student_profile_load_checker(Fileloaded):
    fileloadingchecker = 1
    while (not Fileloaded and fileloadingchecker <=3):
        loadingScreenMenu(fileloadingchecker,"loadingScreenMenu")
        Fileloaded,booleanloader = get_student_profile_json()
        fileloadingchecker = fileloadingchecker+1
    if (fileloadingchecker>3 and booleanloader == False):
        loadingScreenMenu(fileloadingchecker,"FalseToLoadMessage")
        return False,Fileloaded
    if Fileloaded:
        return True,Fileloaded

def student_profile_load_check_linker(Booleanoffileloaded,Fileloaded):
    BooleanFileloaded = True
    
    if Booleanoffileloaded == False:
        BooleanFileloaded , Fileloaded = student_profile_load_checker(Fileloaded)
        return BooleanFileloaded,Fileloaded
    else:
        return BooleanFileloaded,Fileloaded



def menuprinter(student_profile):
    if not student_profile:
        menuDisplayType("Starting")
        return "1001"
    else:
        menuDisplayType("SecondTime")
        return "1002"

def input_validator():
    studentprofile,inputboolean = get_student_profile_json()
    if inputboolean == True:
        print("User input added successfully.")
        return studentprofile,True
    else:
        print("Failed to add user input.")
        return studentprofile,False

def add_student_profile_json(student_profile):
    STUDENT_PROFILE_JSON.parent.mkdir(parents=True, exist_ok=True)
    with open(STUDENT_PROFILE_JSON, "w", encoding="utf-8") as file:
        json.dump(student_profile, file, indent=4)

def menu_function_caller_first_time():
    inputed = False
    while not inputed:
        Userinput = Get_User_Input()
        add_student_profile_json(Userinput)
        studentprofile,inputed = input_validator()
    return studentprofile

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
            menuDisplayType("Preferred_Word_Arrangement")
            updated_profile["preferred_work_arrangement"] = preferred_work_location_looper(
                prompt_input(
                    "Choose a work arrangement (1-3, or type 'exit' to choose all):"
                )
            )
        elif field_number == 8:
            menuDisplayType("locationdisplay")
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
            menuDisplayType("company_preference")
            updated_profile["company_preference"] = company_preference_looper(
                prompt_input(
                    "Choose a company preference (1-5, or type 'exit' to choose all):"
                )
            )
        elif field_number == 11:
            updated_profile["past_experience"] = looping_pass_experience(
                prompt_input("Do you have past work experience? (Have/Exit):")
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
    menuDisplayType("update_display",profile)
    return checking_user_update(studentprofile)

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

def input_validator_option(functionnumber):
    if functionnumber.isdigit()==False:
        print("Your input is not an integer. Please try again.")
        return False
    functionnumber = int(functionnumber)
    if(functionnumber<1):
        print("Your input is incorrect please Try again")
        return False
    elif (functionnumber >5):
        print("Your input is incorrect please Try again")
        return False
    return True

def inputlooper(functionnumber):
    Trueorfalse = input_validator_option(functionnumber)
    while not Trueorfalse :
        functionnumber = prompt_input("Choose an option (1-5):")
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

def display_run_summary(run):
    print_card("PAST RECOMMENDATION RUN", [
        ("Run ID", run.get("run_id")),
        ("Created", run.get("created_at")),
        ("Match Count", run.get("match_count", len(run.get("matches", [])))),
        ("Feedback", run.get("overall_feedback")),
    ])

def display_run_details(run):
    display_run_summary(run)
    if "profile" in run:
        print_card("PROFILE SNAPSHOT", [
            ("Profile", json.dumps(run["profile"], indent=2, ensure_ascii=False)),
        ])
    for match in run.get("matches", []):
        print_card(f"INTERNSHIP MATCH - JOB {match.get('job_id', 'N/A')}", [
            ("Overall Score", match.get("overall_match_score")),
            ("Skills", match.get("skills_match")),
            ("Role", match.get("role_match")),
            ("Industry Interest", match.get("industry_interest_match")),
            ("Experience", match.get("experience_match")),
            ("Salary", match.get("salary_match")),
            ("Work Arrangement", match.get("work_arrangement_match")),
            ("Location", match.get("location_match")),
            ("Company Preference", match.get("company_preference_match")),
            ("Advice", match.get("advice")),
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
    past_runs = data_manager.list_runs(conn, limit=-1)
    print_listing_pages(past_runs, display_run_summary)

def get_latest_one(conn):
    latest_runs = data_manager.list_runs(conn, limit=1)
    latest_run = data_manager.get_run(conn, latest_runs[0]["run_id"]) if latest_runs else None
    if latest_run is None:
        print("No past listing found")
        return None
    display_run_details(latest_run)
    return latest_run

def view_past_listing(conn):
    run_id = id_input(
        "Enter a run ID to view (-1 for the latest run, or -2 to browse all runs):"
    )
    if run_id == -1:
        get_latest_one(conn)
    elif run_id == -2:
        list_all_Listing(conn)
    else:
        run = data_manager.get_run(conn, run_id)
        if run is None:
            print("No past listing found with that id")
        else:
            display_run_details(run)

def list_all_internship(conn):
    internships = data_manager.list_internships(conn, limit=-1)
    print_listing_pages(internships, display_internship)
    return internships


def search_internship(conn):
    input_id = id_input(
        "Enter an internship ID to search (-1 to browse all internships):"
    )
    if input_id != -1:
        internship = data_manager.get_internship(conn, input_id)
        if internship is None:
            print("No internship found with that id")
        else:
            display_internship(internship)
    else:
        internship = list_all_internship(conn)



#option 4 delete listing:

def delete_run_id_checker(deleted_run_id,conn):
    past_runs = data_manager.list_runs(conn, limit=-1)
    if deleted_run_id.isdigit()==False:
        return False
    elif deleted_run_id <-2 or deleted_run_id>past_runs[len(past_runs)-1]["run_id"]:
        return False
    else:
        return True

def delete_run_id_checking_Correcter(deleted_run_id,conn):
    is_valid = delete_run_id_checker(deleted_run_id,conn)
    while not is_valid:
        deleted_run_id = input("Enter the run_id that you want to delete specifically ,type -1 to delete the latest listing , type -2 to delete all listing")
        is_valid = delete_run_id_checker(deleted_run_id,conn)
    return deleted_run_id

def deleteListing(conn): 
    deleted_run_id = delete_run_id_checking_Correcter(input("Enter the run_id that you want to delete specifically ,type -1 to delete the latest listing , type -2 to delete all listing"),conn)
    return deleted_run_id

def inputmenucaller_1002(functionnumber,conn,studentprofile={}):
    if functionnumber == 1:
        student_profile = update_user_menu(studentprofile)
        return True,student_profile
    elif functionnumber == 2:
        view_past_listing(conn)
        return True,studentprofile
    elif functionnumber == 3:
        deleteListing(conn)#Pending completion
        return True,studentprofile
    elif functionnumber == 4:
        search_internship(conn)
        return True,studentprofile
    elif functionnumber == 5:
        add_student_profile_json(studentprofile)
        print("Have a good day. Thanks!")
        return False,studentprofile

def menu_caller_loop_1102(student_profile,conn):
    continues = True
    while continues:
        menutypenumerical = menuprinter(student_profile)
        functionnumber = inputlooper(prompt_input("Choose an option (1-5):"))
        continues,student_profile = inputmenucaller_1002(int(functionnumber),conn,student_profile)
    return student_profile,continues

def menu_function_call_general(menutypenumerical,conn):
    if menutypenumerical == "1001":
        student_profile = menu_function_caller_first_time()
        menutypenumerical = menuprinter(student_profile)
        return student_profile,True
    if menutypenumerical == "1002":
        student_profile,trueorfalse = get_student_profile_json()
        student_profile,continues = menu_caller_loop_1102(student_profile,conn)
        return student_profile,continues
