#The only class that calls print(). Every heading, message, error and card goes through it, so changing how the app looks means editing one file.
WIDTH = 60

class ConsoleDisplay:
    
    def __init__(self):
        self.__width = WIDTH

    def line(self):
        print("="* self.__width)

    def heading(self, title):
        self.line()
        print(f"{title:^{self.__width}}")
        self.line()

    def message(self, *values):
        print(*values)

    def error(self, text):
        print(f"  ERROR : {text}")

    def numbered_list(self, items):
        for value, content in enumerate(items, start=1):
            print(f"{value} : {content}")
            
    def card(self, title, fields):
        self.heading(title)
        for label, value in fields:
            if value is None or value == "":
                value = "Not specified"
            print(f"{label}: {value}")
        self.line()

    def get_width(self):
        return self.__width