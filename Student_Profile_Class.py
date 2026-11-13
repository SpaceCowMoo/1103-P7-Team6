import sqlite3

import Student_Resume_Class as resume
import Student_Login_detail as login
import listing_Class as listing


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

    # ---------- database: read and write the users table ----------
    # db is the Database object from Database.open()
    # The user's id is in the login details: user.get_login_details().get_user_id()

    @classmethod
    def create(cls, db, username, name=None, age=None, student_id=None, user_role="student"):
        """Save a new user and return it. Raises ValueError if the username is blank or taken"""
        username = username.strip()
        if not username:
            raise ValueError("Username cannot be blank")
        try:
            with db.transaction():
                user_id = db.insert("users", {
                    "username": username,
                    "user_role": user_role,
                    "name": name,
                    "age": age,
                    "student_id": student_id,
                })
        except sqlite3.IntegrityError as error:
            raise ValueError(f"Username already taken: {username}") from error
        return cls.get_by_id(db, user_id)

    @classmethod
    def get_by_id(cls, db, user_id):
        """One user, or None"""
        row = db.fetch_one("SELECT * FROM users WHERE user_id = ?", (user_id,))
        return cls._from_row(row) if row else None

    @classmethod
    def get_by_username(cls, db, username):
        """One user, or None. Ignores upper/lower case"""
        row = db.fetch_one("SELECT * FROM users WHERE username = ?", (username.strip(),))
        return cls._from_row(row) if row else None

    def delete(self, db):
        """Delete this user, and their resume and runs too. Returns True if it existed"""
        if self.__login_details is None:
            return False
        with db.transaction():
            cursor = db.execute("DELETE FROM users WHERE user_id = ?",
                                (self.__login_details.get_user_id(),))
        return cursor.rowcount > 0

    @classmethod
    def _from_row(cls, row):
        """One users row -> StudentProfile with its StudentLoginDetails
        (no login yet, so the password is None)"""
        login_details = login.StudentLoginDetails(
            user_id=row["user_id"],
            user_role=row["user_role"],
            username=row["username"],
            password=row["password_hash"],
        )
        return cls(name=row["name"], age=row["age"], student_id=row["student_id"],
                   login_details=login_details)


Student_Profile = StudentProfile
