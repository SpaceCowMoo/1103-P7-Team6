
from ai_manager import get_ai_input, filter_by_duration

profile = {
    "course_of_study": "Information and Communications Technology (Software Engineering)",
    "year_of_study": "1",
    "duration": 4,
    "available_internship_dates": "13/11/2026 - 14/03/2027",
    "skills": ["Python", "C programming"],
    "preferred_roles": ["Programmer", "IT Specialist"],
    "minimum_monthly_salary": "1500.00",
    "preferred_work_arrangement": ["On-site", "Hybrid"],
    "preferred_location": ["North", "East"],
    "industry_interest": ["Information technology"],
    "company_preference": ["Start-ups"],
    "past_experience": {
        "Software Development Intern": {
            "Date": "01/06/2025 - 31/08/2025",
            "Job_Decription": "Developed and tested Python applications."
        }
    }
}

ai_input = get_ai_input(profile)

assert ai_input["course_of_study"] == profile["course_of_study"]
assert ai_input["internship_duration"] == 4
assert ai_input["available_internship_dates"] == profile["available_internship_dates"]
assert ai_input["preferred_roles"] == profile["preferred_roles"]
assert ai_input["industry_interests"] == profile["industry_interest"]
assert ai_input["past_experience"] == profile["past_experience"]
assert "preferred_month" not in ai_input

internships = [
    {"job_id": 1, "duration_months": 3},
    {"job_id": 2, "duration_months": 4},
    {"job_id": 3, "duration_months": 6},
    {"job_id": 4, "duration_months": 12}
]

eligible = filter_by_duration(ai_input, internships)

assert [job["job_id"] for job in eligible] == [1, 2]

print("TEST PASSED: New student profile mapping and duration filtering work!")
