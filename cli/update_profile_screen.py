# Show the user's resume, let them pick fields (e.g. "2, 5", or 12 for all), ask for the
# new values and save. 

import io_manager                                   
from cli.screen import Screen
from models.past_internship import PastInternship
from models.student_resume import StudentResume


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

    # The validators are still functions in io_manager (they ask and re-ask by themselves).
    def __ask_course(self):
        io_manager.menuDisplayType("CourseDisplay")
        course = io_manager.course_of_study_input(self._input.ask("Enter your course of study (1-45):"))
        return {"Courses": course}

    def __ask_year(self):
        year = io_manager.validate_Year_of_Study(self._input.ask("Enter your year of study (1-6):"))
        return {"Year_of_Study": int(year)}        # the validator returns text like "2"

    def __ask_dates(self):
        start, end, months = io_manager.internship_duration_checker(
            self._input.ask("Enter your available internship dates (DD/MM/YYYY - DD/MM/YYYY):"))
        return {"Duration_of_internship": months,
                "available_internship_date": f"{start:%d/%m/%Y} - {end:%d/%m/%Y}"}

    def __ask_skills(self):
        skills = io_manager.continuousloopskills(self._input.ask("Enter a skill (or 'exit' to finish):"))
        return {"Skills": skills}

    def __ask_roles(self):
        roles = io_manager.continoous_Preferred_role(
            self._input.ask("Enter a preferred role (or 'exit' to finish):"))
        return {"Preferred_role": roles}

    def __ask_salary(self):
        salary = io_manager.minimum_monthly_salary_checker(
            self._input.ask("Enter your expected monthly salary (or 'exit' to skip):"))
        return {"Minimum_monthly_salary": float(salary)}     # the validator returns text like "1500.00"

    def __ask_work_arrangement(self):
        io_manager.menuDisplayType("PreferredWorkArrangement")
        arrangement = io_manager.preferred_work_location_looper(
            self._input.ask("Choose a work arrangement (1-3, or 'exit' to choose all):"))
        return {"preferred_work_arrangement": arrangement}

    def __ask_location(self):
        io_manager.menuDisplayType("LocationDisplay")
        locations = io_manager.preferredlocation_listadder(
            self._input.ask("Choose a preferred location (1-5, or 'exit' to choose all):"))
        return {"Preferred_location": locations}

    def __ask_industry(self):
        industries = io_manager.industrial_input_list_adder(
            self._input.ask("Enter an industry interest (or 'exit' to skip):"))
        return {"industry_interest": industries}

    def __ask_company(self):
        io_manager.menuDisplayType("CompanyPreference")
        preferences = io_manager.company_preference_looper(
            self._input.ask("Choose a company preference (1-5, or 'exit' to choose all):"))
        return {"company_preference": preferences}

    def __ask_experience(self):
        # io_manager returns the OLD format: {job_title: {"company_name", "job_title", "Date", "Duration",
        # "Job_Decription"}}. StudentResume wants a list of PastInternship objects, so convert each one.
        experiences = io_manager.looping_past_experience(
            self._input.ask("Do you have past work experience? (Y/N):"))
        past_internships = []
        for job in experiences.values():
            start_text, end_text = (part.strip() for part in job["Date"].split("-", maxsplit=1))
            past_internships.append(PastInternship(
                company_name=job["company_name"],
                role=job["job_title"],
                description=job["Job_Decription"],
                duration=job["Duration"],
                start_date=start_text,
                end_date=end_text,
            ))
        return {"Past_internships": past_internships}
