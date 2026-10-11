#Imports
import io_manager
import ai_manager
import data_manager
import pandas as pd

#functions
# Take in internship data type and what the user provided in IO manager

def addInternshipResultToDB(conn, profile, internship_result, ai_output=None, overall_feedback=None):
    #Save one AI run (profile, internship result, AI output) to the database. Returns the new run_id
    return data_manager.save_run(conn, profile, internship_result, ai_output, overall_feedback)

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

#returns overall match score of a listing
def calculateScore(aiOutput):
    TotalScore = 0  #TotalScore tracks the weightage of fields used
    weightage = {
        "SkillsMatch": 0.3, 
        "RoleMatch": 0.3, 
        "IndustryInterestMatch": 0.2, 
        "ExperienceMatch": 0.15, 
        "CompanyPreferenceMatch": 0.05
        }
    
    job_id = aiOutput.pop("job_id")
    for key, value in aiOutput.items():
        if value == None:
            aiOutput[key] = 0   #change NULL value to 0 to prevent TypeError during MatchScore calculation
        else:
            TotalScore += weightage[key]    #if an optional field has been filled in, add its weightage to TotalScore

    OverallMatchScore = ((aiOutput["SkillsMatch"] * weightage["SkillsMatch"]) + (aiOutput["RoleMatch"] * weightage["RoleMatch"]) + (aiOutput["IndustryInterestMatch"] * weightage["IndustryInterestMatch"]) + (aiOutput["ExperienceMatch"] * weightage["ExperienceMatch"]) + (aiOutput["CompanyPreferenceMatch"] * weightage["CompanyPreferenceMatch"])) / TotalScore    #divide OverallScore over TotalScore to get final score out of 100%
    ListingScore = {"JobID": job_id, "OverallScore": OverallMatchScore}
    return ListingScore

#takes in a dict containing job_id and overall score, searches DB for listing details, apply flags accordingly and update listing score
def applyFlags(listingScore):
    file = pd.read_csv("internships.csv")
    listing = file.loc[file["job_id"] == listingScore["JobID"]].iloc[0]