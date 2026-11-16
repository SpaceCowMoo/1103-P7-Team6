# The rules for every profile answer. Part of the IO Manager (IOManager owns one).
# Contract for every parse_ method:
# takes the text the user typed -> returns the clean value, or raises ValueError("reason")
# Nothing here prints or reads input: InputHandler.ask_valid re-asks, ConsoleDisplay shows the reason.
from datetime import datetime

from dateutil.relativedelta import relativedelta


class InputValidator:
    # ---- the allowed options (screens show these as numbered menus) ----
    COURSES = [
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
        "Speech and Language Therapy",
    ]
    WORK_ARRANGEMENTS = ["On-site", "Hybrid"]
    LOCATIONS = ["North", "East", "South", "West", "Central"]
    COMPANY_PREFERENCES = [
        "Start-ups",
        "Multi-National Corporations (MNCs)",
        "Government",
        "Statutory Boards",
        "Small-to-Medium Enterprises (SMEs)",
    ]

    # ---- the limits (change a rule here, every screen follows) ----
    MAX_YEAR = 6
    MAX_SALARY = 10000
    MIN_INTERNSHIP_MONTHS = 3
    DATE_FORMAT = "%d/%m/%Y"

    # ---- one method per rule ----
    
    def required_text(self, text):
        """Ensure that user types in a something"""
        if not text:
            raise ValueError("Please enter a value.")
        return text

    def parse_year(self, text):
        """Convert input text to number for year"""
        # '2' or 'Year 2' -> 2
        number = text.casefold().removeprefix("year").strip()
        if not number.isdigit() or not 1 <= int(number) <= self.MAX_YEAR:
            raise ValueError(f"Please enter a year between 1 and {self.MAX_YEAR}.")
        return int(number)

    def parse_salary(self, text):
        """Validate salary input. """
        # '1500' -> 1500.0. 'exit' -> 0.0, meaning no minimum.
        if text.casefold() == "exit":
            return 0.0
        try:
            salary = float(text)
        except ValueError:
            raise ValueError("Please enter a number, e.g. 1500.")
        if not 0 < salary <= self.MAX_SALARY:
            raise ValueError(f"Please enter an amount above 0 and up to {self.MAX_SALARY:,}.")
        return salary

    def parse_internship_period(self, text):
        """Check if internship dates that last 3 months"""
        start_text, end_text, start, end = self.__split_period(text)
        if start < datetime.now():
            raise ValueError("Internship dates cannot be in the past.")
        months = self.__months_between(start, end)
        if months < self.MIN_INTERNSHIP_MONTHS:
            raise ValueError(f"The internship must be at least {self.MIN_INTERNSHIP_MONTHS} months long.")
        return start_text, end_text, months

    def parse_past_period(self, text):
        """Calculate total months of inputed period"""
        # e.g. Past dates: '01/01/2024 - 30/06/2024' -> ('01/01/2024', '30/06/2024', 5)
        start_text, end_text, start, end = self.__split_period(text)
        if end > datetime.now():
            raise ValueError(f"Please use dates on or before {datetime.now():{self.DATE_FORMAT}}.")
        return start_text, end_text, self.__months_between(start, end)

    def warn_text(self, text):
        """Check if user entered correctly: returns a warning for the user to confirm, or None."""
        if text.isdigit():
            return "You entered a number."
        if len(text) == 1:
            return "You entered a single character."
        return None

    # ---- Functions that are used to help control date format ----
    def __split_period(self, text):
        #'DD/MM/YYYY - DD/MM/YYYY' -> (start_text, end_text, start, end), start not after end.
        try:
            start_text, end_text = (part.strip() for part in text.split("-", maxsplit=1))
            start = datetime.strptime(start_text, self.DATE_FORMAT)
            end = datetime.strptime(end_text, self.DATE_FORMAT)
        except ValueError:
            raise ValueError("Enter the dates as DD/MM/YYYY - DD/MM/YYYY.")
        if start > end:
            raise ValueError("The start date must be on or before the end date.")
        return start_text, end_text, start, end

    def __months_between(self, start, end):
        difference = relativedelta(end, start)
        return difference.years * 12 + difference.months
