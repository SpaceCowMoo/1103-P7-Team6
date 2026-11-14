class Flags:
    def __init__(self, flag_name: str, flag_value: bool):
        self.__flag_name = flag_name
        self.__flag_value = flag_value

    def get_flag_name(self):
        return self.__flag_name

    def get_flag_value(self):
        return self.__flag_value

    def set_flag_value(self, new_value: bool):
        self.__flag_value = new_value

    def fetch_flag_details(self):
        return {
            "flag_name": self.__flag_name,
            "flag_value": self.__flag_value,
        }
