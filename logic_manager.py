# OutputAI will get the output from the AI manager
# It will be a dictionary of internship IDs and their corresponding match scores and recommended actions
# Example format: {"job_id": 1,"SkillsMatch": 0,"RoleMatch": 70,"IndustryInterestMatch": 50,"ExperienceMatch": 40,"SalaryMatch": 100,"WorkArrangementMatch": null,"LocationMatch": 100,"CompanyPreferenceMatch": 0}
# UserProfile references data from io manager
# It will be a dictionary of the user's profile information
# We assume that we wont have a history of the user output
# Example format: {"CourseOfStudy": "Applied Artificial Intelligence", "YearOfStudy": "Year 1, Semester 1", ...}
# DBReference is the database connection reference to the internship database

#Imports
import io_manager
import ai_manager
import data_manager
from io_manager import datetime
from calendar import monthrange

#functions

# Take in internship data type and what the user provided in IO manager
def addInternshipResultToDB(internshipResult):
    #Add the internship result to the database
    io_manager.addInternshipResult(internshipResult)

def salaryFlag(flags, internshipData, userProfile):
    #Check if the salary is below the user's expected minimum salary
    userSalary = userProfile["Student_Profile"]["Minimum_monthly_Salary"]
    if isinstance(userSalary, str):
        userSalary = 0
    if (internshipData["monthly_allowance"] < (userSalary - 200)):
        #If the user provided a minimum expected monthly salary and a listing's stated salary is below that by more than $200
        flags.append("Salary below expected minimum")
    
def durationFlag(flags, internshipData, userProfile):
    #Check if the duration of the internship matches the user's availability
    userAvaliableTimeDays = userProfile["Student_Profile"]["Avaliable_Intership_date"]
    internshipPeriodMonths = internshipData["duration_months"]
    startDateText, endDateText = userAvaliableTimeDays.split(" - ")
    startDate = datetime.strptime(startDateText.strip(), "%d/%m/%Y").date()
    endDate = datetime.strptime(endDateText.strip(), "%d/%m/%Y").date()
    
    # Add calendar months, accounting for shorter months such as February.
    monthIndex = startDate.month - 1 + internshipPeriodMonths
    targetYear = startDate.year + monthIndex // 12
    targetMonth = monthIndex % 12 + 1
    targetDay = min(
        startDate.day,
        monthrange(targetYear, targetMonth)[1],
    )
    required_end_date = startDate.replace(
        year=targetYear,
        month=targetMonth,
        day=targetDay,
    )
    
    if endDate > required_end_date:
        print("Availability is longer than the internship period")
    elif endDate < required_end_date:
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

#check if output to user is a single value or all the ratings (Pending)
def calculateScore(aiOutput):
    weightage = {"SkillsMatch": 0.25, "RoleMatch": 0.25, "IndustryInterestMatch": 0.125, "ExperienceMatch": 0.125, "SalaryMatch": 0.075, "WorkArrangementMatch": 0.075, "LocationMatch": 0.05, "CompanyPreferenceMatch": 0.05}
    totalWeight = 0
    weightedScore = 0

    for key, weight in weightage.items():
        score = aiOutput.get(key)
        if score is not None:
            weightedScore += score * weight
            totalWeight += weight

    if totalWeight == 0:
        return 0

    return weightedScore / totalWeight

