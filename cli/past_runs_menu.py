# The logged-in user's search history: view latest, browse all, view one. (Deleting is DeleteHistoryScreen.)
# DataManager already filters every run method by user_id, so a user can never see another user's runs.

from cli.menu import Menu

# Views all Past runs made by user
class PastRunsMenu(Menu):

    def __init__(self, context):
        super().__init__("PAST RUNS", context)
        self.add_option("View Latest", self.view_latest)
        self.add_option("Browse all", self.view_all)
        self.add_option("View by run ID", self.view_by_id)
        self.add_option("Back", self.stop)

    # Shows latest ai 5 reccomendation
    def view_latest(self):
        runs = self._data.list_runs(self._user_id)
        if not runs:
            self._display.message("You have no past runs yet.")
            return
        self._show_run(runs[0])

    # Shows all history of best recomendation
    def view_all(self):
        runs = self._data.list_runs(self._user_id)
        self._page_through(runs, self._display.run_summary)   

    def view_by_id(self):
        run_id = self._input.ask_int("Enter a run ID:", low=1)
        run = self._data.get_run(run_id, self._user_id)
        if run is None:
            self._display.message("No run found with that ID.")
            return
        self._show_run(run)
