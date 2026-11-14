class PastInternship:
    def __init__(self, company_name, role, description, duration, start_date, end_date):
        self.__company_name = company_name
        self.__role = role
        self.__description = description
        self.__duration = duration
        self.__start_date = start_date
        self.__end_date = end_date

    def get_company_name(self):
        return self.__company_name

    def get_role(self):
        return self.__role

    def get_description(self):
        return self.__description

    def get_duration(self):
        return self.__duration

    def get_start_date(self):
        return self.__start_date

    def get_end_date(self):
        return self.__end_date

    def fetch_Past_internship_details(self):
        return {
            "company_name": self.__company_name,
            "role": self.__role,
            "description": self.__description,
            "duration": self.__duration,
            "start_date": self.__start_date,
            "end_date": self.__end_date,
        }

   