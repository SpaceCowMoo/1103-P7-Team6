# app.py
from data_manager import load_csv, save_csv
import io_manager

def menu(typeofmenu):
    if typeofmenu == "Starting":
        print("---------------------")
        print("----Intern Link------")
        print("---------------------")
    elif typeofmenu == "Main":
        print("---------------------")
        print("----Intern Link------")
        print("---------------------")
        print("Option 1: Update Profile")
        print("Option 2: View Past Listing")
        print("Option 3: Search New Internship Listing")
        print("Option 4: Exit")


def main():
    userinput = io_manager.Get_User_Input()

main()
