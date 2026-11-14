import os
import json
from pathlib import Path
import re
from datetime import datetime, timezone
from dateutil.relativedelta import relativedelta
import textwrap
from zoneinfo import ZoneInfo
from models.past_internship import PastInternship
import io_manager as io_manager

courseCount = 0

class StudentResume:
    def __init__(
        self,
        Courses: list[str] | None = None,
        Year_of_Study: int = 0,
        Duration_of_internship: int = 0,
        available_internship_date: str = "",
        Skills: list[str] | None = None,
        Preferred_role: list[str] | None = None,
        Minimum_monthly_salary: float = 0.0,
        Preferred_location: list[str] | None = None,
        preferred_work_arrangement: list[str] | None = None,
        industry_interest: list[str] | None = None,
        company_preference: list[str] | None = None,
        Past_internships: list[PastInternship] | None = None,
    ):
        self.__past_internships: list[PastInternship] = Past_internships if Past_internships is not None else []
        self.__Courses: list[str] = Courses if Courses is not None else []
        self.__Year_of_Study: int = Year_of_Study
        self.__Duration_of_internship: int = Duration_of_internship
        self.__available_internship_date: str = available_internship_date
        self.__Skills: list[str] = Skills if Skills is not None else []
        self.__Preferred_role: list[str] = Preferred_role if Preferred_role is not None else []
        self.__Minimum_monthly_salary: float = Minimum_monthly_salary
        self.__Preferred_location: list[str] = Preferred_location if Preferred_location is not None else []
        self.__preferred_work_arrangement: list[str] = preferred_work_arrangement if preferred_work_arrangement is not None else []
        self.__industry_interest: list[str] = industry_interest if industry_interest is not None else []
        self.__company_preference: list[str] = company_preference if company_preference is not None else []

    def get_Courses(self):
        return self.__Courses

    def get_Year_of_Study(self):
        return self.__Year_of_Study

    def get_Duration_of_internship(self):
        return self.__Duration_of_internship

    def get_available_internship_date(self):
        return self.__available_internship_date

    def get_Skills(self):
        return self.__Skills

    def get_Preferred_role(self):
        return self.__Preferred_role

    def get_Minimum_monthly_salary(self):
        return self.__Minimum_monthly_salary

    def get_Preferred_location(self):
        return self.__Preferred_location

    def get_preferred_work_arrangement(self):
        return self.__preferred_work_arrangement

    def get_industry_interest(self):
        return self.__industry_interest

    def get_company_preference(self):
        return self.__company_preference

    def get_Past_internships(self):
        return self.__past_internships

    def fetch_Student_Resume_details(self):
        return {
            "Courses": self.__Courses,
            "Year_of_Study": self.__Year_of_Study,
            "Duration_of_internship": self.__Duration_of_internship,
            "available_internship_date": self.__available_internship_date,
            "Skills": self.__Skills,
            "Preferred_role": self.__Preferred_role,
            "Minimum_monthly_salary": self.__Minimum_monthly_salary,
            "Preferred_location": self.__Preferred_location,
            "preferred_work_arrangement": self.__preferred_work_arrangement,
            "industry_interest": self.__industry_interest,
            "company_preference": self.__company_preference,
            "Past_internships": [internship.fetch_Past_internship_details() for internship in self.__past_internships],
        }

    def add_past_internship(self, past_experiences: dict | PastInternship):
        if isinstance(past_experiences, PastInternship):
            self.__past_internships.append(past_experiences)
            return
        if not isinstance(past_experiences, dict):
            raise TypeError("past_experiences must be a dictionary or PastInternship")

        new_internships = []
        for company_name, details in past_experiences.items():
            if not isinstance(details, dict):
                raise ValueError(f"Past internship for {company_name!r} must be a dictionary")

            role = details.get("job_title")
            date_range = details.get("Date")
            duration = details.get("Duration")
            description = details.get("Job_Description", details.get("Job_Decription"))
            if not all((company_name, role, date_range, description)) or duration is None:
                raise ValueError(f"Past internship for {company_name!r} is missing required details")

            try:
                start_text, end_text = date_range.split("-", maxsplit=1)
                start_date = datetime.strptime(start_text.strip(), "%d/%m/%Y")
                end_date = datetime.strptime(end_text.strip(), "%d/%m/%Y")
                duration = int(duration)
            except (AttributeError, TypeError, ValueError) as error:
                raise ValueError(f"Past internship for {company_name!r} has invalid dates or duration") from error

            if start_date > end_date:
                raise ValueError(f"Past internship for {company_name!r} starts after it ends")

            new_internships.append(
                PastInternship(
                    str(company_name).strip(),
                    str(role).strip(),
                    str(description).strip(),
                    duration,
                    start_date.strftime("%d/%m/%Y"),
                    end_date.strftime("%d/%m/%Y"),
                )
            )

        self.__past_internships.extend(new_internships)

    def add_Past_internship(self, past_experiences: dict | PastInternship):
        self.add_past_internship(past_experiences)

    def update_Student_Resume(
        self,
        Courses=None,
        Year_of_Study=None,
        Duration_of_internship=None,
        available_internship_date=None,
        Skills=None,
        Preferred_role=None,
        Minimum_monthly_salary=None,
        Preferred_location=None,
        preferred_work_arrangement=None,
        industry_interest=None,
        company_preference=None,
    ):
        if Courses is not None:
            self.__Courses = Courses
        if Year_of_Study is not None:
            self.__Year_of_Study = Year_of_Study
        if Duration_of_internship is not None:
            self.__Duration_of_internship = Duration_of_internship
        if available_internship_date is not None:
            self.__available_internship_date = available_internship_date
        if Skills is not None:
            self.__Skills = Skills
        if Preferred_role is not None:
            self.__Preferred_role = Preferred_role
        if Minimum_monthly_salary is not None:
            self.__Minimum_monthly_salary = Minimum_monthly_salary
        if Preferred_location is not None:
            self.__Preferred_location = Preferred_location
        if preferred_work_arrangement is not None:
            self.__preferred_work_arrangement = preferred_work_arrangement
        if industry_interest is not None:
            self.__industry_interest = industry_interest
        if company_preference is not None:
            self.__company_preference = company_preference

    def standard_validation_check_no(self, promptinput):
        return bool(promptinput and str(promptinput).strip())

    def standard_digit_validaton(self, value, digit_type: str = "int"):
        if not self.standard_validation_check_no(value):
            return False

        value = str(value).strip()
        try:
            if digit_type == "int":
                int(value)
            elif digit_type.lower() == "float":
                float(value)
            elif digit_type == "both":
                try:
                    int(value)
                except ValueError:
                    float(value)
            else:
                raise ValueError(f"Unsupported digit type: {digit_type}")
        except ValueError:
            return False
        return True

    def standard_numeric_checker(self, lowernum: float, uppernum: float, value):
        if not self.standard_digit_validaton(value, "float"):
            return False

        value = float(value)
        return 0 <= value and lowernum <= value <= uppernum

    def standard_number_to_String(self, listofinput: list[str], id: int | str):
        if not self.standard_digit_validaton(id, "int"):
            raise ValueError("The selection must be a whole number.")

        selection = int(id)
        if not self.standard_numeric_checker(1, len(listofinput), selection):
            raise ValueError(f"The selection must be between 1 and {len(listofinput)}.")
        return listofinput[selection - 1]

    def standard_validation_looper(
        self, validation_prompt: str, validationType: str, value
    ):
        validators = {
            "course": self.Course_validation,
            "salary": self.validating_minimum_monthly_salary,
            "work_location": self.validating_preferred_work_location,
            "preferred_location": self.validating_preferred_locations,
            "industry_interest": self.validate_Industry_interest,
            "industrical_interest": self.validate_Industry_interest,
            "company_preference": self.validate_company_preference,
            "company_preferrence": self.validate_company_preference,
        }
        validator_name = validationType.strip().casefold()
        validator = validators.get(validator_name)
        if validator is None:
            raise ValueError(f"Unknown validation type: {validationType}")

        while not validator(value):
            value = io_manager.prompt_input(validation_prompt)
        return value


    def course_of_study_words(self,course_of_study_id):
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
        return self.standard_number_to_String(courses, course_of_study_id)

    def Course_count(self):
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
        return len(courses)

    def Course_validation(self,Course:int):
        courseCount = self.Course_count()
        if not self.standard_validation_check_no(Course):
            print("Invalid input. Please enter a number corresponding to your course of study.")
            return False
        elif not self.standard_digit_validaton(Course, "int"):
            print("Invalid input. Please enter a number corresponding to your course of study.")
            return False
        elif not self.standard_numeric_checker(1, courseCount, Course):
            print(f"Invalid input. Please enter a number between 1 and {courseCount}.")
            return False
        return True

    def course_of_study_input(self,courseofStudy):
        self.course_of_study_words(10)
        courseofStudy = self.standard_validation_looper(
            "Please enter your course of study (1-45):",
            "course",
            courseofStudy,
        )
        return self.course_of_study_words(int(courseofStudy))


    def validate_Year_of_Study(self,year):
        if not self.standard_validation_check_no(year):
            match = None
        else:
            match = re.fullmatch(r"(?:Year\s*)?([1-6])", str(year).strip(), re.IGNORECASE)
        while match is None:
            print("Invalid input. Please enter a year between 1 and 6.")
            year = io_manager.prompt_input("Please enter your year of study (1-6):")
            if self.standard_validation_check_no(year):
                match = re.fullmatch(r"(?:Year\s*)?([1-6])", str(year).strip(), re.IGNORECASE)
            else:
                match = None
        return match.group(1)

    def check_Internship_Duration_format(self,internshipDuration):
        if not self.standard_validation_check_no(internshipDuration):
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


    def internship_duration_checker(self,internshipDuration):
        starting_date,ending_date,Total_month,is_valid = self.check_Internship_Duration_format(internshipDuration)

        while is_valid == False:
            internshipDuration = io_manager.prompt_input("Enter your available internship dates (DD/MM/YYYY - DD/MM/YYYY):")
            starting_date,ending_date,Total_month,is_valid = self.check_Internship_Duration_format(internshipDuration)
        return starting_date,ending_date,Total_month


    def validate_skill(self, skillsinput):
        while True:
            if not self.standard_validation_check_no(skillsinput):
                print("Invalid input. Please try again.")
            elif self.standard_digit_validaton(skillsinput, "int"):
                print("You entered a number.")
                if io_manager.Confirming_input(io_manager.prompt_input("Is this correct? (Y/N):")):
                    return skillsinput
            elif len(skillsinput) == 1:
                print("You entered a single character.")
                if io_manager.Confirming_input(io_manager.prompt_input("Is this correct? (Y/N):")):
                    return skillsinput
            else:
                return skillsinput

            skillsinput = io_manager.prompt_input("Enter a skill (or type 'exit' to finish):")

    def continuousloopskills(self,skillsinput):
        skillslist = []
        # Validate exit method
        while True:
            skillinput = self.validate_skill(skillsinput)
            skillinput = skillinput.strip()
            if skillinput.casefold() == "exit" and len(skillslist) <= 0:
                print("[MANDATORY] Please input in a skill.")
            elif skillinput.casefold() == "exit" and len(skillslist) > 0:
                return skillslist
            else:
                io_manager.append_unique_value(skillslist, skillinput, "Skill")
            skillsinput = io_manager.prompt_input("Enter another skill (type 'exit' to finish):")

    def validate_Preferred_role(self, preferred_role):
        areusure = True
        if not self.standard_validation_check_no(preferred_role):
            areusure = False
            print("Please enter a value.")
            return areusure
        elif self.standard_digit_validaton(preferred_role, "int"):
            print("You entered a number.")
            areusure = io_manager.Confirming_input(io_manager.prompt_input("Is this preferred role correct? (Y/N):"))
            return areusure
        elif len(preferred_role) == 1:
            print("You entered a single character. Is this correct?")
            areusure = io_manager.Confirming_input(io_manager.prompt_input("Is this preferred role correct? (Y/N):"))
            return areusure
        else:
            return areusure

    def checking_Preferred_role_input(self,Preferred_role):
        is_valid = self.validate_Preferred_role(Preferred_role)
        while is_valid == False:
            Preferred_role = io_manager.prompt_input("Enter a preferred role (or type 'exit' to finish):")
            is_valid = self.validate_Preferred_role(Preferred_role)
        return is_valid,Preferred_role

    def continoous_Preferred_role(self,Preferred_role):
        Preferred_rolelist = []
        is_valid,Preferred_role = self.checking_Preferred_role_input(Preferred_role)
        if Preferred_role.strip().lower() == "exit":
            return Preferred_rolelist
        io_manager.append_unique_value(Preferred_rolelist, Preferred_role, "Preferred role")
        while True:
            Preferred_role = io_manager.prompt_input("Enter another preferred role (or type 'exit' to finish):")
            _, Preferred_role = self.checking_Preferred_role_input(Preferred_role)
            if Preferred_role.lower().strip() == "exit":
                return Preferred_rolelist
            io_manager.append_unique_value(Preferred_rolelist, Preferred_role, "Preferred role")

    def validating_minimum_monthly_salary(self, minimum_month_salary):
        if not self.standard_validation_check_no(minimum_month_salary):
            print("Please enter a value.")
            return False
        elif minimum_month_salary.lower().strip() == "exit":
            return True
        elif not self.standard_digit_validaton(minimum_month_salary, "float"):
            print("Please enter a number.")
            return False
        minimum_month_salary = float(minimum_month_salary)
        if minimum_month_salary == 0:
            print("The value you entered is 0. Please input again.")
            return False
        elif minimum_month_salary < 0:
            print("The number cannot be negative. Please input again.")
            return False
        elif not self.standard_numeric_checker(0, 10000, minimum_month_salary):
            print("The value you entered is greater than 10,000. Please input again")
            return False
        else:
            return True

    def minimum_monthly_salary_checker(self,minimum_monthly_salary):
        minimum_monthly_salary = self.standard_validation_looper(
            "Enter your expected monthly salary (or type 'exit' to skip):",
            "salary",
            minimum_monthly_salary,
        )
        if minimum_monthly_salary.strip().casefold() != "exit":
            return f"{float(minimum_monthly_salary):.2f}"
        else:
            return 0.00

    def validating_preferred_work_location(self, preferred_work_locations):
        if not self.standard_validation_check_no(preferred_work_locations):
            print("Invalid value.")
            return False
        elif preferred_work_locations.lower().strip() == "exit":
            return True
        elif not self.standard_digit_validaton(preferred_work_locations, "int"):
            print("Please enter a number.")
            return False
        preferred_work_locations = int(preferred_work_locations)
        if not self.standard_numeric_checker(1, 3, preferred_work_locations):
            print("Please enter a valid number.")
            return False
        else:
            return True

    def validating_perferred_work_location_input(self,preferred_work_locations):
        preferred_work_locations = self.standard_validation_looper(
            "Enter a preferred work arrangement (1-3, or type 'exit' to finish):",
            "work_location",
            preferred_work_locations,
        )
        return preferred_work_locations.strip(), True

    def num_to_string_work_location(self,preferred_work_arrangement):
        arrangements = ["On-site", "Hybrid", "No Preference"]
        return self.standard_number_to_String(arrangements, preferred_work_arrangement)

    def preferred_work_location_looper(self,preferred_work_arrangement):
        arrangements = ["On-site", "Hybrid", "No Preference"]
        selected = []
        response = preferred_work_arrangement.strip()

        if response.casefold() == "exit":
            return [arrangements[0],arrangements[1]]

        while True:
            response, _ = self.validating_perferred_work_location_input(response)
            if response.casefold() == "exit":
                return selected
            if int(response)==3:
                selected = [arrangements[0],arrangements[1]]
                return selected
            arrangement = arrangements[int(response) - 1]
            io_manager.append_unique_value(selected, arrangement, "Work arrangement")
            response = io_manager.prompt_input(
                "Choose another work arrangement (1-3, or type 'exit' to finish):"
            )

    def pre_work_location_input_validation(self,preferred_work_locations):
        preferred_work_locations,isvalid = self.validating_perferred_work_location_input(preferred_work_locations)
        if isvalid != False:
            preferred_work_locations = int(preferred_work_locations)
            preferred_work_locations = self.num_to_string_work_location(preferred_work_locations)
        return preferred_work_locations


    def validating_preferred_locations(self, preferredlocations):
        if not self.standard_validation_check_no(preferredlocations):
            print("Invalid value.")
            return False
        elif  preferredlocations.lower().strip() == "exit":
            return True
        elif not self.standard_digit_validaton(preferredlocations, "int"):
            print("Please enter a number.")
            return False
        preferredlocations = int(preferredlocations)
        if not self.standard_numeric_checker(1, 5, preferredlocations):
            print("Please enter a valid number.")
            return False
        else:
            return True

    def validating_perferred_location_input(self,preferredlocations):
        return self.standard_validation_looper(
            "Choose a preferred location (1-5, or type 'exit' to finish):",
            "preferred_location",
            preferredlocations,
        )

    def preferredlocations_number_to_string(self,preferredlocationnumber):
        locations = ["North", "East", "South", "West", "Central"]
        return self.standard_number_to_String(locations, preferredlocationnumber)

    def preferredlocation_listadder(self,preferredlocations):
        locations = ["North", "East", "South", "West", "Central"]
        selected = []
        response = preferredlocations.strip()

        if response.casefold() == "exit":
            return locations

        while True:
            response = self.validating_perferred_location_input(response)
            if response.casefold() == "exit":
                print("Selected locations:", ", ".join(selected) or "None")
                return selected

            location = self.preferredlocations_number_to_string(response)
            io_manager.append_unique_value(selected, location, "Preferred location")
            print("\nSelected locations:", ", ".join(selected))
            response = io_manager.prompt_input(
            "Choose another preferred location (1-5, or type 'exit' to finish):"
        )

    def validate_Industry_interest(self, Industrial_intrest):
        if not self.standard_validation_check_no(Industrial_intrest):
            print("Please enter a valid response.")
            return False
        elif Industrial_intrest.strip().lower() == "exit":
            return True
        elif self.standard_digit_validaton(Industrial_intrest, "int"):
            print("You entered a number.")
            return io_manager.Confirming_input(io_manager.prompt_input("Is this industry interest correct? (Y/N):"))
        elif len(Industrial_intrest)==1:
            print("You entered a single character.")
            return io_manager.Confirming_input(io_manager.prompt_input("Is this industry interest correct? (Y/N):"))
        return True

    def Industrial_input_checker(self,industrial_interest):
        industrial_interest = self.standard_validation_looper(
            "Enter an industry interest (or type 'exit' to finish):",
            "industry_interest",
            industrial_interest,
        )
        return industrial_interest, True

    def industrial_input_list_adder(self,industrial_interest):
        industrial_interestlist = []
        while True:
            industrial_interest, _ = self.Industrial_input_checker(industrial_interest)
            if industrial_interest.strip().casefold() == "exit":
                return industrial_interestlist
            io_manager.append_unique_value(industrial_interestlist, industrial_interest, "Industry interest")
            industrial_interest = io_manager.prompt_input("Enter another industry interest (or type 'exit' to finish):")


    def validate_company_preference(self, company_perference):
        if not self.standard_validation_check_no(company_perference):
            print("Please enter a value.")
            return False
        elif company_perference.lower().strip() == "exit":
            return True
        elif not self.standard_digit_validaton(company_perference, "int"):
            print("Please enter a number.")
            return False
        company_perference = int(company_perference)
        if not self.standard_numeric_checker(1, 5, company_perference):
            print("Please enter a number between 1 and 5.")
            return False
        return True

    def company_preference_number_to_String(self,company_preference):
        company_preferences = [
            "Start-ups",
            "Multi-National Corporations (MNCs)",
            "Government",
            "Statutory Boards",
            "Small-to-Medium Enterprises (SMEs)",
        ]
        return self.standard_number_to_String(company_preferences, company_preference)

    def company_preference_checker(self,company_preference):
        return self.standard_validation_looper(
            "Choose a company preference (1-5, or type 'exit' to skip):",
            "company_preference",
            company_preference,
        )

    def company_preference_looper(self,company_preference):
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
            response = self.company_preference_checker(response)
            if response.casefold() == "exit":
                return selected

            preference = self.company_preference_number_to_String(response)
            io_manager.append_unique_value(selected, preference, "Company preference")
            print("\nSelected Company Preferences:", ", ".join(selected) or "None")
            response = io_manager.prompt_input(
            "Choose another company preference (1-5, or type 'exit' to finish):"
            )


    def validate_job_string_input(self,job_string, variable_name):
        while not job_string.strip():
            print(f"Please enter a value for {variable_name}.")
            job_string = io_manager.prompt_input(f"Enter {variable_name}:")
        return job_string.strip()

    def validate_past_experience(self,job_period_past):
        start_date = ""
        end_date = ""
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
            job_period_past = io_manager.prompt_input("Enter the period worked (DD/MM/YYYY - DD/MM/YYYY):")


        diff = relativedelta(end_date, start_date)
        total_months = (diff.years * 12) + diff.months
        return job_period_past.strip(),total_months

    def arrange_pass_experiences(self,experiences):
        return dict(
            sorted(
                experiences.items(),
                key=lambda experience: datetime.strptime(
                experience[1]["Date"].split("-", maxsplit=1)[0].strip(),
                "%d/%m/%Y",
            ),
        )
    )

    def looping_past_experience(self,pass_experience_input):
        experiences = {}
        response = pass_experience_input.strip().lower()

        while response not in {"y", "n"}:
            response = io_manager.prompt_input("Enter 'Y' to add past experience or 'N' to skip:").strip().lower()

        while response == "y":
            Company_name = self.validate_job_string_input(io_manager.prompt_input("Enter your Company:"), "job title"
                        )
            job_title = self.validate_job_string_input(
                io_manager.prompt_input("Enter your job title:"), "job title"
            )
            while any(existing.casefold() == job_title.strip().casefold() for existing in experiences):
                print("That job title has already been added; enter a different title.")
                job_title = self.validate_job_string_input(
                    io_manager.prompt_input("Enter a different job title:"), "job title"
                )
            dateofhiring = io_manager.prompt_input("Enter the period worked (DD/MM/YYYY - DD/MM/YYYY):")
            dateofhiring,duration = self.validate_past_experience(dateofhiring)
            jobdiscription = io_manager.prompt_input("Enter a short job description:")
            jobdiscription = self.validate_job_string_input(
            jobdiscription, "job description"
            )

            experiences[Company_name] = {
                "job_title":job_title,
                "Date": dateofhiring,
                "Duration":duration,
                "Job_Decription": jobdiscription,
            }
            response = io_manager.prompt_input("Do you have another past experience? (Y/N):").strip().lower()
            while response not in {"y", "n"}:
                response = io_manager.prompt_input("Enter 'Y' to add another or 'N' to finish:").strip().lower()

        return self.arrange_pass_experiences(experiences)


    def get_user_Student_Resume_input(self):
            loopmanger = True
            while loopmanger:

            #Mandatory Fields


                #Course of Study Input
                io_manager.menuDisplayType("CourseDisplay")
                userCourse = io_manager.prompt_input("Please enter your course of study (1-45):")
                courseOfStudy = self.course_of_study_input(userCourse)

                # Year of Study Input
                yearOfStudy = io_manager.prompt_input(
                    "Enter your year of study (1-6):"
                )
                userYear = self.validate_Year_of_Study(yearOfStudy)

                #Available internship duration input
                internshipDuration = io_manager.prompt_input(
                    "Enter your available internship dates (DD/MM/YYYY - DD/MM/YYYY):"
                )
                starting_date,ending_date,Total_month = self.internship_duration_checker(internshipDuration)

                #skills
                Skills = self.continuousloopskills(io_manager.prompt_input("Enter a skill:"))


                #optional Input

            #Preferred roles (e.g Marketing Assistant, Data Analyst),
                preferedroles = self.continoous_Preferred_role(
                    io_manager.prompt_input("Enter a preferred role (or type 'exit' to skip):")
                )



            # Minimum expected monthly salary,
                Minimummonthsalary = self.minimum_monthly_salary_checker(
                    io_manager.prompt_input("Enter your expected monthly salary (or type 'exit' to skip):")
                )


            # Preferred location,

                io_manager.menuDisplayType("PreferredWorkArrangement")
                preferred_work_arrangement = self.preferred_work_location_looper(
                    io_manager.prompt_input(
                        "Choose a work arrangement (1-3, or type 'exit' to choose all):"
                    )
                )

                io_manager.menuDisplayType("LocationDisplay")
                preferedlocation = self.preferredlocation_listadder(
                    io_manager.prompt_input("Choose a preferred location (1-5 to choose individually, or type 'exit' to choose All):")
                )


            # Industry interests (e.g fintech, cybersecurity),
                Industry_interest = self.industrial_input_list_adder(
                    io_manager.prompt_input("Enter an industry interest (or type 'exit' to skip):")
                )

            # Company preference (e.g start-up, MNCs),
                io_manager.menuDisplayType("CompanyPreference")
                Company_preference = self.company_preference_looper(
                    io_manager.prompt_input(
                        "Choose a company preference (1-5, or type 'exit' to choose all):"
                    )
                )

            # Past experience (e.g previous SWE internship)
                past_experience = self.looping_past_experience(
                    io_manager.prompt_input("Do you have past work experience? (Y/N):")
                )
                break

            student_resume = StudentResume(
                Courses=[courseOfStudy],
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
            )
            student_resume.add_past_internship(past_experience)
            return student_resume
