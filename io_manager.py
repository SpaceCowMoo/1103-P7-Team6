import json
from pathlib import Path
import re
from datetime import datetime

STUDENT_PROFILE_JSON = Path(__file__).resolve().parent / "data" / "student_profile.json"


def UserResponseidMaker():
    return 0

#Menu output styles
def menuDisplayType(typeofmenu,studentprofile={}):
    match typeofmenu:
        case "Starting":
            print("---------------------")
            print("----Intern Link------")
            print("---------------------")
            print("Welcome to Intern Link and please enter your your user profile")

        case "SecondTime":
            print("---------------------")
            print("----Intern Link------")
            print("---------------------")
            print("1:Update Profile")
            print("2:View Past Listing")
            print("3:Search for new internship")
            print("4:exit")



        case "CourseDisplay":
            print ("""
            Singapore Institute of Technology (SIT) Full Course List 2026
            
            Infocomm Technology
            1: Applied Artificial Intelligence
            2: Applied Computing (Fintech)
            3: Applied Computing Degree (via CSM Pathway)
            4: Computer Engineering
            5: Computer Science in Interactive Media and Game Development
            6: Computer Science in Real-Time Interactive Simulation
            7: Computing Science
            8: Digital Art and Animation
            9: Information and Communications Technology (Information Security)
            10: Information and Communications Technology (Software Engineering)
            11: User Experience and Game Design
            
            Engineering
            12: Aircraft Systems Engineering
            13: Chemical Engineering
            14: Civil Engineering
            15: Digital Supply Chain
            16: Electrical and Electronic Engineering
            17: Electrical and Electronic Engineering Degree (via CSM Pathway)
            18: Electrical Power Engineering
            19: Electronics and Data Engineering
            20: Engineering Systems
            21: Infrastructure and Systems Engineering Degree (via CSM Pathway)
            22: Mechanical Design and Manufacturing Engineering
            23: Mechanical Engineering
            24: Naval Architecture and Marine Engineering
            25: Robotics Systems
            26: Sustainable Built Environment
            
            Business, Communication and Design
            27: Accountancy
            28: Aviation Management
            29: Business and Infocomm Technology
            30: Communication and Digital Media
            31: Hospitality and Tourism Management
            32: Integrated Studies in Technology and Management
            33: Integrated Studies in Technology and Management with Specialisation in Supply Chain
            
            Food, Chemical and Biotechnology
            34: Dietetics and Nutrition
            35: Food Business Management (Baking and Pastry Arts)
            36: Food Business Management (Culinary Arts)
            37: Food Technology
            38: Pharmaceutical Engineering
            
            Health and Social Sciences
            39: Diagnostic Radiography
            40: Nursing
            41: Nursing (Pre-registration and Specialty Training)
            42: Occupational Therapy
            43: Physiotherapy
            44: Radiation Therapy
            45: Speech and Language Therapy
            """)

        case "locationdisplay":
            singapore_areas_list = [
                # North Region
                "Woodlands",
                "Yishun",
                "Sembawang",
                "Mandai",
                "Sungei Kadut",
                "Lim Chu Kang",
                "Simpang",
                "Central Water Catchment",
                # North-East Region
                "Ang Mo Kio",
                "Hougang",
                "Punggol",
                "Sengkang",
                "Serangoon",
                "Seletar",
                "Paya Lebar",
                "North-Eastern Islands",
                # East Region
                "Bedok",
                "Tampines",
                "Pasir Ris",
                "Changi",
                "Changi Bay",
                # West Region
                "Jurong East",
                "Jurong West",
                "Clementi",
                "Bukit Batok",
                "Bukit Panjang",
                "Choa Chu Kang",
                "Tengah",
                "Boon Lay",
                "Pioneer",
                "Tuas",
                "Western Islands",
                "Western Water Catchment",
                # Central Region
                "Downtown Core",
                "Marina East",
                "Marina South",
                "Orchard",
                "Newton",
                "Novena",
                "River Valley",
                "Rochor",
                "Singapore River",
                "Outram",
                "Museum",
                "Straits View",
                "Bishan",
                "Bukit Merah",
                "Bukit Timah",
                "Geylang",
                "Kallang",
                "Marine Parade",
                "Queenstown",
                "Toa Payoh",
                "Southern Islands",
                "Tanglin",
                "Remote"
            ]
            singapore_areas_numbered_string = "\n".join(f"{i}. {area}" for i, area in enumerate(singapore_areas_list, 1))
            print(singapore_areas_numbered_string)

        case "company_preference":
            print("""
            1.Start-ups
            2.Scale-ups
            3.Multi-National Corporations(MNCs) 
            4.Big Tech Companies 
            5.Government 
            6.Statutory Boards
            7.Semi-Govement tech companies
            8.Small-to-Medium Enterprises



            """)

        case "update_display":
            profile = studentprofile
            display_student_profile(profile)
        case _:
            print("Insert a proper display type")

