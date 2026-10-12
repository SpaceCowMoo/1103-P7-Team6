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

# DB NOTE (Johann): find_matches is the one function io_manager calls for menu option 5.
# It runs the whole flow: read internships from DB -> AI -> save_ai_result -> DB.
def find_matches(conn, student_profile):
    #Run the whole AI flow and save the result. Returns the new match_id
    #conn            = the database connection from app.setup()
    #student_profile = the dict io_manager loads: {"student_profile": {...}}

    # 1. Get every internship from the database (list of dicts)
    internships = data_manager.list_internships(conn, limit=-1)

    # 2. Turn the profile into the format the AI expects
    ai_input = ai_manager.get_ai_input(student_profile["student_profile"])

    # 3. Ask the AI for 5 to 10 internships + overall feedback
    client = ai_manager.configure_gemini()
    ai_result = ai_manager.run_ai_pipeline(client, ai_input, internships)

    # 4. Score them, add flags and save to the database
    return save_ai_result(conn, student_profile, ai_result)

def save_ai_result(conn, student_profile, ai_result):
    #Score each AI-selected internship and save them as one match. Returns the new match_id
    #ai_result is the output of ai_manager.run_ai_pipeline:
    # Fazila AI now returns this shape (5 to 10 internships, feedback as points):
    #{"selected_internships": {"internships": [{"job_id": 12, "SkillsMatch": 80, ...}, ...]},
    # "overall_feedback": {"points": ["...", "...", "..."]}}
    results = []
    for internship in ai_result["selected_internships"]["internships"]:
        flags = []
        current_score = calculateScore(internship)
        flag_deduction = 0
        # flag functions now also get conn, so they read the job from the database
        # was "deduction += 3", but the variable is flag_deduction (NameError)
        if salaryFlag(conn, flags, student_profile, internship["job_id"]):
            flag_deduction += 3
        if workarrangementFlag(conn, flags, student_profile, internship["job_id"]):
            flag_deduction += 3
        if locationFlag(conn, flags, student_profile, internship["job_id"]):
            flag_deduction += 3

        final_score = current_score - flag_deduction

        results.append({"job_id": internship["job_id"], "score": final_score, "flags": flags})

    # Best score first, so job_id_1 / score_1 in the database is the top match
    results.sort(key=lambda result: result["score"], reverse=True)
    # DB NOTE: the AI gives 5 to 10, but the database keeps exactly 5, so keep the best 5
    results = results[:5]

    job_ids = [result["job_id"] for result in results]
    scores = [result["score"] for result in results]
    flags = [result["flags"] for result in results]
    # DB NOTE:  save_match(conn, profile, job_ids, scores, flags, overall_feedback)
    #   job_ids  [12, 4, 30, 7, 2]                    5 ints, best first
    #   scores   [82.3, 70.0, 51.2, 35.0, 20.0]       5 numbers, same order
    #   flags    [["Salary below ..."], [], ...]      5 lists of text, same order
    #   overall_feedback is saved exactly as the AI gave it ({"points": [...]})
    # Read it back with data_manager.get_match(conn, match_id)
    return data_manager.save_match(conn, student_profile, job_ids, scores, flags, ai_result["overall_feedback"])

# this used to read internships.csv, but use database
# Now it reads the database. Returns a dict like
# {"job_id": 12, "monthly_allowance": 1500, "work_mode": "Hybrid", "location_district": "Tampines", ...}
# with numbers already as int, or None if the job_id doesn't exist.
def get_job_by_id(conn, job_id):
    return data_manager.get_internship(conn, job_id)

# DB NOTE: the student picks regions (North/East/South/West/Central) but the
# database stores the district (e.g. "Tampines"), so this maps every district in
DISTRICT_REGION = {
    "Woodlands": "North", "Yishun": "North", "Seletar": "North", "Ang Mo Kio": "North",
    "Sengkang": "North", "Hougang": "North", "Serangoon": "North",
    "Bedok": "East", "Changi": "East", "Pasir Ris": "East", "Tampines": "East", "Paya Lebar": "East",
    "Bukit Merah": "South", "Outram": "South", "Downtown Core": "South", "Queenstown": "South",
    "Clementi": "West", "Jurong East": "West", "Jurong West": "West", "Pioneer": "West", "Tuas": "West",
    "Bishan": "Central", "Kallang": "Central", "Novena": "Central", "Orchard": "Central",
    "Rochor": "Central", "Tanglin": "Central", "Toa Payoh": "Central",
}

