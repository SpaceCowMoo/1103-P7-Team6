class StudentLoginDetails:
    def __init__(self, user_id, user_role, username, password):
        self.__user_id = user_id
        self.__user_role = user_role
        self.__username = username
        self.__password = password

    def get_user_id(self):
        return self.__user_id

    def get_user_role(self):
        return self.__user_role

    def get_username(self):
        return self.__username

    def get_password(self):
        return self.__password

    def fetch_login_details(self):
        return {
            "user_id": self.__user_id,
            "user_role": self.__user_role,
            "username": self.__username,
            "password": self.__password,
        }

    def add_login_details(self, username, password):
        self.__username = username
        self.__password = password

    def update_login_details(self, username=None, password=None):
        if username is not None:
            self.__username = username
        if password is not None:
            self.__password = password

    

Student_login_details = StudentLoginDetails
