
from Student_Profile_Class import Student_Profile




class Student:
    def __init__(self, student_profile:list[Student_Profile]):
        self.__student_profile: list[Student_Profile] = student_profile

    def get_student_profile(self):
        return self.__student_profile

    def fetch_student_details(self):
        return {
            "student_profile": [profile.fetch_Student_Profile_details() for profile in self.__student_profile]
        }

    def add_student_profile(self, new_profile: Student_Profile):
        self.__student_profile.append(new_profile)