def salaryFlag(conn, flags, userProfile, job_id):
    #Check if the salary is below the user's expected minimum salary
    # AI comment apprently: io_manager saves the salary as text like "1500.00" (or 0 when skipped),
    # int("1500.00") crashes, so use float()
    userSalary = float(userProfile["student_profile"]["minimum_monthly_salary"])
    if not userSalary:
        return False
    listing_data = get_job_by_id(conn, job_id)
    if listing_data["monthly_allowance"] < (userSalary - 200):
        #If the user provided a minimum expected monthly salary and a listing's stated salary is below that by more than $200
        flags.append("Salary below expected minimum by >$200")
        return True
    else:
        return False

def workarrangementFlag(conn, flags, userProfile, job_id):
    # this is a list, e.g. ["On-site", "Hybrid"], and the database work_mode is
    # one text, "On-site" or "Hybrid", so check "not in" instead of "!=".
    userWorkArrangment = userProfile["student_profile"]["preferred_work_arrangement"]
    if not userWorkArrangment or "No Preference" in userWorkArrangment:
        return False
    listing_data = get_job_by_id(conn, job_id)
    if listing_data["work_mode"] not in userWorkArrangment:
        #if work_mode of job listing does not match users preference, raise flag
        flags.append("Work arrangement does not meet user's preference")
        return True
    else:
        return False

def locationFlag(conn, flags, userProfile, job_id):
    # this is a list of regions, e.g. ["North", "East"], and the database
    # location_district is a district, e.g. "Tampines", so turn the district into its region first
    userLocation = userProfile["student_profile"]["preferred_location"]
    if not userLocation:
        return False
    listing_data = get_job_by_id(conn, job_id)
    region = DISTRICT_REGION.get(listing_data["location_district"])
    if region is not None and region not in userLocation:   # unknown district: don't flag
        #if location does not match, raise flag
        flags.append("Location does not meet user's preference")
        return True
    else:
        return False

#output to IO manager
#Expecting recomendation to be a very long paragraph
# def evaluateInternship(DBReference,aiScores, reccomendedActionsText, userProfile):
#     ResultID = 1
#     InternshipResult = {}
#     for aiScore in aiScores:
#         flags = []
#         finalScore = calculateScore(aiScore)
#         # A row in the internship database
#         internshipData = data_manager.get_internship(DBReference, aiScore["job_id"])

#         salaryFlag(flags, internshipData, userProfile)

#         durationFlag(flags, internshipData, userProfile)

#         skillFlag(flags, internshipData, userProfile)

#         roleFlag(flags, internshipData, userProfile)

#         InternshipResult[ResultID] = {
#             "job_id": internshipData["job_id"],
#             "overall_match_score": finalScore,
#             "overall_feedback": reccomendedActionsText["overall_feedback"],
#             "flags": flags,
#         }
#         ResultID += 1

#     print("Internship Result:", InternshipResult)
#     return InternshipResult

#returns overall match score of a listing
def calculateScore(aiOutput):
    weightage = {
        "SkillsMatch": 0.3, 
        "RoleMatch": 0.3, 
        "IndustryInterestMatch": 0.2, 
        "ExperienceMatch": 0.15, 
        "CompanyPreferenceMatch": 0.05
        }
<<<<<<< HEAD
    for key, value in aiOutput.items():
        try:
            if value == None:
                aiOutput[key] = 0   #change NULL value to 0 to prevent TypeError during MatchScore calculation
            else:
                TotalScore += weightage[key]    #if an optional field has been filled in, add its weightage to TotalScore
        except:
            continue
    OverallMatchScore = (aiOutput["SkillsMatch"] * weightage["SkillsMatch"]) + (aiOutput["RoleMatch"] * weightage["RoleMatch"]) + (aiOutput["IndustryInterestMatch"] * weightage["IndustryInterestMatch"]) + (aiOutput["ExperienceMatch"] * weightage["ExperienceMatch"]) + (aiOutput["CompanyPreferenceMatch"] * weightage["CompanyPreferenceMatch"])
=======
    # DB NOTE: the AI dict also has "job_id", so looping over aiOutput.items() hit
    # weightage["job_id"] -> KeyError. Same weighted average, but only the 5 score keys are read
    # and aiOutput is not changed.
    OverallMatchScore = 0
    TotalScore = 0  #TotalScore tracks the weightage of fields used
    for key, weight in weightage.items():
        value = aiOutput.get(key)
        if value is not None:   #null means the AI could not assess it, so skip it
            OverallMatchScore += value * weight
            TotalScore += weight    #if an optional field has been filled in, add its weightage to TotalScore
    if TotalScore == 0:
        return 0    #every score was null, avoid dividing by zero
>>>>>>> e1a3b90e1bcdf300d9c92c5f4f87e8ee41187c89
    return OverallMatchScore/TotalScore   #divide OverallScore over TotalScore to get final score out of 100%