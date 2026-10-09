#Imports
import io_manager
import ai_manager
import data_manager

#functions
# Take in internship data type and what the user provided in IO manager

def addInternshipResultToDB(internshipResult):
    #Add the internship result to the database
    io_manager.addInternshipResult(internshipResult)

def evaluateInternship(outputAI, userProfile):
    score = calculateScore(outputAI)
    flags = []
    ResultID = 0

    #output to IO manager
    InternshipResult = {
        ResultID:{
        "UserID": 0,
        "InternshipID": 0,
        "OverallMatchScore": 0,
        "Advice": ""
        }
    }

    internshipData = data_manager.get_internship(outputAI["InternshipID"])

    if (internshipData["monthly_allowance"] < (userProfile["expected_salary"] - 200)):
        #If the user provided a minimum expected monthly salary and a listing's stated salary is below that by more than $200
        flags.append("Salary below expected minimum")
    if (internshipData["duration"] != userProfile["availability"]):
        #If a listing's commitment duration does not match the student's availability
        flags.append("Duration mismatch")
    if (internshipData["required_skills"] != userProfile["skills"]):
        flags.append("Skills mismatch")
    if (internshipData["required_experience"] == "Yes" and userProfile["prior_experience"] == "No"):
        #If a listing explicitly requires prior internship experience and the student’s profile doesn't have relevant prior internship experience
        flags.append("Likely unsuitable")

    #Get AI generated advice based on the internship data, user profile, and any flags that were raised
    reccomendedActions = ai_manager.generateUserAdvice(internshipData, userProfile, flags)

    #Create internship recomendation result
    InternshipResult["InternshipID"] = internshipData["InternshipID"]
    InternshipResult["OverallMatchScore"] = score
    InternshipResult["Advice"] = reccomendedActions

    addInternshipResultToDB(InternshipResult)
    return InternshipResult

#check if output to user is a single value or all the ratings (Pending)
def calculateScore(aiOutput):
    #TotalScore tracks the weightage of fields used
    TotalScore = 0
    weightage = {"SkillsMatch": 0.25, "RoleMatch": 0.25, "IndustryInterestMatch": 0.125, "ExperienceMatch": 0.125, "SalaryMatch": 0.075, "WorkArrangementMatch": 0.075, "LocationMatch": 0.05, "CompanyPreferenceMatch": 0.05}
    for key, value in aiOutput.items():
        if value == None:
            #change NULL value to 0 to prevent TypeError during MatchScore calculation
            aiOutput[key] = 0
        else:
            #if an optional field has been filled in, add its weightage to TotalScore
            TotalScore += weightage[key]

    OverallMatchScore = (aiOutput["SkillsMatch"] * weightage["SkillsMatch"]) + (aiOutput["RoleMatch"] * weightage["RoleMatch"]) + (aiOutput["IndustryInterestMatch"] * weightage["IndustryInterestMatch"]) + (aiOutput["ExperienceMatch"] * weightage["ExperienceMatch"]) + (aiOutput["SalaryMatch"] * weightage["SalaryMatch"]) + (aiOutput["WorkArrangementMatch"] * weightage["WorkArrangementMatch"]) + (aiOutput["LocationMatch"] * weightage["LocationMatch"]) + (aiOutput["CompanyPreferenceMatch"] * weightage["CompanyPreferenceMatch"])
    return OverallMatchScore/TotalScore
    #divide OverallScore over TotalScore to get final score out of 100%