#User input functions
def quitMenu():
    print("Exiting application")

def format_list(item):
    if isinstance(item, list) and item:
        return ", ".join(item)
    return "None specified"

# 2. Define a function to display the profile nicely
def display_student_profile(profile):
    # Format the Year of Study ("1,2" -> "Year 1, Semester 2")
    raw_year = profile.get("Year_of_Study", "")
    year_parts = raw_year.split(",")
    if len(year_parts) == 2:
        formatted_year = f"Year {year_parts[0].strip()} , Semester {year_parts[1].strip()}"
    else:
        formatted_year = raw_year

    # Handle past_experience if it's an empty dictionary
    past_exp = profile.get("past_experience", {})
    exp_text = "None recorded" if not past_exp else str(past_exp)

    # Print the UI box
    print("\n" + "=" * 55)
    print(f"{'✨ YOUR STUDENT PROFILE ✨':^55}")
    print("=" * 55)

    w = 28
    print(f"{'Course of Study:':<{w}} {profile.get('Cource_of_Study', 'N/A')}")
    print(f"{'Year of Study:':<{w}} {formatted_year}")
    print(f"{'Available Internship:':<{w}} {profile.get('Avaliable_Intership_date', 'N/A')}")
    print(f"{'Preferred Month:':<{w}} {profile.get('Preferred_month', 'N/A')}")
    print(f"{'Skills:':<{w}} {format_list(profile.get('Skills', []))}")
    print(f"{'Preferred Roles:':<{w}} {format_list(profile.get('Preferred_Roles', []))}")
    print(f"{'Minimum Monthly Salary:':<{w}} ${profile.get('Minimum_monthly_Salary', '0.00')}")
    print(f"{'Preferred Location:':<{w}} {format_list(profile.get('Preferred_location', []))}")
    print(f"{'Industry Interest:':<{w}} {format_list(profile.get('Industry_interest', []))}")
    print(f"{'Company Preference:':<{w}} {profile.get('Company_preference', 'N/A')}")
    print(f"{'Past Experience:':<{w}} {exp_text}")
    print("=" * 55 + "\n")


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

def validate_Cource_of_Study(cource):
    if not cource:
        print("Invalid input. Please enter a number corresponding to your course of study.")
        return False
    elif cource.isdigit()!= True:
        print("Invalid input. Please enter a number corresponding to your course of study.")
        return False 
    elif int(cource) < 1 or int(cource) > 45:
        print("Invalid input. Please enter a number between 1 and 45.")
        return False
    return True

def course_of_study_input(courseofStudy):
    is_valid = validate_Cource_of_Study(courseofStudy)
    while is_valid == False:
        #course_of_study_menu()
        courseofStudy = input("Please enter your course of study(1-45): ")
        is_valid = validate_Cource_of_Study(courseofStudy)
    return course_of_study_words(int(courseofStudy))



def validate_Year_of_Study(year):
    while re.match(r"Year\s*[1-6]\s*,\s*(?:Semester|Trimester|Trimesters)\s*[1-3]", year, re.IGNORECASE) is None:
        print("Invalid input. Please enter your year of study in the format 'Year X, Semester/Trimester Y' where X is between 1 and 6 and Y is between 1 and 3.")
        year = input("Please enter your year of study(Year 1-6 , Trimesters 1-3 ): ")
    years_Trimesters = year.lower().strip().split(",")
    year = years_Trimesters[0].strip().split(" ")
    Trimesters = years_Trimesters[1].strip().split(" ") 
    yearfinal, Trimestersfinal = Spacing_Year_of_Study_String(year,Trimesters)
    return yearfinal, Trimestersfinal


    


