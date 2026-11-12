import Student_Resume_Class as resume
import Past_internship_done_class as past_internship
import Student_Login_detail as login

    

class Student_Profile( login.Student_login_details):
    def __init__(self, name, age , student_id,Student_Resume:list[resume.Student_Resume], username, password):
        self.__name = name
        self.__age = age
        self.__student_id = student_id
        self.__Student_Resume:list[resume.Student_Resume] = Student_Resume

    def get_name(self):
        return self.__name

    def get_age(self):
        return self.__age       

    def get_student_id(self):
        return self.__student_id

    def get_Student_Resume(self):
        return self.__Student_Resume

    def fetch_Student_Profile_details(self):
        return {
            "name": self.__name,
            "age": self.__age,
            "student_id": self.__student_id,
            "Student_Resume": [resume.fetch_Student_Resume_details() for resume in self.__Student_Resume]
        }

    def add_Student_Resume(self, new_resume: resume.Student_Resume):
        self.__Student_Resume.append(new_resume)