#The only class that calls input(). It owns every "ask again until the answer is valid" loop, so no screen has to write one
from getpass import getpass # use python built in password

class InputHandler:
    
    def __init__(self, display):
        self.__display = display

    def ask(self, message):
        """Show a separator, then the question. Return what the user typed."""
        self.__display.divider()
        return input(f"{message}\n> ")

    # Menu interface for password
    def ask_password(self, message):
        self.__display.line()
        return getpass(f"{message}\n> ")  

    # Menu interface for selecting a single option
    def ask_int(self, message, low=None, high=None):
        """Keep asking until the user types a number. Returns the number."""
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

    def ask_list(self, message, field_name, required=True, warn=None):
        """Keep asking until 'exit'. Returns a list without duplicates.
        warn: optional function text -> warning or None; a warning asks the user to confirm."""
        values = []
        while True:
            text = self.ask(message).strip()

            if text.casefold() == "exit":
                if values or not required:
                    return values
                self.__display.error(f"Please enter at least one {field_name.lower()}.")
                continue

            if not text:
                self.__display.error("Please enter a value.")
                continue

            if warn is not None:
                warning = warn(text)
                if warning and not self.ask_yes_no(f"{warning} Is this correct? (Y/N):"):
                    continue

            if any(existing.casefold() == text.casefold() for existing in values):
                self.__display.error(f"{field_name} already added; duplicates are not allowed.")
                continue

            values.append(text)
            message = f"Enter another {field_name.lower()} (or 'exit' to finish):"

    def ask_choices(self, message, choices):
        """Keep asking until 'exit'. Choices are pre-defined"""
        self.__display.numbered_list(choices)
        numbers = self.ask_number_list(message, 1, len(choices))
        if numbers is None:
            return list(choices)
        return [choices[number - 1] for number in numbers]

    def ask_valid(self, message, convert):
        """Keep asking until convert(text) succeeds. convert returns the value, or raises ValueError(reason)."""
        while True:
            text = self.ask(message).strip()
            try:
                return convert(text)
            except ValueError as error:
                self.__display.error(str(error))
            