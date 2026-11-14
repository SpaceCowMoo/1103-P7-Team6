import unittest
from contextlib import redirect_stdout
from io import StringIO
from unittest.mock import patch

import data_manager
import io_manager_under_refactoring as io_manager
from database import Database
from Past_internship_done_class import PastInternship
from Student_Profile_Class import StudentProfile
from Student_Resume_Class import StudentResume


class LoginFlowTest(unittest.TestCase):
    def setUp(self):
        self.db = Database.open(":memory:")
        user = StudentProfile.create(
            self.db,
            "test_user",
            name="Test User",
            age=20,
            student_id="S123",
        )
        user_id = user.get_login_details().get_user_id()
        with self.db.transaction():
            self.db.execute(
                "UPDATE users SET password_hash = ? WHERE user_id = ?",
                ("test_pass", user_id),
            )
        self.conn = data_manager.get_conn(":memory:")
        data_manager.init_db(self.conn)

    def tearDown(self):
        self.db.close()
        self.conn.close()

    def test_main_opens_menu_for_authenticated_database_profile(self):
        with (
            patch.object(io_manager, "get_user_input", side_effect=["test_user", "test_pass"]),
            patch.object(io_manager, "menu_type"),
            patch.object(io_manager, "Student_profile_menu_decide") as profile_menu,
        ):
            io_manager.main(self.db, self.conn)

        profile_menu.assert_called_once()
        self.assertEqual(profile_menu.call_args.args[0].get_name(), "Test User")
        self.assertIs(profile_menu.call_args.args[1], self.conn)

    def test_main_does_not_open_menu_after_failed_login_attempts(self):
        responses = ["test_user", "wrong_pass"] * 3
        with (
            patch.object(io_manager, "get_user_input", side_effect=responses),
            patch.object(io_manager, "menu_type"),
            patch.object(io_manager, "Student_profile_menu_decide") as profile_menu,
        ):
            io_manager.main(self.db, self.conn)

        profile_menu.assert_not_called()

    def test_login_loop_loads_saved_resume(self):
        user = StudentProfile.get_by_username(self.db, "test_user")
        user_id = user.get_login_details().get_user_id()
        StudentResume(Courses="Computer Science", Skills=["Python"]).save(
            self.db, user_id
        )

        with patch.object(
            io_manager, "get_user_input", side_effect=["test_user", "test_pass"]
        ):
            student_profile = io_manager.login_loop(self.db)

        self.assertEqual(
            student_profile.get_Student_Resume()[0].get_Skills(), ["Python"]
        )

    def test_save_to_database_persists_latest_resume(self):
        student_profile = StudentProfile.get_by_username(self.db, "test_user")
        user_id = student_profile.get_login_details().get_user_id()
        student_profile.add_Student_Resume(
            StudentResume(Courses="Older course", Skills=["Excel"])
        )
        student_profile.add_Student_Resume(
            StudentResume(Courses="Current course", Skills=["Python"])
        )

        with redirect_stdout(StringIO()):
            saved = io_manager.Save_to_database(self.db, user_id, student_profile)

        loaded_resume = StudentResume.load(self.db, user_id)
        self.assertTrue(saved)
        self.assertEqual(loaded_resume.get_Courses(), "Current course")
        self.assertEqual(loaded_resume.get_Skills(), ["Python"])

    def test_save_to_database_rejects_profile_without_resume(self):
        student_profile = StudentProfile("Test User", 20, "S123")

        with patch.object(io_manager, "display_error") as display_error:
            saved = io_manager.Save_to_database(
                self.db, 1, student_profile
            )

        self.assertFalse(saved)
        display_error.assert_called_once_with(
            "Student profile has no resume to save."
        )

    def test_exit_option_saves_resume_to_database(self):
        student_profile = StudentProfile.get_by_username(self.db, "test_user")
        user_id = student_profile.get_login_details().get_user_id()
        student_profile.add_Student_Resume(
            StudentResume(Courses="Current course", Skills=["Python"])
        )

        with redirect_stdout(StringIO()):
            should_exit = io_manager.user_input_process(
                7, self.db, self.conn, user_id, student_profile
            )

        loaded_resume = StudentResume.load(self.db, user_id)
        self.assertTrue(should_exit)
        self.assertEqual(loaded_resume.get_Courses(), "Current course")
        self.assertEqual(loaded_resume.get_Skills(), ["Python"])

    def test_menu_type_handles_supported_menu_names(self):
        student_profile = StudentProfile("Test User", 20, "S123")
        menu_names = (
            "Starting",
            "login",
            "SecondTime",
            "Main_Menu",
            "First_Resume",
            "CourseDisplay",
            "LocationDisplay",
            "PreferredWorkArrangement",
            "CompanyPreference",
            "UpdateDisplay",
            "FilterInternships",
            "not-a-menu",
        )
        with redirect_stdout(StringIO()):
            for menu_name in menu_names:
                if menu_name == "UpdateDisplay":
                    io_manager.menu_type(menu_name, student_profile)
                else:
                    io_manager.menu_type(menu_name)

    def test_add_student_resume_appends_resume_object(self):
        student_profile = StudentProfile.get_by_username(self.db, "test_user")
        resume = StudentResume(Courses="Computer Science")

        with patch.object(io_manager, "Get_User_Input", return_value=resume):
            added = io_manager.add_student_resume(student_profile)

        self.assertTrue(added)
        self.assertEqual(student_profile.get_Student_Resume(), [resume])

    def test_profile_menu_adds_resume_when_profile_has_none(self):
        student_profile = StudentProfile("Test User", 20, "S123")

        with (
            patch.object(io_manager, "menu_type") as show_menu,
            patch.object(io_manager, "add_student_resume", return_value=True) as add_resume,
            patch.object(io_manager, "menu_input", return_value=True) as show_main_menu,
            redirect_stdout(StringIO()),
        ):
            result = io_manager.Student_profile_menu_decide(
                student_profile, self.conn
            )

        self.assertTrue(result)
        show_menu.assert_called_once_with("First_Resume")
        add_resume.assert_called_once_with(student_profile)
        show_main_menu.assert_called_once_with(student_profile, self.conn)

    def test_standard_validation_helpers_reject_invalid_values(self):
        self.assertFalse(io_manager.Standard_Checker("   "))
        self.assertTrue(io_manager.Standard_Checker(0))
        self.assertTrue(io_manager.Standard_number_checker("int", "12"))
        self.assertFalse(io_manager.Standard_number_checker("int", "12.5"))
        self.assertTrue(io_manager.Standard_number_checker("float", "12.5"))
        self.assertFalse(io_manager.Standard_number_checker("float", "nan"))
        self.assertFalse(io_manager.Standard_number_checker("unknown", "12"))
        self.assertTrue(io_manager.Standard_numerical_range_checker("5", 1, 5))
        self.assertFalse(io_manager.Standard_numerical_range_checker("0", 1, 5))
        self.assertFalse(io_manager.Standard_numerical_range_checker("invalid", 1, 5))

        self.assertEqual(io_manager.standard_num_to_String_adder(["A", "B"], "2"), "B")
        with self.assertRaises(ValueError):
            io_manager.standard_num_to_String_adder(["A", "B"], "3")

    def test_input_validators_use_shared_number_and_range_checks(self):
        with redirect_stdout(StringIO()):
            io_manager.course_of_study_words(1)
            self.assertTrue(io_manager.validate_course_of_study("45"))
            self.assertFalse(io_manager.validate_course_of_study("46"))
            self.assertTrue(io_manager.validating_minimum_monthly_salary("1250.50"))
            self.assertFalse(io_manager.validating_minimum_monthly_salary("10000.01"))
            self.assertTrue(io_manager.validating_preferred_work_location("3"))
            self.assertFalse(io_manager.validating_preferred_work_location("4"))
            self.assertTrue(io_manager.validating_preferred_locations("5"))
            self.assertFalse(io_manager.validating_preferred_locations("6"))

        self.assertEqual(io_manager.preferredlocations_number_to_string("5"), "Central")
        self.assertEqual(io_manager.company_preference_number_to_String("1"), "Start-ups")

    def test_view_all_profile_displays_profile_values(self):
        student_profile = StudentProfile.get_by_username(self.db, "test_user")
        student_profile.add_Student_Resume(StudentResume(Courses="Computer Science"))

        with patch.object(io_manager, "display_message") as display:
            displayed = io_manager.view_All_profile(student_profile)

        output = "\n".join(str(call.args[0]) for call in display.call_args_list)
        self.assertTrue(displayed)
        self.assertIn("Test User", output)
        self.assertIn("20", output)
        self.assertIn("S123", output)
        self.assertIn("Computer Science", output)

    def test_view_all_profile_rejects_non_profile(self):
        with patch.object(io_manager, "display_error") as display_error:
            displayed = io_manager.view_All_profile(None)

        self.assertFalse(displayed)
        display_error.assert_called_once_with("Invalid student profile object.")

    def test_getting_student_resume_displays_numbered_options(self):
        student_profile = StudentProfile.get_by_username(self.db, "test_user")
        resumes = [
            StudentResume(Courses="Computer Science"),
            StudentResume(Courses="Information Technology"),
        ]
        for resume in resumes:
            student_profile.add_Student_Resume(resume)

        with patch.object(io_manager, "display_message") as display:
            displayed_resumes = io_manager.getting_Student_resume(student_profile)

        self.assertEqual(displayed_resumes, resumes)
        messages = [call.args[0] for call in display.call_args_list]
        self.assertTrue(messages[0].startswith("1. "))
        self.assertIn("Computer Science", messages[0])
        self.assertTrue(messages[1].startswith("2. "))
        self.assertIn("Information Technology", messages[1])

    def test_updateprofile_applies_selected_fields_to_resume(self):
        resume = StudentResume(
            Courses="Old course",
            Year_of_Study=1,
            Minimum_monthly_salary=1000.0,
        )

        with (
            patch.object(io_manager, "get_user_input", side_effect=["1", "4", "1750.50"]),
            patch.object(io_manager, "menu_type"),
            patch.object(io_manager, "course_of_study_input", return_value="New course"),
        ):
            updated_resume = io_manager.updateprofile([1, 2, 6], resume)

        self.assertIs(updated_resume, resume)
        self.assertEqual(resume.get_Courses(), "New course")
        self.assertEqual(resume.get_Year_of_Study(), 4)
        self.assertEqual(resume.get_Minimum_monthly_salary(), 1750.50)

    def test_updateprofile_replaces_past_internships(self):
        old_internship = PastInternship(
            "Old Company", "Old Role", "Old work", 3, "01/01/2022", "01/04/2022"
        )
        new_internship = PastInternship(
            "New Company", "New Role", "New work", 4, "01/01/2023", "01/05/2023"
        )
        resume = StudentResume(Past_internships=[old_internship])

        with (
            patch.object(io_manager, "get_user_input", return_value="Y"),
            patch.object(
                io_manager,
                "looping_past_experience",
                return_value={"New Role": {"company_name": "New Company"}},
            ),
            patch.object(
                io_manager,
                "convert_past_experience_to_internships",
                return_value={"New Role": new_internship},
            ),
        ):
            io_manager.updateprofile([11], resume)

        self.assertEqual(resume.get_Past_internships(), [new_internship])

    def test_update_profile_selects_resume_and_updates_it(self):
        first_resume = StudentResume(Courses="First course")
        selected_resume = StudentResume(Courses="Old course")
        student_profile = StudentProfile(
            "Test User",
            20,
            "S123",
            Student_Resume=[first_resume, selected_resume],
        )

        with (
            patch.object(io_manager, "get_user_input", side_effect=["2", "1", "n", "3"]),
            patch.object(io_manager, "menu_type"),
            patch.object(io_manager, "course_of_study_input", return_value="Updated course"),
            redirect_stdout(StringIO()),
        ):
            result = io_manager.update_profile(student_profile)

        self.assertIs(result, selected_resume)
        self.assertEqual(first_resume.get_Courses(), "First course")
        self.assertEqual(selected_resume.get_Courses(), "Updated course")

    def test_update_input_chooser_supports_all_and_cancel(self):
        with (
            patch.object(io_manager, "get_user_input", return_value="12"),
            redirect_stdout(StringIO()),
        ):
            all_fields = io_manager.update_input_choser_input()
        self.assertEqual(all_fields, list(range(1, 12)))

        with (
            patch.object(io_manager, "get_user_input", return_value="13"),
            redirect_stdout(StringIO()),
        ):
            cancelled_fields = io_manager.update_input_choser_input()
        self.assertEqual(cancelled_fields, [])

    def test_menu_validator_accepts_exit_option(self):
        self.assertEqual(io_manager.menu_validator("7"), 7)

    def test_menu_input_exits_on_option_seven(self):
        student_profile = StudentProfile("Test User", 20, "S123")

        with (
            patch.object(io_manager, "get_user_input", return_value="7"),
            patch.object(io_manager, "menu_type"),
            patch.object(io_manager, "display_message") as display,
        ):
            should_exit = io_manager.menu_input(student_profile, self.conn)

        self.assertTrue(should_exit)
        display.assert_called_once_with("Goodbye.")


