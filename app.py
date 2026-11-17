import os
import sys
import time

from dotenv import load_dotenv
load_dotenv()

from data_manager import DataManager
from ai_manager import AIManager
from logic.auth_service import AuthService
from cli.app_context import AppContext
from cli.login_menu import LoginMenu
from cli.main_menu import MainMenu
from io_manager import IOManager


INTERNSHIP_DATA = os.getenv("INTERNSHIP_DATA")
DB_PATH = os.getenv("INTERNSHIP_DB")


# Main app excution
def main():
    # 1. Check the .env settings and the CSV before anything else
    missing = [name for name, value in (("INTERNSHIP_DATA", INTERNSHIP_DATA), ("INTERNSHIP_DB", DB_PATH)) if not value]
    if missing:
        sys.exit(f"Please set {', '.join(missing)} in your .env file")
    if not os.path.exists(INTERNSHIP_DATA):
        sys.exit(f"Missing internship data: {INTERNSHIP_DATA}")

    # 2. Create everything ONCE, then hand over to the screens
    data = DataManager.open(DB_PATH, INTERNSHIP_DATA) 
    try:
        io = IOManager()
        ai = AIManager()
        context = AppContext(data, io, ai, auth=AuthService(data))

        LoginMenu(context).run()          
        if context.is_logged_in():
            MainMenu(context).run()
    finally:
        data.close()                      # always close, even if something crashed

if __name__ == "__main__": main()
