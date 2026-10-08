from data_manager import load_csv, save_csv
import re
from datetime import datetime


def UserResponseidMaker():
    return 0

#Menu output styles
def menuDisplayType(typeofmenu):
    match typeofmenu:
        case "Starting":
            print("---------------------")
            print("----Intern Link------")
            print("---------------------")

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

        case _:
            print("Insert a proper display type")

#User input functions
def quitMenu():
    print("Exiting application")

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
    elif int(cource) < 1 or int(cource) > 46:
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
        
def skill_validation(skillsinput):
    if not skillsinput:
        return False
    elif skillsinput.isdigit()==True:
        areusure = input("Are u sure what u click in Correct, Example (Y/N): ")
        if areusure.strip().lower() == 'y':
            return True
        elif areusure.strip().lower() == 'n':
            return False
    return True

def skill_validate(skillsinput):
    is_valid = skill_validation(skillsinput)
    while is_valid == False:
        skillsinput = input("Please enter your skills (type exit to exit):")
        is_valid = skill_validation(skillsinput)
    return skillsinput , is_valid

def continuousloopskills(skillsinput):
    firsttime = 1
    skillslist = []
    skillinput , isvalid = skill_validate(skillsinput)
    skillslist.append(skillinput)
    while ((firsttime == 1)or (isvalid == True and skillinput.strip().lower() != "exit")):
        firsttime = firsttime+1
        skillsinput = input("Please enter your skills (type exit to exit):")
        skillinput , isvalid = skill_validate(skillsinput)
        skillslist.append(skillinput)
    return skillslist

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
            "Company preference":"MNC",
            "Past experience":
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
        menuDisplayType("Starting")

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
        preferedroles = input("Enter your preferred role :")
        
        
    
        # Minimum expected monthly salary, 
        Minimummonthsalary = input("Enter your expected monthly salary :")
        
        
        # Preferred location, 
        preferedlocation = input("Enter your preferred location :")
    
        
        # Industry interests (e.g fintech, cybersecurity), 
        Industry_interest = input("Enter your Industry Interest :")
    
        # Company preference (e.g start-up, MNCs), 
        Company_preference = input("Enter your company preference :")

        # Past experience (e.g previous SWE internship)
        past_experience  = input("Enter your past experience :")

        #Input id 
        input_id = "PD001"
        user_input = {
            input_id:{
                "Cource_of_Study":courseOfStudy,
                "Year_of_Study":f'{userYear},{userTrimester}',
                "Avaliable_Intership_date":f'{startingdate}-{endingdate}',
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