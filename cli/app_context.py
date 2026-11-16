# Called once in app.py
# This class holds everything the screens share
# data is reference to DataManager

class AppContext:

    # data = DataManager, io = IOManager (owns ConsoleDisplay, InputHandler and InputValidator)
    # The last 2 will be used for login features
    def __init__(self, data, io, auth=None, current_user = None):
        self.data = data
        self.io = io
        self.auth = auth
        self.current_user = current_user

    def is_logged_in(self):
        if self.current_user == None:
            return False
        return True
