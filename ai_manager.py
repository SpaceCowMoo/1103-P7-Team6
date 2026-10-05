import csv


def get_latest_profile(filename):
    latest_profile = None

    with open(filename, "r", newline="", encoding="utf-8") as file:
        reader = csv.DictReader(file)

        for row in reader:
            latest_profile = row

    return latest_profile

profile = get_latest_profile("data/student_profiles.csv")
print(profile)