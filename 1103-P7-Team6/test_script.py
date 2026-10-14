import logic_manager
from unittest.mock import patch

#Test 1 - hardcoded AI output
ai_output = {
    "job_id": 1,
    "SkillsMatch": 85,
    "RoleMatch": 90,
    "IndustryInterestMatch": 95,
    "ExperienceMatch": 70,
    "CompanyPreferenceMatch": 80
}
score = logic_manager.calculateScore(ai_output)
assert abs(score - 86.0) < 0.001, f"Expected 86.0, got {score}"
print("PASS: calculateScore")

#Test 2 - handling missing AI outputs
ai_output_missing = {
    "SkillsMatch": None,
    "RoleMatch": None,
    "IndustryInterestMatch": None,
    "ExperienceMatch": None,
    "CompanyPreferenceMatch": None
}
score = logic_manager.calculateScore(ai_output_missing)
assert score == 0, f"Expected 0, got {score}"
print("PASS: calculateScore with missing scores")

#sample student_profile
profile = {
    "student_profile": {
        "minimum_monthly_salary": "1500.00",
        "preferred_work_arrangement": ["On-site", "Hybrid"],
        "preferred_location": ["Central", "East"]
    }
}

#Test 3 - salary flag
#Mock the database lookup so no real database is needed
with patch("logic_manager.get_job_by_id") as mock_job:
    mock_job.return_value = {
        "monthly_allowance": 1200,
        "work_mode": "Hybrid",
        "location_district": "Tampines"
    }
    flags = []
    result = logic_manager.salaryFlag(None, flags, profile, 1)

    assert result is True, "Expected salary flag to be triggered"
    assert len(flags) == 1, f"Unexpected flags: {flags}"

print("PASS: salaryFlag")

#Test 4 - work arrangement flag
with patch("logic_manager.get_job_by_id") as mock_job:
    mock_job.return_value = {
        "monthly_allowance": 1500,
        "work_mode": "Remote",
        "location_district": "Tampines"
    }

    flags = []
    result = logic_manager.workarrangementFlag(None, flags, profile, 1)

    assert result is True, "Expected work arrangement flag"
    assert len(flags) == 1, f"Unexpected flags: {flags}"

print("PASS: workarrangementFlag")

#Test 5 - location flag
with patch("logic_manager.get_job_by_id") as mock_job:
    mock_job.return_value = {
        "monthly_allowance": 1500,
        "work_mode": "Hybrid",
        "location_district": "Woodlands"
    }

    flags = []
    result = logic_manager.locationFlag(None, flags, profile, 1)

    assert result is True, "Expected location flag"
    assert len(flags) == 1, f"Unexpected flags: {flags}"

print("PASS: locationFlag")

print("\nAll tests passed!")


# <HOW TO RUN>
# 1. docker build -t internlink-test .
# 2. docker run --rm internlink-test python test_script.py