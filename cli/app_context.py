# Called once in app.py
# This class holds everything the screens share
# data is reference to DataManager

class AppContext:

    def __init__(self, data, display, input_handler, auth=None, current_user = None):
        self.data = data
        self.display = display
        self.input_handler = input_handler
        self.auth = auth
        self.current_user = current_user

    def is_logged_in(self):
        if self.current_user == None:
            return False
        return True