class MenuDatabaseOptionsTest(unittest.TestCase):
    def setUp(self):
        self.conn = data_manager.get_conn(":memory:")
        data_manager.init_db(self.conn)

    def tearDown(self):
        self.conn.close()

    def save_match(self):
        return data_manager.save_match(
            self.conn,
            {"student_profile": {}},
            [1, 2, 3, 4, 5],
            [90, 80, 70, 60, 50],
            [[], [], [], [], []],
            {"points": ["Test feedback"]},
        )

    def test_option_3_views_latest_match_using_connection(self):
        match_id = self.save_match()

        with patch.object(io_manager, "id_input", return_value=-1), patch.object(
            io_manager, "display_run_details"
        ) as display_run:
            result = io_manager.user_input_process(
                3, self.conn, StudentProfile("Test User", 20, "S123")
            )

        self.assertFalse(result)
        display_run.assert_called_once()
        self.assertIs(display_run.call_args.args[0], self.conn)
        self.assertEqual(display_run.call_args.args[1]["match_id"], match_id)

    def test_option_4_deletes_latest_match_using_connection(self):
        match_id = self.save_match()

        with (
            patch.object(
                io_manager, "get_user_input", side_effect=[str(match_id), "Y"]
            ),
            patch.object(io_manager, "Confirming_input", return_value=True),
            patch.object(io_manager, "display_run_summary"),
            redirect_stdout(StringIO()),
        ):
            result = io_manager.user_input_process(
                4, self.conn, StudentProfile("Test User", 20, "S123")
            )

        self.assertFalse(result)
        self.assertEqual(data_manager.list_matches(self.conn), [])

    def test_option_5_searches_internships_using_connection(self):
        data_manager.create_internship(
            self.conn,
            {
                "company_name": "Acme",
                "company_type": "MNC",
                "industry": "Software",
                "job_title": "Developer",
                "relevant_course": "Computer Science",
                "monthly_allowance": 1500,
                "work_mode": "Hybrid",
                "duration_months": 6,
                "required_skills": "Python",
                "location_district": "Tampines",
                "job_description": "Build software",
            },
        )

        with (
            patch.object(io_manager, "id_input", return_value=-1),
            patch.object(io_manager, "display_internship") as display_listing,
            redirect_stdout(StringIO()),
        ):
            result = io_manager.user_input_process(
                5, self.conn, StudentProfile("Test User", 20, "S123")
            )

        self.assertFalse(result)
        display_listing.assert_called_once()
        self.assertEqual(display_listing.call_args.args[0]["company_name"], "Acme")

    def test_option_6_converts_resume_and_mocks_ai_call(self):
        past_internship = PastInternship(
            "Acme",
            "Developer",
            "Built an internal tool",
            3,
            "01/01/2024",
            "31/03/2024",
        )
        resume = StudentResume(
            Courses="Computer Science",
            Year_of_Study=2,
            Duration_of_internship=6,
            available_internship_date="01/01/2025 - 30/06/2025",
            Skills=["Python"],
            Preferred_role=["Developer"],
            Minimum_monthly_salary=1200.0,
            Preferred_location=["East"],
            preferred_work_arrangement=["Hybrid"],
            industry_interest=["Technology"],
            company_preference=["MNC"],
            Past_internships=[past_internship],
        )
        student_profile = StudentProfile(
            "Test User", 20, "S123", Student_Resume=[resume]
        )
        expected_profile = {
            "student_profile": {
                "course_of_study": "Computer Science",
                "year_of_study": "2",
                "duration": 6,
                "available_internship_dates": "01/01/2025 - 30/06/2025",
                "skills": ["Python"],
                "preferred_roles": ["Developer"],
                "minimum_monthly_salary": 1200.0,
                "preferred_work_arrangement": ["Hybrid"],
                "preferred_location": ["East"],
                "industry_interest": ["Technology"],
                "company_preference": ["MNC"],
                "past_experience": {
                    "Developer": {
                        "company_name": "Acme",
                        "Date": "01/01/2024 - 31/03/2024",
                        "Duration": 3,
                        "Job_Decription": "Built an internal tool",
                    }
                },
            }
        }

        with (
            patch.object(
                io_manager.logic_manager, "find_matches", return_value=12
            ) as find_matches,
            patch.object(
                io_manager.data_manager,
                "get_match",
                return_value={"match_id": 12},
            ) as get_match,
            patch.object(io_manager, "display_run_details"),
            redirect_stdout(StringIO()),
        ):
            result = io_manager.user_input_process(6, self.conn, student_profile)

        self.assertFalse(result)
        find_matches.assert_called_once_with(self.conn, expected_profile)
        get_match.assert_called_once_with(self.conn, 12)


if __name__ == "__main__":
    unittest.main()
