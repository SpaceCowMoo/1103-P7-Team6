# flag evaluator contains rules that will trigger and raise flags
# 3 points are deducted from individual match scores for each flag raised
from data_manager import DataManager

class FlagEvaluator:

    DISTRICT_REGION = {
    "Woodlands": "North", "Yishun": "North", "Seletar": "North", "Ang Mo Kio": "North",
    "Sengkang": "North", "Hougang": "North", "Serangoon": "North",
    "Bedok": "East", "Changi": "East", "Pasir Ris": "East", "Tampines": "East", "Paya Lebar": "East",
    "Bukit Merah": "South", "Outram": "South", "Downtown Core": "South", "Queenstown": "South",
    "Clementi": "West", "Jurong East": "West", "Jurong West": "West", "Pioneer": "West", "Tuas": "West",
    "Bishan": "Central", "Kallang": "Central", "Novena": "Central", "Orchard": "Central",
    "Rochor": "Central", "Tanglin": "Central", "Toa Payoh": "Central",
}

    def __init__(self, conn):
        self.conn = conn
        self.data_manager = DataManager(conn)

    def get_job_by_id(self, job_id):
        # Retrieve job listing data from db using job_id
        return self.data_manager.get_internship(self.conn, job_id)

    def salary_flag(self, user_profile: dict, job_id: int):
        user_salary = float(user_profile["student_profile"]["minimum_monthly_salary"])
        if not user_salary:
            return False
        
        listing_data = self.get_job_by_id(self.conn, job_id)
        if listing_data["monthly_allowance"] < (user_salary - 200):
            #If the user provided a minimum expected monthly salary and a listing's stated salary is below that by more than $200
            return True
        else:
            return False

    def work_arrangement_flag(self, user_profile: dict, job_id: int):
        user_work_arrangement = user_profile["student_profile"]["preferred_work_arrangement"]
        if not user_work_arrangement or "No Preference" in user_work_arrangement:
            return False
        
        listing_data = self.get_job_by_id(self.conn, job_id)
        if listing_data["work_mode"] not in user_work_arrangement:
            #if work_mode of job listing does not match users preference, raise flag
            return True
        else:
            return False

    def location_flag(self, user_profile: dict, job_id: int):
        user_location = user_profile["student_profile"]["preferred_location"]
        if not user_location:
            return False
        
        listing_data = self.get_job_by_id(self.conn, job_id)
        region = self.DISTRICT_REGION.get(listing_data["location_district"])
        if region is not None and region not in user_location:   # unknown district: don't flag
            #if location does not match, raise flag
            return True
        else:
            return False

    def evaluate_flags(self, user_profile: dict, job_id: int):
        flags = []
        point_deduction = 0

        if self.salary_flag(user_profile, job_id):
            flags.append("Salary below expected minimum by >$200")
            point_deduction += 3

        if self.work_arrangement_flag(user_profile, job_id):
            flags.append("Work arrangement does not meet user's preference")
            point_deduction += 3

        if self.location_flag(user_profile, job_id):
            flags.append("Location does not meet user's preference")
            point_deduction += 3

        return flags, point_deduction
