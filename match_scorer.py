# match scorer contains the rubrics to calculate the individual match scores

class MatchScorer:
    def __init__(self):
        self.weightage = {
            "SkillsMatch": 0.3, 
            "RoleMatch": 0.3, 
            "IndustryInterestMatch": 0.2, 
            "ExperienceMatch": 0.15, 
            "CompanyPreferenceMatch": 0.05
        }

    def calculate_score(self, ai_output):
        overall_match_score = 0
        total_weight = 0

        for key, weight in self.weightage.items():
            value = ai_output.get(key)

            if value is not None:
                overall_match_score += value * weight
                total_weight += weight

        if total_weight == 0:
            return 0    #prevent division by zero

        return overall_match_score / total_weight