#Imports
import io_manager
import ai_manager
import data_manager

#functions
# Take in internship data type and what the user provided in IO manager

def addInternshipResultToDB(internshipResult):
    #Add the internship result to the database
    io_manager.addInternshipResult(internshipResult)

# OutputAI
# Example format: {1: {"SkillsMatch": 100, "RoleMatch": 100, ...}}
# UserProfile
# Example format: {"CourseOfStudy": "Applied Artificial Intelligence", "YearOfStudy": "Year 1, Semester 1", "InternshipDuration": "01/11/2023 - 30/11/2023", "PreferMonth": "February", "Skills": ["C Programming", "Python Programming", "Artificial Intelligence programming"], "PreferRole": ["Ict Intern"], "MinMonthlySalary": 500, "PreferredLocation": ["Chua Chu kang"], "IndustryInterests": ["Artificial Intelligence"], "CompanyPreference": "MNC", "PastExperience": {"Ict Intern": {"Date": "11/06/2024 - 24/06/2025", "JobDescription": "It is a work about a program"}}}

#output to IO manager
def evaluateInternship(DBReference,outputAI,userProfile):
    
    for key in outputAI:
        flags = []
        ResultID = 1
        finalScore = calculateScore(**outputAI[key])
        # A row in the internship database
        internshipData = data_manager.get_internship(DBReference, outputAI[key]["InternshipID"])
        reccomendedActions = outputAI[key]["NextAction"]

        # if (internshipData["monthly_allowance"] < (userProfile["Minimum_monthly_salary"] - 200)):
        #     #If the user provided a minimum expected monthly salary and a listing's stated salary is below that by more than $200
        #     flags.append("Salary below expected minimum")
        # if (internshipData["duration"] != userProfile["Internship_Duration"]):
        #     #If a listing's commitment duration does not match the student's availability
        #     flags.append("Duration mismatch")
        # if (internshipData["required_skills"] != userProfile["Skills"]):
        #     flags.append("Skills mismatch")
        # if (internshipData["required_experience"] == "Yes" and userProfile["Past_experience"] == "No"):
        #     #If a listing explicitly requires prior internship experience and the student’s profile doesn't have relevant prior internship experience
        #     flags.append("Likely unsuitable")

        InternshipResult = {
            ResultID:{
            "InternshipID": 0,
            "OverallMatchScore": 0,
            "Advice": ""
            }
        }

        
        InternshipResult[ResultID]["InternshipID"] = internshipData["job_id"]
        InternshipResult[ResultID]["OverallMatchScore"] = finalScore
        InternshipResult[ResultID]["Advice"] = reccomendedActions
        ResultID += 1

    print("Internship Result:", InternshipResult)
    return InternshipResult

#check if output to user is a single value or all the ratings (Pending)
def calculateScore(**AIScore):
    OverallMatchScore = (AIScore["SkillsMatch"] * 0.25) + (AIScore["RoleMatch"] * 0.25) + (AIScore["IndustryInterestMatch"] * 0.125) + (AIScore["ExperienceMatch"] * 0.125) + (AIScore["SalaryMatch"] * 0.075) + (AIScore["WorkArrangementMatch"] * 0.075) + (AIScore["LocationMatch"] * 0.05) + (AIScore["CompanyPreferenceMatch"] * 0.05)
    return OverallMatchScore

