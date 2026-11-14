# One user's login details. The password is never stored: only a salted hash, kept as one
# string "salt$hash" in the users.password_hash column (so no extra salt column is needed).
# The class answers "is this the right password?" and never hands out the hash itself.
import hashlib
import secrets


class StudentLoginDetails:
    # PBKDF2 runs the hash many times, so guessing passwords from a stolen .db file is slow
    __HASH_ROUNDS = 200_000

    def __init__(self, user_id, user_role, username, password):
        # `password` is the STORED value from the database: "salt$hash", or None/"" for an account
        # made before login existed. The keyword stays `password` because DataManager._user_from_row
        # and StudentProfile build this class with password=row["password_hash"].
        self.__user_id = user_id
        self.__user_role = user_role
        self.__username = username
        self.__password_hash = password

    # ---- building a hash ----
    @staticmethod
    def hash_password(password, salt=None):
        """Return "salt$hash" for this password. A new random salt is made when none is given."""
        salt = salt or secrets.token_hex(16)
        digest = hashlib.pbkdf2_hmac("sha256", password.encode("utf-8"), bytes.fromhex(salt),
                                     StudentLoginDetails.__HASH_ROUNDS).hex()
        return f"{salt}${digest}"

    # ---- getters (there is no get_password: the hash never needs to leave this class) ----
    def get_user_id(self):
        return self.__user_id

    def get_user_role(self):
        return self.__user_role

    def get_username(self):
        return self.__username

    # ---- behaviour ----
    def verify_password(self, attempt):
        """True if `attempt` is this user's password."""
        if not self.__password_hash or "$" not in self.__password_hash:
            return False                      # no password set yet: nobody can log in as this user
        salt, _ = self.__password_hash.split("$", 1)
        return secrets.compare_digest(self.hash_password(attempt, salt), self.__password_hash)

    def change_password(self, new_password):
        """Replace the stored hash. (Saving it to the database is DataManager's job.)"""
        self.__password_hash = self.hash_password(new_password)

    def fetch_login_details(self):
        # Safe to show or log: no password and no hash
        return {
            "user_id": self.__user_id,
            "user_role": self.__user_role,
            "username": self.__username,
        }


Student_login_details = StudentLoginDetails
