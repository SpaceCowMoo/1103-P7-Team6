# OutputAI will get the output from the AI manager
# It will be a dictionary of internship IDs and their corresponding match scores and recommended actions
# Example format: {"job_id": 1,"SkillsMatch": 0,"RoleMatch": 70,"IndustryInterestMatch": 50,"ExperienceMatch": 40,"SalaryMatch": 100,"WorkArrangementMatch": null,"LocationMatch": 100,"CompanyPreferenceMatch": 0}
# UserProfile references data from io manager
# It will be a dictionary of the user's profile information
# We assume that we wont have a history of the user output
# Example format: {"CourseOfStudy": "Applied Artificial Intelligence", "YearOfStudy": "Year 1", ...}
# DBReference is the database connection reference to the internship database

#Imports
import io_manager
import ai_manager
import data_manager

#functions

def addInternshipResultToDB(conn, profile, internship_result, ai_output=None, overall_feedback=None):
    #Save one AI run (profile, internship result, AI output) to the database. Returns the new run_id
    return data_manager.save_run(conn, profile, internship_result, ai_output, overall_feedback)

def salaryFlag(flags, internshipData, userProfile):
    #Check if the salary is below the user's expected minimum salary
    userSalary = userProfile["Student_Profile"]["Minimum_monthly_Salary"]
    if isinstance(userSalary, str):
        userSalary = 0
    if (internshipData["monthly_allowance"] < (userSalary - 200)):
        #If the user provided a minimum expected monthly salary and a listing's stated salary is below that by more than $200
        flags.append("Salary below expected minimum")
    
def durationFlag(flags, internshipData, userProfile):
    user_duration_months = userProfile["Student_Profile"]["Duration"]
    internship_duration_months = internshipData["duration_months"]

    if internship_duration_months > user_duration_months:
        flags.append("Duration mismatch")

def skillFlag(flags, internshipData, userProfile):
    #Check if the user has the required skills for the internship
    # assuming that internshipData and userProfile are arrays of strings
    skillMatch = []
    for skill in userProfile["Student_Profile"]["Skills"]:
        if skill in internshipData["required_skills"]:
            skillMatch.append(f"Skill match: {skill}")
    if len(skillMatch) == 0:
        #If a listing requires skills that the student does not have
        flags.append("No matching skills")

def roleFlag(flags, internshipData, userProfile):
    #Check if the user has the preferred role for the internship
    # assuming that internshipData and userProfile are arrays of strings
    roleMatch = []
    for role in userProfile["Student_Profile"]["Preferred_Roles"]:
        if role in internshipData["job_title"]:
            roleMatch.append(f"Role match: {role}")
    if len(roleMatch) == 0:
        #If a listing requires roles that the student does not have
        flags.append("No matching roles")

def workarrangementFlag(flags, internshipData, userProfile):
    userWorkarrangment = userProfile["Student_Profile"]["Preferred_Work_Arrangement"]
    if internshipData["work_mode"] != userWorkarrangment:
        #if work_mode of job listing does not match users preference, raise flag
        flags.append("Work arrangement does not meet user's preference")
        #for review, do these functions take in job_id to search?

def locationFlag(flags, internshipData, userProfile):
    userLocation = userProfile["Student_Profile"]["Preferred_location"]
    if internshipData["location_district"] != userLocation:
        #if location does not match, raise flag
        flags.append("Location does not meet user's preference")
        #to change, student_profile location should be limited to North, East, South, West, Central

#output to IO manager
#Expecting recomendation to be a very long paragraph
def evaluateInternship(DBReference,aiScores, reccomendedActionsText, userProfile):
    ResultID = 1
    InternshipResult = {}
    for aiScore in aiScores:
        flags = []
        finalScore = calculateScore(aiScore)
        # A row in the internship database
        internshipData = data_manager.get_internship(DBReference, aiScore["job_id"])

        salaryFlag(flags, internshipData, userProfile)

        durationFlag(flags, internshipData, userProfile)

        skillFlag(flags, internshipData, userProfile)

        roleFlag(flags, internshipData, userProfile)

        InternshipResult[ResultID] = {
            "job_id": internshipData["job_id"],
            "overall_match_score": finalScore,
            "overall_feedback": reccomendedActionsText["overall_feedback"],
            "flags": flags,
        }
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
    for key, value in aiOutput.items():
        if value == None:
            aiOutput[key] = 0   #change NULL value to 0 to prevent TypeError during MatchScore calculation
        else:
            TotalScore += weightage[key]    #if an optional field has been filled in, add its weightage to TotalScore

    OverallMatchScore = (aiOutput["SkillsMatch"] * weightage["SkillsMatch"]) + (aiOutput["RoleMatch"] * weightage["RoleMatch"]) + (aiOutput["IndustryInterestMatch"] * weightage["IndustryInterestMatch"]) + (aiOutput["ExperienceMatch"] * weightage["ExperienceMatch"]) + (aiOutput["CompanyPreferenceMatch"] * weightage["CompanyPreferenceMatch"])
    return OverallMatchScore/TotalScore   #divide OverallScore over TotalScore to get final score out of 100%
