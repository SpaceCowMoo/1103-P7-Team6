import csv
import json

def get_latest_profile(filename):
    latest_profile = None

    with open(filename, "r", newline="", encoding="utf-8") as file:
        reader = csv.DictReader(file)

        for row in reader:
            latest_profile = row

    return latest_profile

# Convert CSV values into Python data types
def convert_value(value):
    if value is None or value.strip() == "":
        return None

    try:
        return json.loads(value)
    except (json.JSONDecodeError, TypeError):
        return value

def get_ai_input(profile):
    ai_input = {
        "course_of_study": profile["Course_of_Study"],
        "year_of_study": profile["Year_of_Study"],
        "internship_duration": profile["Internship_Duration"],
        "preferred_month": profile["Prefer_month"],
        "skills": convert_value(profile["Skills"]),
        "preferred_roles": convert_value(profile["Prefer_Role"]),
        "minimum_monthly_salary": convert_value(
            profile["Minimum_monthly_salary"]
        ),
        "preferred_location": convert_value(profile["Preferred_location"]),
        "industry_interests": convert_value(profile["Industry_interests"]),
        "company_preference": convert_value(profile["Company preference"]),
        "past_experience": convert_value(profile["Past experience"])
    }

    return ai_input

if __name__ == "__main__":
    profile = get_latest_profile("data/student_profiles.csv")

    if profile is None:
        raise ValueError("No student profiles found.")

    ai_input = get_ai_input(profile)
    print(ai_input)