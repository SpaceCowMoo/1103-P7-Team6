import csv

def get_latest_profile(filename):
    latest_profile = None

    with open(filename, "r", newline="", encoding="utf-8") as file:
        reader = csv.DictReader(file)

        for row in reader:
            latest_profile = row

    return latest_profile

def get_ai_input(profile):
    ai_input = {
        "course_of_study": profile["Course_of_Study"],
        "year_of_study": profile["Year_of_Study"],
        "internship_duration": profile["Internship_Duration"],
        "preferred_month": profile["Prefer_month"],
        "skills": profile["Skills"],
        "preferred_roles": profile["Prefer_Role"],
        "minimum_monthly_salary": profile["Minimum_monthly_salary"],
        "preferred_location": profile["Preferred_location"],
        "industry_interests": profile["Industry_interests"],
        "company_preference": profile["Company preference"],
        "past_experience": profile["Past experience"]
    }

    return ai_input

profile = get_latest_profile("data/student_profiles.csv")
ai_input = get_ai_input(profile)
print(ai_input)