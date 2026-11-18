# flag evaluator contains rules that will trigger and raise flags
# 3 points are deducted from individual match scores for each flag raised
# It only checks a StudentResume against an Internship; MatchService fetches the Internship.

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

    def salary_flag(self, resume, internship):
        try:
            minimum = resume.get_Minimum_monthly_salary()
            internship_salary = internship.get_monthly_allowance()

            if minimum is None or internship_salary is None:
                return False

            return float(internship_salary) < float(minimum) - 200

        except (AttributeError, TypeError, ValueError) as e:
            print(f"Error evaluating salary flag: {e}")
            return False
        
    def work_arrangement_flag(self, resume, internship):
        try:
            work_arrangement = resume.get_preferred_work_arrangement()
            internship_work_arrangement = internship.get_work_mode()

            if not work_arrangement or not internship_work_arrangement:
                return False

            return internship_work_arrangement not in work_arrangement

        except (AttributeError, TypeError) as e:
            print(f"Error evaluating work arrangement flag: {e}")
            return False
        
    def location_flag(self, resume, internship):
        try:
            location = resume.get_Preferred_location()
            internship_location = internship.get_location_district()

            if not location or not internship_location:
                return False

            region = self.DISTRICT_REGION.get(internship_location)

            if region is None:
                return False

            return region not in location

        except (AttributeError, TypeError) as e:
            print(f"Error evaluating location flag: {e}")
            return False

    def evaluate_flags(self, resume, internship):
        """resume is a StudentResume, internship is an Internship.
        Returns (list of flag names, points to deduct)"""
        flags = []
        point_deduction = 0

        if self.salary_flag(resume, internship):
            flags.append("Salary below expected minimum by >$200")
            point_deduction += 3

        if self.work_arrangement_flag(resume, internship):
            flags.append("Work arrangement does not meet user's preference")
            point_deduction += 3

        if self.location_flag(resume, internship):
            flags.append("Location does not meet user's preference")
            point_deduction += 3

        return flags, point_deduction
