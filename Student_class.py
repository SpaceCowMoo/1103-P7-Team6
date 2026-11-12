
from Student_Profile_Class import StudentProfile


class Student:
    def __init__(self, student_profile: list[StudentProfile] | None = None):
        self.__student_profile: list[StudentProfile] = student_profile if student_profile is not None else []

    def get_student_profile(self):
        return self.__student_profile

    def fetch_student_details(self):
        return {
            "student_profile": [profile.fetch_Student_Profile_details() for profile in self.__student_profile]
        }

    def add_student_profile(self, new_profile: StudentProfile):
        self.__student_profile.append(new_profile)


Student_Profile = StudentProfile