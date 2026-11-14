#general function for io manager
from asyncio import log

from models.student_login_details import StudentLoginDetails
from models.student_profile import StudentProfile

consoleWidth_60 = 60
consoleWidth_55 = 55
profileFieldWidth = 28
courseCount = 0

def display_message(*args):
    """Display a message to the user"""
    print(*args)

def display_error(message):
    """Display an error message to the user"""
    display_message("Error:", message)

def get_user_input(prompt):
    """Get input from the user"""
    return input(prompt)

def print_heading(title):
        print("\n" + "=" * consoleWidth_60)
        print(f"{title:^{consoleWidth_60}}")
        print("=" * consoleWidth_60)


#Temporary function for student login and profile creation
def load_login_details(username , password , user_id , user_role):
    login_details = StudentLoginDetails(user_id, user_role, username, password)
    return login_details

def loaded_temporary_login_details():
    """Load temporary login details for testing"""
    username = "test_user"
    password = "test_pass"
    user_id = "12345"
    user_role = "student"
    return load_login_details(username, password, user_id, user_role)

def load_student_profile_none():
    """Load a temporary student profile with no resume or listings for testing"""
    name = "John Doe"
    age = 20
    student_id = "S123456"
    return StudentProfile(name, age, student_id)

def menu_type(menu_type):
    display_message("Temporary menu type:", menu_type)
    match menu_type:
        case "login":
            display_message("Welcome to InternLink!")
            display_message("Please Login to continue")
        case "CourseDisplay":
                    course_sections = [
                        ("Infocomm Technology", [
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
                        ]),
                        ("Engineering", [
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
                        ]),
                        ("Business, Communication and Design", [
                            "Accountancy",
                            "Aviation Management",
                            "Business and Infocomm Technology",
                            "Communication and Digital Media",
                            "Hospitality and Tourism Management",
                            "Integrated Studies in Technology and Management",
                            "Integrated Studies in Technology and Management with Specialisation in Supply Chain",
                        ]),
                        ("Food, Chemical and Biotechnology", [
                            "Dietetics and Nutrition",
                            "Food Business Management (Baking and Pastry Arts)",
                            "Food Business Management (Culinary Arts)",
                            "Food Technology",
                            "Pharmaceutical Engineering",
                        ]),
                        ("Health and Social Sciences", [
                            "Diagnostic Radiography",
                            "Nursing",
                            "Nursing (Pre-registration and Specialty Training)",
                            "Occupational Therapy",
                            "Physiotherapy",
                            "Radiation Therapy",
                            "Speech and Language Therapy",
                        ]),
                    ]
                    print_heading("COURSES OF STUDY")
                    course_number = 1
                    for section, courses in course_sections:
                        print(f"\n{section}")
                        for course in courses:
                            print(f"  {course_number:>2}. {course}")
                            course_number += 1
                    print("\n" + "=" * consoleWidth_60)
        case "First_Resume":
            display_message("Hi Welcome to internlink , please enter your first Student Resume")
        case "Main_Menu":
            display_message("Temp")

#Login functions
def login_Username_verification(username):
    # Placeholder for username verification logic
    # In a real application, this would check against a database or other data source
    login_details = loaded_temporary_login_details()
    if username == login_details.get_username():
        return True 
    else:
        return False

def login_Username_validation_outcome(username):
    if login_Username_verification(username):
        display_message(f"Username '{username}' is valid.")
        return True
    else:
        display_error(f"Username '{username}' is invalid. Please try again.")
        return False

def login_Password_verification(username, password):
    # Placeholder for password verification logic
    # In a real application, this would check against a database or other data source
    login_details = loaded_temporary_login_details()
    return login_details.get_password() == password

def login_Password_validation_outcome(username, password):
    if login_Password_verification(username, password):
        display_message(f"Password for username '{username}' is valid.")
        return True
    else:
        display_error(f"Password for username '{username}' is invalid. Please try again.")
        return False

def login():
    username = get_user_input("Enter your username: ")
    if not login_Username_validation_outcome(username):
        return
    password = get_user_input("Enter your password: ")
    if not login_Password_validation_outcome(username, password):
        return
    display_message(f"Username: {username}, Password: {password}")

def login_verification(username, password):
    if login_Username_verification(username) and login_Password_verification(username, password):
        display_message("Login successful!")
        return True
    else:
        display_error("Login failed. Please check your username and password.")
        return False

def login_loop():
    Timeout = 3
    while True and Timeout > 0:
        username = get_user_input("Enter your username: ")
        password = get_user_input("Enter your password: ")
        if login_verification(username, password):
            break
        else:
            Timeout -= 1
            display_message("Please try again.")


# Check Student Profile functions
def check_student_profile(student_profile: StudentProfile):
    if student_profile is None:
        display_error("Student profile is None.")
        return False
    if not isinstance(student_profile, StudentProfile):
        display_error("Invalid student profile object.")
        return False
    display_message("Student profile is valid.")
    return True

def check_student_profile_details(student_profile: StudentProfile):
    if not check_student_profile(student_profile):
        return False
    details = student_profile.fetch_Student_Profile_details()
    if not details.get("name") or not details.get("age") or not details.get("student_id"):
        display_error("Student profile is missing required details.")
        return False
    display_message("Student profile details are valid.")
    return True

def check_student_profile_resume(student_profile: StudentProfile):
    if not check_student_profile(student_profile):
        return False
    resume_list = student_profile.get_Student_Resume()
    if not resume_list:
        display_error("No Student Resume was found , Creating a new one.")
        return False
    display_message("Student resumes was found")
    return True

#student resume validator

#Add student_resume
def add_student_resume():

    menu_type("CourseDisplay")
    course_of_study = get_user_input("Enter the course of Student")    
    display_message("temp")

#menu function
def Student_profile_menu_decide(Student_profile):
    if not check_student_profile(Student_profile) or not check_student_profile_details(Student_profile):
        return display_error("Please Check Your Student Profile")
    if check_student_profile_resume(Student_profile):
        menu_type("First_Resume")
        add_student_resume()
    else:
        menu_type("Main_Menu")



def main():
    login_details = loaded_temporary_login_details()
    menu_type("login")
    login_loop()
    Student_profile = load_student_profile_none()
    Student_profile_menu_decide(Student_profile)

main()