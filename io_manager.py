from cli.console_display import ConsoleDisplay
from cli.input_handler import InputHandler
from cli.input_validator import InputValidator


class IOManager:
    """The IO Manager: every print() and input() in the app goes through the parts it owns."""

    def __init__(self):
        self.__display = ConsoleDisplay()
        self.__input = InputHandler(self.__display)
        self.__validator = InputValidator()

    @property
    def display(self):
        return self.__display

    @property
    def input(self):
        return self.__input

    @property
    def validator(self):
        return self.__validator