def Spacing_Year_of_Study_String(year,Trimesters):
    yearfinal = ""
    Trimestersfinal = ""
    for i in year:
        if i.isdigit() == True:
            yearfinal += i
    for i in Trimesters:
        if i.isdigit() == True:
            Trimestersfinal += i
    return yearfinal, Trimestersfinal

def check_Internship_Duration_format(internshipDuration):
    if not internshipDuration :
        print("Invalid input. Please enter the duration of your available internships in the format 'DD/MM/YYYY - DD/MM/YYYY'.")
        return "Invalid","Invalid",False
    internshipDuration = internshipDuration.split("-")
    try:
        startingdate = datetime.strptime(internshipDuration[0].strip(), "%d/%m/%Y")
        endingdate =datetime.strptime(internshipDuration[1].strip(), "%d/%m/%Y")
        if startingdate < datetime.now() or endingdate< datetime.now():
            print("Sorry Can't Set Date in the past for internship ")
            return "Invalid","Invalid",False
        if startingdate>endingdate or endingdate<startingdate:
            print("Sorry can't process look like you set the date wrong ")
            return "Invalid","Invalid",False
        else:
            return startingdate, endingdate,True
    except Exception:
        print("Invalid input. Please enter the duration of your available internships in the format 'DD/MM/YYYY - DD/MM/YYYY'.")
        return "Invalid","Invalid",False

def internship_duration_checker(internshipDuration):
    Startingdate,endingdate,is_valid = check_Internship_Duration_format(internshipDuration)
    
    while is_valid == False:
        internshipDuration = input("Please enter the duration of your available internships (Example: 01/11/2023 - 30/11/2023 ): ")
        Startingdate,endingdate,is_valid = check_Internship_Duration_format(internshipDuration)
    return Startingdate, endingdate

def valid_month_preferrance(startingdate , endingdate):
    startingmonth = startingdate.month
    startingyear = startingdate.year
    endingmonth = endingdate.month
    endingyear = endingdate.year

    return f'{startingmonth}/{startingyear} - {endingmonth}/{endingyear}'

def validating_month(inputmonth):
    if not inputmonth:
        print("Invalid input , please try again")
        return False , "Invalid"
    inputmonth = inputmonth.strip()
    if inputmonth.isdigit():
        month_number = int(inputmonth)
        if not 1 <= month_number <= 12:
            print("Enter a month from 1 to 12.")
            return False,"Invalid"
        month_name = datetime.strptime(f"{month_number:02d}", "%m").strftime("%B")
        return True, month_name
    else:
        try:
            month_name = datetime.strptime(inputmonth, "%B").strftime("%B")
            return True, month_name
        except ValueError:
            print("Enter a month number or full month name.")
            return False,"Invalid"


def validate_month_preferrance(startingdate,endingdate,inputedmonth):
    valid_input,inputresult = validating_month(inputedmonth)
    while valid_input == False:
        valid_months = valid_month_preferrance(startingdate,endingdate)
        inputedmonth = input(f"Please enter the prefer starting month of your internships between {valid_months} , Example Febuary:")
        valid_input,inputresult = validating_month(inputedmonth)
    return inputresult

def Confirming_input(confirmation):
    return confirmation.strip().lower() == "y"

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
        print("invalid input , please enter again")
        areusure = False
        return areusure
    elif skillsinput.isdigit()==True:
        print("you entered a number ")
        areusure = Confirming_input(input("Are u sure what u click in Correct, Example (Y/N): "))
        return areusure
    elif len(skillsinput) == 1:
        print("You entered a character")
        areusure = Confirming_input(input("Are u sure what u click in Correct, Example (Y/N): "))
        return areusure
    return areusure

def skill_validate(skillsinput):
    is_valid = skill_validation(skillsinput)
    while is_valid == False:
        skillsinput = input("Please enter your skills (type exit to exit):")
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
        skillsinput = input("Please enter your skills (type exit to continue to next input):")

def validate_Preferred_role(preferred_role):
    areusure = True 
    if not preferred_role:
        areusure = False
        print("Please Enter a value")
        return areusure
    elif preferred_role.isdigit() == True:
        print("you are entering a number")
        areusure=Confirming_input(input("Are u sure , what u enter (Enter Y/N):"))
        return areusure
    elif len(preferred_role) == 1:
        print("you enter a character are u sure")
        areusure=Confirming_input(input("Are u sure , what u enter (Enter Y/N):"))
        return areusure
    else:
        return areusure 


