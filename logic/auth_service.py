# Step 8 - All the account RULES in one place: what a valid username and password look like,
# registering and logging in. LoginMenu only asks questions and shows the answers (S).
import re

from models.student_login_details import StudentLoginDetails


class AuthService:
    USERNAME_PATTERN = re.compile(r"[A-Za-z0-9_]{3,20}")   # 3-20 letters, digits or _
    MIN_PASSWORD_LENGTH = 8

    def __init__(self, data):
        self.__data = data              # the DataManager

    def username_problem(self, username):
        """An error message if this username can't be used, or None if it's fine."""
        if not self.USERNAME_PATTERN.fullmatch(username):
            return "Username must be 3-20 letters, numbers or underscores."
        if self.__data.get_user_by_username(username) is not None:    # ignores upper/lower case
            return "That username is already taken."
        return None

    def password_problem(self, password):
        """An error message if this password is too weak, or None if it's fine."""
        if len(password) < self.MIN_PASSWORD_LENGTH:
            return f"Password must be at least {self.MIN_PASSWORD_LENGTH} characters."
        return None

    def register(self, username, password):
        """Create the account and return its StudentProfile. Raises ValueError if the details are invalid."""
        problem = self.username_problem(username) or self.password_problem(password)
        if problem:
            raise ValueError(problem)
        return self.__data.create_user(username,
                                       password_hash=StudentLoginDetails.hash_password(password))

    def login(self, username, password):
        """The user's StudentProfile if the username and password match, otherwise None.
        Returns None for BOTH "no such user" and "wrong password", so nobody can find out which
        usernames exist."""
        user = self.__data.get_user_by_username(username.strip())
        if user is None:
            return None
        if not user.get_login_details().verify_password(password):
            return None
        return user
