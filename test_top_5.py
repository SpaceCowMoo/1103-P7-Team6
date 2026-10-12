
from ai_manager import validate_top_five_response

# Fake internship dataset
internships = [
    {"job_id": 1},
    {"job_id": 2},
    {"job_id": 3},
    {"job_id": 4},
    {"job_id": 5},
    {"job_id": 6}
]

# Fake Gemini response containing five internships
fake_response = {
    "selected_internships": [
        {
            "job_id": job_id,
            "SkillsMatch": 85,
            "RoleMatch": 90,
            "IndustryInterestMatch": 75,
            "ExperienceMatch": None,
            "CompanyPreferenceMatch": 100
        }
        for job_id in [1, 2, 3, 4, 5]
    ]
}

# TEST 1: Valid response
try:
    result = validate_top_five_response(fake_response, internships)
    print("TEST 1 PASSED: Five valid internships accepted")
    print("Selected job IDs:", [job["job_id"] for job in result])
except ValueError as e:
    print("TEST 1 FAILED:", e)

# TEST 2: Duplicate job ID
duplicate_response = {
    "selected_internships": [
        dict(job) for job in fake_response["selected_internships"]
    ]
}
duplicate_response["selected_internships"][4]["job_id"] = 1

try:
    validate_top_five_response(duplicate_response, internships)
    print("TEST 2 FAILED: Duplicate was accepted")
except ValueError as e:
    print("TEST 2 PASSED: Duplicate rejected:", e)

# TEST 3: Invalid score
invalid_score_response = {
    "selected_internships": [
        dict(job) for job in fake_response["selected_internships"]
    ]
}
invalid_score_response["selected_internships"][0]["SkillsMatch"] = 150

try:
    validate_top_five_response(invalid_score_response, internships)
    print("TEST 3 FAILED: Invalid score was accepted")
except ValueError as e:
    print("TEST 3 PASSED: Invalid score rejected:", e)
