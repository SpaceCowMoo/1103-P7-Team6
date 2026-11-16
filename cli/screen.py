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
            self._display.error("No Results Found.")
            return
        for index, item in enumerate(items):
            show_function(item)                                         

            is_last = index == len(items) - 1                
            if is_last:
                break                                          

            if not self._input.ask_yes_no("View the next one? (Y/N):"):
                break

    # Read Only
    # We want app_context to be set up once.
    # Used @property here as I dont want to have a long connection to context
    @property
    def _display(self):
        return self._context.io.display

    @property
    def _input(self):
        return self._context.io.input

    @property
    def _validator(self):
        return self._context.io.validator

    @property
    def _data(self):
        return self._context.data

    @property
    def _user_id(self):
        # The logged-in user's ID. Every run and resume method in DataManager needs it.
        return self._context.current_user.get_login_details().get_user_id()

    # Show one past run: the summary card, then one card per match.
    # Used by PastRunsMenu (view a saved run) and MainMenu (show a brand-new run).
    def _show_run(self, run):
        self._display.run_summary(run)
        for result in run.get_results():
            self._display.run_result(result)
