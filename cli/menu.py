from cli.screen import Screen
from cli.menu_option import MenuOption

class Menu(Screen):
    def __init__(self, title, context):
        super().__init__(context)
        self._title = title
        self._options = []
        self._running = False

    def add_option(self,label, action):
        self._options.append(MenuOption(label,action))

    def display(self):
        display = self._context.display
        display.heading(self._title)
        display.numbered_list([option.get_label() for option in self._options])
        display.line()
        
    def run(self):
        self._running = True                        
        while self._running:
            self.display()
            count = len(self._options)
            choice = self._context.input_handler.ask_int(f"Choose an option (1-{count}):", 1, count)
            option = self._options[choice - 1]      
            option.run()

    def stop(self):
        self._running = False