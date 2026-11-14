#The only class that calls input(). It owns every "ask again until the answer is valid" loop, so no screen has to write one
from getpass import getpass # use python built in password

class InputHandler:
    
    def __init__(self, display):
        self.__display = display

    def ask(self, message):
        """Show a separator, then the question. Return what the user typed."""
        self.__display.line()
        return input(f"{message}\n> ")

    # Menu interface for password
    def ask_password(self, message):
        self.__display.line()
        return getpass(f"{message}\n> ")  

    # Menu interface for selecting a single option
    def ask_int(self, message, low=None, high=None):
        
        while True:
            text = self.ask(message).strip()       

            if not text.lstrip("-").isdigit():           
                self.__display.error("Please enter a whole number.")
                continue                                  

            number = int(text)                       

            if low is not None and number < low:
                self.__display.error(f"Please enter a number of at least {low}.")
                continue
            if high is not None and number > high: # which comparison means "too big"?
                self.__display.error(f"Please enter a number no bigger than {high}.")
                continue

            return number                               

    # Menu interface for selecting a y or n option
    def ask_yes_no(self, message):
        """Keep asking until the user types Y or N. Return True for Y, False for N."""
        while True:
            answer = self.ask(message).strip().lower()  
            if answer == "y":
                return True
            if answer == "n":
                return False
            self.__display.error("Please enter Y or N.")

    # Menu interface for selecting multiple options. So far they have not been mandatory
    def ask_number_list(self, message, low, high):
        """Read numbers like '1, 3, 5'. Return them as a list of ints, or None for 'exit'."""
        while True:
            text = self.ask(message).strip()
            if text.lower() == "exit":
                return None

            parts = [part.strip() for part in text.split(",")]    

            if all(part.isdigit() and low <= int(part) <= high for part in parts):
                numbers = [int(part) for part in parts]
                return list(dict.fromkeys(numbers)) 

            self.__display.error(f"Enter numbers from {low} to {high}, separated by commas.")
        
            