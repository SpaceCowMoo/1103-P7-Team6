# The hub: six options, each one creates the right screen and runs it.
# (On the UML this is the «create» dependency to the other screens.)

from cli.menu import Menu
from cli.internship_search import InternshipSearch
from cli.past_runs_menu import PastRunsMenu
from cli.delete_history_screen import DeleteHistoryScreen
from cli.update_profile_screen import UpdateProfileScreen
from logic.match_service import MatchService

class MainMenu(Menu):

    def __init__(self, context):
        super().__init__("INTERN LINK", context)
        self.add_option("Update profile", self.open_update_profile)
        self.add_option("View past runs", self.open_past_runs)
        self.add_option("Delete history", self.open_delete_history)
        self.add_option("Search for internships", self.open_search)
        self.add_option("Find internship matches (AI)", self.run_matches)
        self.add_option("Exit", self.exit_app)
        

    def open_update_profile(self):
        UpdateProfileScreen(self._context).run()

    def open_past_runs(self):
        PastRunsMenu(self._context).run()

    def open_delete_history(self):
        DeleteHistoryScreen(self._context).run()

    def open_search(self):
        InternshipSearch(self._context).run()

    def run_matches(self):
        """Hand the user's resume to the team's MatchService, then show the run it saved.
        MainMenu doesn't score anything itself: that's MatchService's job (S)."""
        resume = self._data.load_resume(self._user_id)
        if resume is None:
            self._display.message("Create your profile first (option 1), then try again.")
            return

        self._display.message("Finding your top 5 internships. This can take a minute...")
        try:
            run = MatchService(self._data, self._context.ai).find_matches(self._user_id, resume)
        except Exception as error:
            # e.g. MatchService not finished yet, no GEMINI_API_KEY, no internet, bad AI answer
            self._display.error(f"Could not find matches: {error}")
            return

        self._display.message(f"Saved as run #{run.get_run_id()}. You can view it again under 'View past runs'.")
        self._show_run(run)

    def exit_app(self):
        self._display.message("Closing App")
        self.stop()

