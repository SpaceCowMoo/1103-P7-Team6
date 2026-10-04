#Imports
from data_manager import load_csv, save_csv
import io_manager
import ai_manager

#variables

#AI returns individual match scores for each of the following criteria
#AI filters listings based on mandatory fields
#Overall match score is calculated from the optional fields below:
internshipName = ""
companyName = ""
SkillsMatch = 0
RoleMatch = 0
IndustryInterestMatch = 0
ExperienceMatch = 0
SalaryMatch = 0
WorkArrangementMatch = 0
LocationMatch = 0
CompanyPreferenceMatch = 0
#They will follow the weightage using this formula:
OverallMatchScore = (SkillsMatch * 0.25) + (RoleMatch * 0.25) + (IndustryInterestMatch * 0.125) + (ExperienceMatch * 0.125) + (SalaryMatch * 0.075) + (WorkArrangementMatch * 0.075) + (LocationMatch * 0.05) + (CompanyPreferenceMatch * 0.05)
#If an optional field is left empty, its weightage will be redistributed proportionally among the remaining fields
#Sum up the weightage of fields that have non-empty values, divide OverallMatchScore by the sum to get final score

#Flags
salaryFlag = False
avaliabilityFlag = False
experienceFlag = False

#At least one multi-condition rule that uses two or more fields from the AI response
#functions
def salaryCheck():
    #If the user provided a minimum expected monthly salary and a listing's stated salary is below that by more than $200, Check it with a warning label
    return

def userAvaliabilityCheck():
    #If a listing's commitment duration does not match the student's availability, Check it as duration mismatch
    return

def experienceCheck():
    #If a listing explicitly requires prior internship experience and the student’s profile doesn't have relevant prior internship experience, Check as likely unsuitable
    return

def evaluate(record):
    return 

def score(record):
    return

def route(record):
    return

#check if output to user is a single value or all the ratings (Pending)
def finalScore():
    return