def checking_Preferred_role_input(Preferred_role):
    is_valid = validate_Preferred_role(Preferred_role)
    while is_valid == False:
        Preferred_role = input("Enter your preferred role (enter exit to continue):")
        is_valid = validate_Preferred_role(Preferred_role)
    return is_valid,Preferred_role

def continoous_Preferred_role(Preferred_role):
    Preferred_rolelist = []
    is_valid,Preferred_role = checking_Preferred_role_input(Preferred_role)
    if Preferred_role.strip().lower() == "exit":
        return Preferred_rolelist
    append_unique_value(Preferred_rolelist, Preferred_role, "Preferred role")
    while True:
        Preferred_role = input("Enter your preferred role (enter exit to continue):")
        _, Preferred_role = checking_Preferred_role_input(Preferred_role)
        if Preferred_role.lower().strip() == "exit":
            return Preferred_rolelist
        append_unique_value(Preferred_rolelist, Preferred_role, "Preferred role")

def validating_minimum_monthly_salary(minimum_month_salary):
    if not minimum_month_salary:
        print("Please Enter a value !")
        return False
    elif minimum_month_salary.lower().strip() == "exit":
        return True
    elif minimum_month_salary.isdigit() ==False:
        print("Number you enter is not a number")
        return False
    minimum_month_salary = float(minimum_month_salary)
    if minimum_month_salary<0 :
        print("Number You enter in the negative")
        return False
    elif minimum_month_salary == 0:
        print("The value you enter is 0")
        return Confirming_input(input("Are u sure , what u enter (Enter Y/N):"))
    elif minimum_month_salary>10000:
        print("The value you enter is more than 10000 ")
        return Confirming_input(input("Are u sure , what u enter (Enter Y/N):"))
    else:
        return True

def minimum_monthly_salary_checker(minimum_monthly_salary):
    is_valid = validating_minimum_monthly_salary(minimum_monthly_salary)
    while is_valid == False:
        minimum_monthly_salary = input("Enter your expected monthly salary (enter exit to continue): ")
        is_valid = validating_minimum_monthly_salary(minimum_monthly_salary)
    if minimum_monthly_salary.isdigit() == True:
        return f"{float(minimum_monthly_salary):.2f}"
    else:
        return ""

def validating_preferred_locations(preferredlocations):
    if not preferredlocations:
        print("invalid value")
        return False
    elif  preferredlocations.lower().strip() == "exit":
        return True
    elif preferredlocations.isdigit() == False:
        print("Enter Value is not a number")
        return False
    preferredlocations = int(preferredlocations)
    if preferredlocations<0 or preferredlocations>56:
        print("The number is incorrect")
        return False
    else:
        return True
    
def validating_perferred_location_input(preferredlocations):
    is_valid = validating_preferred_locations(preferredlocations)
    while is_valid == False:
        preferredlocations = input("Enter your preferred location (1-56)(Enter exit to continue):")
        is_valid = validating_preferred_locations(preferredlocations)
    return preferredlocations,is_valid

def preferredlocations_number_to_string(preferredlocationnumber):
    singapore_areas_list = [
                    # North Region
                    "Woodlands",
                    "Yishun",
                    "Sembawang",
                    "Mandai",
                    "Sungei Kadut",
                    "Lim Chu Kang",
                    "Simpang",
                    "Central Water Catchment",
                    # North-East Region
                    "Ang Mo Kio",
                    "Hougang",
                    "Punggol",
                    "Sengkang",
                    "Serangoon",
                    "Seletar",
                    "Paya Lebar",
                    "North-Eastern Islands",
                    # East Region
                    "Bedok",
                    "Tampines",
                    "Pasir Ris",
                    "Changi",
                    "Changi Bay",
                    # West Region
                    "Jurong East",
                    "Jurong West",
                    "Clementi",
                    "Bukit Batok",
                    "Bukit Panjang",
                    "Choa Chu Kang",
                    "Tengah",
                    "Boon Lay",
                    "Pioneer",
                    "Tuas",
                    "Western Islands",
                    "Western Water Catchment",
                    # Central Region
                    "Downtown Core",
                    "Marina East",
                    "Marina South",
                    "Orchard",
                    "Newton",
                    "Novena",
                    "River Valley",
                    "Rochor",
                    "Singapore River",
                    "Outram",
                    "Museum",
                    "Straits View",
                    "Bishan",
                    "Bukit Merah",
                    "Bukit Timah",
                    "Geylang",
                    "Kallang",
                    "Marine Parade",
                    "Queenstown",
                    "Toa Payoh",
                    "Southern Islands",
                    "Tanglin",
                    "Remote",
                ]
    preferredlocationnumber = int(preferredlocationnumber)
    return singapore_areas_list[(preferredlocationnumber-1)]

