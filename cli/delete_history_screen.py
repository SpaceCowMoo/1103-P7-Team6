# Delete some or all of the logged-in user's past AI runs.
# Asks for one run ID (or -1 / -2 / -3), not a numbered option.
# DataManager.delete_run also checks the user_id, so a user can never delete another user's run.
from cli.screen import Screen


class DeleteHistoryScreen(Screen):
    DELETE_LATEST = -1
    DELETE_ALL = -2
    CANCEL = -3

    def run(self):
        runs = self._data.list_runs(self._user_id)      # newest first
        if not runs:
            self._display.message("You have no past runs to delete.")
            return

        self._display.heading("DELETE HISTORY")
        self._page_through(runs, self._display.run_summary)   # let them see what's there first

        to_delete = self.__pick_runs(runs)
        if not to_delete:
            return                                          # cancelled

        if not self._input.ask_yes_no(f"Delete {len(to_delete)} run(s)? This cannot be undone (Y/N):"):
            self._display.message("Nothing was deleted.")
            return

        deleted = 0
        for run_id in to_delete:
            if self._data.delete_run(run_id, self._user_id):   # True only if it existed and is theirs
                deleted += 1
        self._display.message(f"Deleted {deleted} run(s).")

    # ---- helpers ----
    def __pick_runs(self, runs):
        """Ask which runs to delete. Returns a list of run IDs, or an empty list if cancelled."""
        choice = self._input.ask_int(
            "Run ID to delete (-1 latest, -2 all, -3 cancel):", low=self.CANCEL)

        if choice == self.CANCEL:
            return []
        if choice == self.DELETE_LATEST:
            return [runs[0].get_run_id()]
        if choice == self.DELETE_ALL:
            return [run.get_run_id() for run in runs]
        return [choice]                                     # one specific run ID
