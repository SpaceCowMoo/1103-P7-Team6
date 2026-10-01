#Imports
import data_manager
import io_manager
import ai_manager

#variables

#AI output variables
#To edit once I have an idea of what the AI output will look like
internshipName = ""
companyName = ""
SkillMatch = 0
RoleInterestMatch = 0
CareerGoalAlignment = 0
IndustryInterestMatch = 0
ExperienceMatch = 0
CompanyPreferenceMatch = 0

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