def preferredlocation_listadder(preferredlocations):
    preferredlocationslist = []
    while True:
        preferredlocations, _ = validating_perferred_location_input(preferredlocations)
        if preferredlocations.strip().casefold() == "exit":
            return preferredlocationslist
        location = preferredlocations_number_to_string(preferredlocations)
        append_unique_value(preferredlocationslist, location, "Preferred location")
        preferredlocations = input("Enter your preferred location (1-56)(Enter exit to continue):")
        
def validate_Industry_interest(Industrial_intrest):
    if not Industrial_intrest:
        print("please enter correct input")
        return False
    elif Industrial_intrest.strip().lower() == "exit":
        return True
    elif Industrial_intrest.isdigit()==True:
        print("You enter a digit ")
        return Confirming_input(input("Are u sure , what u enter (Enter Y/N):"))
    elif len(Industrial_intrest)==1:
        print("you enter a character")
        return Confirming_input(input("Are u sure , what u enter (Enter Y/N):"))
    return True

def Industrial_input_checker(industrial_interest):
    is_valid = validate_Industry_interest(industrial_interest)
    while is_valid == False:
        industrial_interest = input("Enter your Industry Interest (Enter exit to continue):")
        is_valid = validate_Industry_interest(industrial_interest)
    return industrial_interest,is_valid

def industrial_input_list_adder(industrial_interest):
    industrial_interestlist = []
    while True:
        industrial_interest, _ = Industrial_input_checker(industrial_interest)
        if industrial_interest.strip().casefold() == "exit":
            return industrial_interestlist
        append_unique_value(industrial_interestlist, industrial_interest, "Industry interest")
        industrial_interest = input("Enter another Industry Interest (or enter exit to continue):")


def validate_company_preference(company_perference):
    if not company_perference:
        print("Incorrect input")
        return False
    elif company_perference.lower().strip() == "exit":
        return True
    elif company_perference.isdigit() == False:
        print("Please enter a digit")
        return False
    company_perference = int(company_perference)
    if not 1 <= company_perference <= 8:
        print("please enter the correct input")
        return False
    return True

def company_preference_number_to_String(company_preference):
    company_preferenceslist = [
    "Start-ups",
    "Scale-ups",
    "Multi-National Corporations (MNCs)",
    "Big Tech Companies",
    "Government",
    "Statutory Boards",
    "Semi-Government Tech Companies",
    "Small-to-Medium Enterprises",
]
    return company_preferenceslist[int(company_preference)-1] 

def company_preference_checker(company_preference):
    is_valid = validate_company_preference(company_preference)
    while is_valid == False:
        company_preference = input("Enter your company preference (Enter exit to continue):")
        is_valid = validate_company_preference(company_preference)
    return company_preference,is_valid

def company_preference_looper(company_preference):
    company_preference , is_valid = company_preference_checker(company_preference)
    if company_preference.strip().lower() == "exit":
        return ""
    return company_preference_number_to_String(int(company_preference))

def validate_pass_experience(job_title,dateofhiring,jobdiscription):
    while not job_title.strip():
        print("Please enter a job title.")
        job_title = input("Enter your job title: ")

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
        dateofhiring = input("Enter the period you worked (for example, 01/01/2024 - 30/06/2024): ")

    while not jobdiscription.strip():
        print("Please enter a job description.")
        jobdiscription = input("Enter your job description: ")

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
        response = input("Enter 'Have' to add past experience or 'Exit' to skip: ").strip().lower()

    while response == "have":
        job_title = input("Enter your job title: ")
        while any(existing.casefold() == job_title.strip().casefold() for existing in experiences):
            print("That job title has already been added; enter a different title.")
            job_title = input("Enter your job title: ")
        dateofhiring = input("Enter the period you worked (DD/MM/YYYY - DD/MM/YYYY): ")
        jobdiscription = input("Enter your job description: ")
        job_title, dateofhiring, jobdiscription = validate_pass_experience(
            job_title, dateofhiring, jobdiscription
        )
        experiences[job_title] = {
            "Date": dateofhiring,
            "Job_Decription": jobdiscription,
        }
        response = input("Do you have another past experience? (Have/Exit): ").strip().lower()
        while response not in {"have", "exit"}:
            response = input("Enter 'Have' to add another or 'Exit' to finish: ").strip().lower()

    return arrange_pass_experiences(experiences)


        
    
