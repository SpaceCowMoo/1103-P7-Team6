# app.py
from data_manager import load_csv, save_csv
import io_manager

def menu(typeofmenu):
    if typeofmenu == "Starting":
        print("---------------------")
        print("----Intern Link------")
        print("---------------------")



def main():
    menu("Starting")
    userinput = io_manager.Get_User_Input()
