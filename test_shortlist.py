
from ai_manager import validate_shortlist_response

internships = [
    {"job_id": i, "duration_months": 6}
    for i in range(1, 13)
]

def make_result(count):
    return {
        "selected_internships": [
            {
                "job_id": i,
                "SkillsMatch": 80,
                "RoleMatch": 75,
                "IndustryInterestMatch": 70,
                "ExperienceMatch": None,
                "CompanyPreferenceMatch": 90
            }
            for i in range(1, count + 1)
        ]
    }

# Valid shortlist sizes
for count in (5, 7, 10):
    result = validate_shortlist_response(
        make_result(count),
        internships
    )
    assert len(result) == count

# Invalid shortlist sizes
for count in (4, 11):
    try:
        validate_shortlist_response(
            make_result(count),
            internships
        )
        raise AssertionError("Invalid shortlist was accepted")
    except ValueError:
        pass

# Duplicate internship IDs
duplicate = make_result(5)
duplicate["selected_internships"][1]["job_id"] = 1

try:
    validate_shortlist_response(duplicate, internships)
    raise AssertionError("Duplicate internship was accepted")
except ValueError:
    pass

print("TEST PASSED: Shortlist validation works!")
