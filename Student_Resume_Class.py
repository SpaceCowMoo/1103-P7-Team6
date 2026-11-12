from Past_internship_done_class import PastInternship


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

    def add_Past_internship(self, Past_internship):
        self.__past_internships.append(Past_internship)

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


Student_Resume = StudentResume