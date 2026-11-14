
from models.internship import Internship
from models.flags import Flags


class Listing:
    def __init__(self, internship: Internship, Flags: list[Flags] | None = None):
        self.__internship = internship
        self.__Flags: list[Flags] = Flags if Flags is not None else []

    def get_internship(self):
        return self.__internship

    def get_Flags(self):
        return self.__Flags

    def fetch_listing_details(self):
        return {
            "internship": self.__internship.fetch_internship_details(),
            "Flags": [flag.fetch_flag_details() for flag in self.__Flags],
        }

    def add_flag(self, new_flag: Flags):
        self.__Flags.append(new_flag)

    def remove_flag(self, flag_name: str):
        self.__Flags = [flag for flag in self.__Flags if flag.get_flag_name() != flag_name]


    