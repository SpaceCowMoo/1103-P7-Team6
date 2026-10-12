# OutputAI will get the output from the AI manager
# It will be a dictionary of internship IDs and their corresponding match scores and recommended actions
# Example format: {"job_id": 1,"SkillsMatch": 0,"RoleMatch": 70,"IndustryInterestMatch": 50,"ExperienceMatch": 40,"SalaryMatch": 100,"WorkArrangementMatch": null,"LocationMatch": 100,"CompanyPreferenceMatch": 0}
# UserProfile references data from io manager
# It will be a dictionary of the user's profile information
# We assume that we wont have a history of the user output
# Example format: {"student_profile": {"course_of_study": "Applied Artificial Intelligence", "year_of_study": "1", "duration": 4, "skills": [...], ...}}
# DBReference is the database connection reference to the internship database

#Imports
import ai_manager
import data_manager

#functions

# def addInternshipResultToDB(conn, profile, internship_result, ai_output=None, overall_feedback=None):
#     #Save one AI run (profile, internship result, AI output) to the database. Returns the new run_id
#     return data_manager.save_run(conn, profile, internship_result, ai_output, overall_feedback)

def save_ai_result(conn, student_profile, ai_result):
    #Score each AI-selected internship and save them as one match. Returns the new match_id
    #ai_result is the output of ai_manager.run_ai_pipeline:
    #{"selected_internships": [5 dicts with job_id + AI scores], "overall_feedback": "..."}
    results = []
    for internship in ai_result["selected_internships"]:
        results.append({"job_id": internship["job_id"], "score": calculateScore(internship)})

    # Best score first, so job_id_1 / score_1 in the database is the top match
    results.sort(key=lambda result: result["score"], reverse=True)

    job_ids = [result["job_id"] for result in results]
    scores = [result["score"] for result in results]
    return data_manager.save_match(
        conn, student_profile, job_ids, scores, ai_result["overall_feedback"])

def get_job_by_id(job_id, csv_file='internships.csv'):
    with open(csv_file, 'r') as file:
        read_file = csv.DictReader(file)
        for row in read_file:
            if row['job_id'] == str(job_id):
                return row
    return None

def salaryFlag(flags, userProfile, job_id):
    #Check if the salary is below the user's expected minimum salary
    userSalary = int(userProfile["student_profile"]["minimum_monthly_salary"])
    if not userSalary:
        return False
    listing_data = get_job_by_id(job_id)
    if listing_data["monthly_allowance"] < (userSalary - 200):
        #If the user provided a minimum expected monthly salary and a listing's stated salary is below that by more than $200
        flags.append("Salary below expected minimum by >$200")
        return True
    else:
        return False

def workarrangementFlag(flags, userProfile, job_id):
    userWorkarrangment = userProfile["student_profile"]["preferred_work_arrangement"]
    if not userWorkarrangement:
        return False
    listing_data = get_job_by_id(job_id)
    if listing_data["work_mode"] != userWorkarrangment:
        #if work_mode of job listing does not match users preference, raise flag
        flags.append("Work arrangement does not meet user's preference")
        return True
    else:
        return False

def locationFlag(flags, userProfile, job_id):
    userLocation = userProfile["student_profile"]["preferred_location"]
    if not userLocation:
        return False
    listing_data = get_job_by_id(job_id)
    if listing_data["location_district"] != userLocation:
        #if location does not match, raise flag
        flags.append("Location does not meet user's preference")
        return True
    else:
        return False

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