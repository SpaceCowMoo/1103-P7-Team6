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
    OverallMatchScore = (aiOutput["SkillsMatch"] * 0.25) + (aiOutput["RoleMatch"] * 0.25) + (aiOutput["IndustryInterestMatch"] * 0.125) + (aiOutput["ExperienceMatch"] * 0.125) + (aiOutput["SalaryMatch"] * 0.075) + (aiOutput["WorkArrangementMatch"] * 0.075) + (aiOutput["LocationMatch"] * 0.05) + (aiOutput["CompanyPreferenceMatch"] * 0.05)
    return OverallMatchScore
