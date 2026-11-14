class Internship:
    """One internship listing. DataManager reads and saves it"""

    def __init__(self, job_id, company_name, company_type, industry, job_title, relevant_course, monthly_allowance, work_mode, duration_months, required_skills, location_district, job_description):
        self.__job_id = job_id
        self.__company_name = company_name
        self.__company_type = company_type
        self.__industry = industry
        self.__job_title = job_title
        self.__relevant_course = relevant_course
        self.__monthly_allowance = monthly_allowance
        self.__work_mode = work_mode
        self.__duration_months = duration_months
        self.__required_skills = required_skills
        self.__location_district = location_district
        self.__job_description = job_description

    def get_job_id(self):
        return self.__job_id

    def get_company_name(self):
        return self.__company_name

    def get_company_type(self):
        return self.__company_type

    def get_industry(self):
        return self.__industry

    def get_job_title(self):
        return self.__job_title

    def get_relevant_course(self):
        return self.__relevant_course

    def get_monthly_allowance(self):
        return self.__monthly_allowance

    def get_work_mode(self):
        return self.__work_mode

    def get_duration_months(self):
        return self.__duration_months

    def get_required_skills(self):
        return self.__required_skills

    def get_location_district(self):
        return self.__location_district

    def get_job_description(self):
        return self.__job_description

    def fetch_internship_details(self):
        return {
            "job_id": self.__job_id,
            "company_name": self.__company_name,
            "company_type": self.__company_type,
            "industry": self.__industry,
            "job_title": self.__job_title,
            "relevant_course": self.__relevant_course,
            "monthly_allowance": self.__monthly_allowance,
            "work_mode": self.__work_mode,
            "duration_months": self.__duration_months,
            "required_skills": self.__required_skills,
            "location_district": self.__location_district,
            "job_description": self.__job_description,
        }
