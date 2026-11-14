# The first screen that the user must see is the log in or register option.
# Checks the DB. On success it stores the user in context.current_user and stops, so app.py
# knows to open the main menu. Exit leaves current_user as None.
from cli.menu import Menu
from cli.update_profile_screen import UpdateProfileScreen


class LoginMenu(Menu):
    MAX_ATTEMPTS = 3            # how many tries the SCREEN allows before going back to this menu

    def __init__(self, context):
        super().__init__("WELCOME TO INTERN LINK", context)
        self.add_option("Log in", self.login)
        self.add_option("Register a new account", self.register)
        self.add_option("Exit", self.stop)

    @property
    def _auth(self):
        return self._context.auth

    # ---- menu actions ----
    def login(self):
        for attempt in range(1, self.MAX_ATTEMPTS + 1):
            username = self._input.ask("Username:").strip()
            password = self._input.ask_password("Password:")
            user = self._auth.login(username, password)
            if user is not None:
                self.__finish(user, f"Welcome back, {user.get_login_details().get_username()}!")
                return
            # Same message for "no such user" and "wrong password" (see AuthService.login)
            left = self.MAX_ATTEMPTS - attempt
            self._display.error(f"Invalid username or password. {left} attempt(s) left.")
        self._display.message("Too many failed attempts. Returning to the login menu.")

    def register(self):
        username = self.__ask_new_username()
        if username is None:
            return                                   # they typed exit
        password = self.__ask_new_password()
        user = self._auth.register(username, password)
        self.__finish(user, f"Account created. Welcome, {username}!")

    # ---- helpers ----
    def __finish(self, user, message):
        self._context.current_user = user
        self._display.message(message)
        if self._data.load_resume(self._user_id) is None:
            # First time in: create the profile now, so every main menu option works straight away
            self._display.message("Let's set up your profile first.")
            UpdateProfileScreen(self._context).run()
        self.stop()                                  # leave the login menu; app.py opens the main menu

    def __ask_new_username(self):
        """Keep asking until AuthService accepts the username. None if the user types 'exit'."""
        while True:
            username = self._input.ask(
                "Choose a username (3-20 letters, numbers or _), or type 'exit' to cancel:").strip()
            if username.lower() == "exit":
                return None
            problem = self._auth.username_problem(username)
            if problem is None:
                return username
            self._display.error(problem)

    def __ask_new_password(self):
        """Ask twice, so a typo can't lock someone out of their brand-new account."""
        while True:
            password = self._input.ask_password(
                f"Choose a password (at least {self._auth.MIN_PASSWORD_LENGTH} characters):")
            problem = self._auth.password_problem(password)
            if problem:
                self._display.error(problem)
                continue
            if password != self._input.ask_password("Type the password again:"):
                self._display.error("Passwords do not match. Please try again.")
                continue
            return password
