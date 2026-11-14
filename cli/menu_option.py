# One line in a menu: the text the user sees and the method to run when they pick it.

class MenuOption:

    def __init__(self, label, action):
        self.__label = label
        self.__action = action

    def get_label(self):
        return self.__label

    def get_action(self):
        return self.__action

    def run(self):
        """Run the method this option was given."""
        self.__action()