def Get_User_Input():
    sampleinput = {
        "P1001": {
            "Course_of_Study": "Applied Artificial Intelligence",
            "Year_of_Study": "Year 1, Semester 1",
            "Internship_Duration": "01/11/2023 - 30/11/2023",
            "Prefer_month":"February",
            "Skills":["C Programming","Python Programming", "Artifical Intelligence programming"],
            "Prefer_Role":["Ict Intern"],
            "Minimum_monthly_salary":500,
            "Preferred_location":["Chua Chu kang"],
            "Industry_interests":["Artifical Intelligence"],
            "Company_preference":"MNC",
            "Past_experience":
            {
                "Ict Intern":{
                    "Date":"11/06/2024 - 24/06/2025",
                    "Job Decription":"It a work about a program"



                }

            }




        }
    }
    loopmanger = True
    while loopmanger:

        #Mandatory Fields
        

        #Cource of Study Input
        menuDisplayType("CourseDisplay")
        userCourse = input("Please enter your course of study(1-45): ")
        courseOfStudy = course_of_study_input(userCourse)

        # Year of Study Input
        yearOfStudy = input("Please enter your study period in the format 'Year X, Trimester Y' (e.g., Year 2, Trimester 1): ")
        userYear, userTrimester = validate_Year_of_Study(yearOfStudy)

        #Avaliable internships duration input
        internshipDuration = input("Please enter the duration of your available internships (Example: 01/11/2026 - 30/11/2026 ): ")
        startingdate, endingdate = internship_duration_checker(internshipDuration)

        #prefered Start month
        valid_months = valid_month_preferrance(startingdate,endingdate)
        preferedstartedmonth = validate_month_preferrance(startingdate,endingdate,input(f"Please enter the prefer starting month of your internships between {valid_months} , Example Febuary:"))

        #skills
        Skills = continuousloopskills(input("Please enter your skills: "))


        #optional Input

        #Preferred roles (e.g Marketing Assistant, Data Analyst), 
        preferedroles = continoous_Preferred_role(input("Enter your preferred role (enter exit to skip):"))
        
        
    
        # Minimum expected monthly salary, 
        Minimummonthsalary = minimum_monthly_salary_checker(input("Enter your expected monthly salary (enter exit to continue ):"))
        
        
        # Preferred location, 
        menuDisplayType("locationdisplay")
        preferedlocation = preferredlocation_listadder(input("Enter your preferred location (1-56)(Enter exit to skip):"))
    
        
        # Industry interests (e.g fintech, cybersecurity), 
        Industry_interest = industrial_input_list_adder(input("Enter your Industry Interest (Enter exit to skip):"))
    
        # Company preference (e.g start-up, MNCs),
        menuDisplayType("company_preference") 
        Company_preference = company_preference_looper(input("Enter your company preference (Enter exit to skip):"))

        # Past experience (e.g previous SWE internship)
        past_experience = looping_pass_experience(
            input("Do you have past work experience? (Have/Exit): ")
        )

        

        user_input = {
            "Student_Profile":{
                "Cource_of_Study":courseOfStudy,
                "Year_of_Study":f'{userYear},{userTrimester}',
                "Avaliable_Intership_date":(
                    f"{startingdate:%d/%m/%Y} - {endingdate:%d/%m/%Y}"
                ),
                "Preferred_month":preferedstartedmonth,
                "Skills":Skills,
                "Preferred_Roles":preferedroles,
                "Minimum_monthly_Salary":Minimummonthsalary,
                "Preferred_location":preferedlocation,
                "Industry_interest":Industry_interest,
                "Company_preference":Company_preference,
                "past_experience":past_experience,
            }
        }
        return user_input

