# Show the user's resume, let them pick fields (e.g. "2, 5", or 12 for all), ask for the
# new values and save. 

from cli.screen import Screen
from models.past_internship import PastInternship
from models.student_resume import StudentResume
from datetime import datetime


class UpdateProfileScreen(Screen):
    UPDATE_ALL = 12

    def __init__(self, context):
        super().__init__(context)
        # number -> (label the user sees, key in fetch_Student_Resume_details(), the method that asks for it)
        self.__fields = {
            1: ("Course of study", "Courses", self.__ask_course),
            2: ("Year of study", "Year_of_Study", self.__ask_year),
            3: ("Internship dates", "available_internship_date", self.__ask_dates),
            4: ("Skills", "Skills", self.__ask_skills),
            5: ("Preferred roles", "Preferred_role", self.__ask_roles),
            6: ("Minimum monthly salary", "Minimum_monthly_salary", self.__ask_salary),
            7: ("Work arrangement", "preferred_work_arrangement", self.__ask_work_arrangement),
            8: ("Preferred location", "Preferred_location", self.__ask_location),
            9: ("Industry interest", "industry_interest", self.__ask_industry),
            10: ("Company preference", "company_preference", self.__ask_company),
            11: ("Past experience", "Past_internships", self.__ask_experience),
        }

    def run(self):
        resume = self._data.load_resume(self._user_id)
        if resume is None:
            # First time: start from an empty resume and ask every field
            self._display.heading("CREATE YOUR PROFILE")
            resume = StudentResume()
            choices = list(self.__fields)
        else:
            choices = self.__pick_fields(resume)
            if choices is None:
                return

        for number in choices:
            label, key, ask_method = self.__fields[number]
            self._display.heading(f"UPDATE: {label.upper()}")
            changes = ask_method()
            resume.update_Student_Resume(**changes)     # the same line for every field: no if-statements

        self._data.save_resume(self._user_id, resume)    # save once, after every field is done
        self._display.message("Profile updated.")
        self.__show_resume(resume)

    # ---- helpers ----
    def __pick_fields(self, resume):
        """Show the resume and ask which fields to change. A list of field numbers, or None to cancel."""
        self.__show_resume(resume)
        if not self._input.ask_yes_no("Would you like to update your profile? (Y/N):"):
            return None
        choices = self._input.ask_number_list(
            f"Enter field numbers separated by commas (1-11), {self.UPDATE_ALL} for all, "
            "or 'exit' to cancel:", 1, self.UPDATE_ALL)
        if choices is None:
            self._display.message("No changes were made.")
            return None
        if self.UPDATE_ALL in choices:
            return list(self.__fields)
        return choices

    def __show_resume(self, resume):
        """Number each field the same way as the field table, so the user knows what to type."""
        details = resume.fetch_Student_Resume_details()
        fields = []
        for number, (label, key, ask_method) in self.__fields.items():
            fields.append((f"{number}. {label}", self.__as_text(key, details)))
        self._display.card("YOUR PROFILE", fields)

    @staticmethod
    def __as_text(key, details):
        """Turn one stored value into text for the card."""
        value = details.get(key)
        if key == "available_internship_date" and value:
            return f"{value} ({details.get('Duration_of_internship')} months)"
        if key == "Past_internships":
            return "\n".join(f"{job['role']} at {job['company_name']} ({job['start_date']} - {job['end_date']})"
                             for job in value) if value else None
        if key == "Minimum_monthly_salary":
            return f"${float(value):,.2f}" if value else None
        if isinstance(value, list):
            return ", ".join(str(item) for item in value) if value else None
        return value

    # ---- one method per field: each returns {update_Student_Resume parameter: new value} ----
    # Asking + re-asking goes through self._input; the rules come from self._validator (InputValidator).

    def __ask_course(self):
        courses = self._validator.COURSES
        self._display.numbered_list(courses)
        number = self._input.ask_int(f"Enter your course of study (1-{len(courses)}):", 1, len(courses))
        return {"Courses": courses[number - 1]}

    def __ask_year(self):
        year = self._input.ask_valid("Enter your year of study (1-6):", self._validator.parse_year)
        return {"Year_of_Study": year}

    def __ask_dates(self):
        start, end, months = self._input.ask_valid(
            "Enter your available internship dates (DD/MM/YYYY - DD/MM/YYYY):",
            self._validator.parse_internship_period)
        return {"Duration_of_internship": months, "available_internship_date": f"{start} - {end}"}

    def __ask_skills(self):
        skills = self._input.ask_list("[MANDATORY] Enter a skill:", "Skill",
                                      warn=self._validator.warn_text)
        return {"Skills": skills}

    def __ask_roles(self):
        roles = self._input.ask_list("Enter a preferred role (or 'exit' to finish):", "Role",
                                     required=False, warn=self._validator.warn_text)
        return {"Preferred_role": roles}

    def __ask_salary(self):
        salary = self._input.ask_valid("Enter your expected monthly salary (or 'exit' to skip):",
                                       self._validator.parse_salary)
        return {"Minimum_monthly_salary": salary}

    def __ask_work_arrangement(self):
        arrangements = self._input.ask_choices(
            "Choose work arrangements, e.g. 1, 2 (or 'exit' for no preference):",
            self._validator.WORK_ARRANGEMENTS)
        return {"preferred_work_arrangement": arrangements}

    def __ask_location(self):
        locations = self._input.ask_choices(
            "Choose preferred locations, e.g. 1, 5 (or 'exit' for all):", self._validator.LOCATIONS)
        return {"Preferred_location": locations}

    def __ask_industry(self):
        industries = self._input.ask_list("Enter an industry interest (or 'exit' to skip):", "Industry",
                                          required=False)
        return {"industry_interest": industries}

    def __ask_company(self):
        preferences = self._input.ask_choices(
            "Choose company preferences, e.g. 2, 3 (or 'exit' for all):", self._validator.COMPANY_PREFERENCES)
        return {"company_preference": preferences}

    def __ask_experience(self):
        past_internships = []
        adding = self._input.ask_yes_no("Do you have past work experience? (Y/N):")
        while adding:
            past_internships.append(self.__ask_one_experience())
            adding = self._input.ask_yes_no("Do you have another past experience? (Y/N):")
        past_internships.sort(key=lambda job: datetime.strptime(job.get_start_date(), "%d/%m/%Y"))
        return {"Past_internships": past_internships}

    def __ask_one_experience(self):
        """One filled-in PastInternship. Every question goes through InputHandler."""
        company = self._input.ask_valid("Enter your company name:", self._validator.required_text)
        role = self._input.ask_valid("Enter your job title:", self._validator.required_text)
        start, end, months = self._input.ask_valid(
            "Enter the period worked (DD/MM/YYYY - DD/MM/YYYY):", self._validator.parse_past_period)
        description = self._input.ask_valid("Enter a short job description:", self._validator.required_text)
        return PastInternship(company_name=company, role=role, description=description,
                              duration=months, start_date=start, end_date=end)
