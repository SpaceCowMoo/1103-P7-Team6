from unittest.mock import patch
from ai_manager import evaluate_multiple_internships


internships = [
    {"job_id": 1},
    {"job_id": 2},
    {"job_id": 3}
]


def fake_evaluate(client, profile, internship):
    if internship["job_id"] == 2:
        raise RuntimeError("Simulated Gemini failure")

    return {
        "job_id": internship["job_id"],
        "SkillsMatch": 80
    }


with patch("ai_manager.evaluate_internship", side_effect=fake_evaluate):
    results = evaluate_multiple_internships(
        None,
        {},
        internships
    )


print("Successful:", len(results["successful"]))
print("Failed:", len(results["failed"]))
print("Failed Job ID:", results["failed"][0]["job_id"])
print("Error:", results["failed"][0]["error"])