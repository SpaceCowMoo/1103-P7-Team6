
from unittest.mock import patch
from ai_manager import run_ai_pipeline

# Fake internship records
internships = [
    {
        "job_id": i,
        "company_name": f"Company {i}",
        "job_title": "Data Analyst Intern",
        "required_skills": "Python, SQL",
        "job_description": "Analyse business data"
    }
    for i in range(1, 7)
]

student_profile = {
    "skills": ["Python"],
    "preferred_roles": ["Data Analyst"],
    "past_experience": {}
}

# Simulate Gemini's five selected internships and scores
fake_selection = [
    {
        "job_id": i,
        "SkillsMatch": 80,
        "RoleMatch": 90,
        "IndustryInterestMatch": None,
        "ExperienceMatch": None,
        "CompanyPreferenceMatch": None
    }
    for i in range(1, 6)
]

fake_feedback = {
    "overall_feedback": (
        "The student has a foundation in Python but could "
        "strengthen SQL and data analysis skills."
    )
}

with patch("ai_manager.select_top_five_internships",
           return_value=fake_selection) as mock_select, \
     patch("ai_manager.generate_skill_gap_feedback",
           return_value=fake_feedback) as mock_feedback:

    result = run_ai_pipeline(
        client=None,
        student_profile=student_profile,
        internships=internships
    )

    assert len(result["selected_internships"]) == 5
    assert result["selected_internships"][0]["job_id"] == 1
    assert result["selected_internships"][0]["company_name"] == "Company 1"
    assert result["selected_internships"][0]["SkillsMatch"] == 80
    assert result["overall_feedback"] == fake_feedback["overall_feedback"]

    mock_select.assert_called_once()
    mock_feedback.assert_called_once()

    print("TEST PASSED: Complete AI pipeline works correctly!")
    print("Selected job IDs:",
          [job["job_id"] for job in result["selected_internships"]])
    print("Overall feedback:", result["overall_feedback"])
