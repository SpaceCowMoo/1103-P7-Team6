from abc import ABC, abstractmethod
#The parent of every screen. It stores the context and promises that every screen can loop
class Screen(ABC):

    # Context refers to AppContext object
    def __init__(self, context ):
        self._context = context

    # Ensure that all menu screens loop
    @abstractmethod
    def run(self):
        pass

    # Logic for flowing through pages such as internship listings
    def _page_through(self,items, show_function):
        if not items:
            self._context.display.error("No Results Found.")
            return
        for index, item in enumerate(items):
            show_function(item)                                         

            is_last = index == len(items) - 1                
            if is_last:
                break                                          

            if not self._context.input_handler.ask_yes_no("View the next one? (Y/N):"):
                break