def initialize_student_profile_Json():
    STUDENT_PROFILE_JSON.parent.mkdir(parents=True, exist_ok=True)

    try:
        with open(STUDENT_PROFILE_JSON, "r", encoding="utf-8") as file:
            print(f'Student_Profile_Json,loaded Sucessfully')
            return json.load(file)
    except (FileNotFoundError, json.JSONDecodeError):
            print(f'Student_Profile_Json,Failed to load')
            return {}

def check_student_profile_json(User_profile):
    if not User_profile:
        return False
    else:
        return True

def create_a_student_profile_json():
    STUDENT_PROFILE_JSON.parent.mkdir(parents=True, exist_ok=True)
    if not STUDENT_PROFILE_JSON.is_file():
        with open(STUDENT_PROFILE_JSON, "w", encoding="utf-8") as file:
            json.dump({}, file)
    

def get_student_profile_json():
    student_profile = initialize_student_profile_Json()
    if check_student_profile_json(student_profile)==False:
        print("Creating a new student_profile_json")
        create_a_student_profile_json()
        student_profile = initialize_student_profile_Json()
        if STUDENT_PROFILE_JSON.is_file():
            print("Student_profile.json create sucessfully")
            return student_profile,True
        else:
            print("Unknown error occur attempting to retry")
            return student_profile,False
    else:
        return student_profile,True

def loadingScreenMenu(fileloadingchecker,menutype):
    if menutype == "loadingScreenMenu":
        print(f'The program is attempting to reload the student_profile please the system would try at least 3 times before stopping: this is the {fileloadingchecker}')
    elif menutype =="FalseToLoadMessage":
        print(f'Could not load the student_profile.json ,please check file integrity')

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
        print("User Input Added Sucessfully")
        return studentprofile,True
    else:
        print("User Input Failed to add")
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

def update_student_profile_json(studentprofile):
    if not isinstance(studentprofile, dict) or not isinstance(
        studentprofile.get("Student_Profile"), dict
    ):
        raise ValueError("studentprofile must contain a Student_Profile dictionary")

    profile = studentprofile["Student_Profile"]
    print("Current student profile:")
    menuDisplayType("update_display",profile)
    print("Please answer the questions again to update your profile.")

    updated_profile = Get_User_Input()
    updated_studentprofile = studentprofile.copy()
    updated_studentprofile["Student_Profile"] = updated_profile["Student_Profile"]
    add_student_profile_json(updated_studentprofile)
    print("Student profile updated successfully.")
    return updated_studentprofile

def input_validator_option(functionnumber):
    if functionnumber.isdigit()==False:
        print("Your input is not a integer , try again")
        return False
    functionnumber = int(functionnumber)
    if(functionnumber<1):
        print("Your input is incorrect please Try again")
        return False
    elif (functionnumber >4):
        print("Your input is incorrect please Try again")
        return False
    return True

def inputlooper(functionnumber):
    Trueorfalse = input_validator_option(functionnumber)
    while not Trueorfalse :
        functionnumber = input("Enter the option you choose :")
        Trueorfalse = input_validator_option(functionnumber)
    return int(functionnumber)

def inputmenucaller_1002(functionnumber,studentprofile={}):
    if functionnumber == 1:
        student_profile = update_student_profile_json(studentprofile)
        return True,student_profile
    elif functionnumber == 2:
        return True,student_profile
    elif functionnumber == 3:
        return True,student_profile
    elif functionnumber == 4:
        add_student_profile_json(studentprofile)
        print("Have a good day , Thanks")
        return False,studentprofile

def menu_caller_loop_1102(student_profile):
    continues = True
    while continues:
        menutypenumerical = menuprinter(student_profile)
        functionnumber = inputlooper(input("Enter the option you choose :"))
        continues,student_profile = inputmenucaller_1002(int(functionnumber),student_profile)
    return student_profile,continues

def menu_function_call_general(menutypenumerical):
    if menutypenumerical == "1001":
        student_profile = menu_function_caller_first_time()
        menutypenumerical = menuprinter(student_profile)
        return student_profile,True
    if menutypenumerical == "1002":
        student_profile,trueorfalse = get_student_profile_json()
        student_profile,continues = menu_caller_loop_1102(student_profile)
        return student_profile,continues

        
        

    