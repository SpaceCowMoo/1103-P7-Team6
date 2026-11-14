import models.student_resume as resume
import models.student_login_details as login
import models.listing as listing
import io_manager as io_manager



class StudentProfile:
    def __init__(
        self,
        name: str,
        age: int,
        student_id: str,
        Student_Resume: list[resume.StudentResume] | None = None,
        login_details: login.StudentLoginDetails | None = None,
        listings: list[listing.Listing] | None = None,
    ):
        self.__name = name
        self.__age = age
        self.__student_id = student_id
        self.__Student_Resume: list[resume.StudentResume] = Student_Resume if Student_Resume is not None else []
        self.__login_details: login.StudentLoginDetails | None = login_details
        self.__listings: list[listing.Listing] = listings if listings is not None else []

    def get_name(self):
        return self.__name

    def get_age(self):
        return self.__age

    def get_student_id(self):
        return self.__student_id

    def get_Student_Resume(self):
        return self.__Student_Resume

    def get_login_details(self):
        return self.__login_details

    def fetch_Student_Profile_details(self):
        return {
            "name": self.__name,
            "age": self.__age,
            "student_id": self.__student_id,
            "Student_Resume": [resume_item.fetch_Student_Resume_details() for resume_item in self.__Student_Resume],
            "login_details": self.__login_details.fetch_login_details() if self.__login_details is not None else None,
        }


    def add_Student_Resume(self, new_resume: resume.StudentResume):
        self.__Student_Resume.append(new_resume)

    def get_listings(self):
        return self.__listings

    def add_listing(self, new_listing: listing.Listing):
        self.__listings.append(new_listing)

    def remove_listing(self, listing_id: str):
        self.__listings = [
            current_listing for current_listing in self.__listings
            if current_listing.get_internship().get_job_id() != listing_id
        ]

    def fetch_listings(self):
        return [current_listing.fetch_listing_details() for current_listing in self.__listings]
