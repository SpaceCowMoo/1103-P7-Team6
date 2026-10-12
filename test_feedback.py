
from unittest.mock import patch
from ai_manager import generate_skill_gap_feedback

student_profile = {
    "course_of_study": "Software Engineering",
    "skills": ["Python"]
}

internships = [
    {
        "job_id": 1,
        "job_title": "Software Developer Intern",
        "required_skills": "Python, SQL, Git"
    }
]

mock_response = """
{
    "overall_feedback": {
        "points": [
            "Improve your SQL querying skills.",
            "Practise version control using Git.",
            "Build a software development portfolio."
        ]
    }
}
"""

with patch("ai_manager.call_gemini", return_value=mock_response):
    result = generate_skill_gap_feedback(
        None,
        student_profile,
        internships
    )

assert isinstance(result, dict)
assert len(result["points"]) == 3
assert all(isinstance(point, str) for point in result["points"])

print("TEST PASSED: Structured feedback works!")
