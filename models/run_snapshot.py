# RunSnapshot: one saved run of the matching tool (the search history):
# when it ran, a copy of the resume at that moment, the top 5 results and the AI feedback.
# Each result is a RunResult (models/run_result.py); a job deleted after the run was saved
# comes back as RemovedInternship (models/removed_internship.py).
# DataManager.save_run / get_run / list_runs / delete_run read and write it.

from __future__ import annotations

from typing import TYPE_CHECKING

if TYPE_CHECKING:  # only needed for the type hints, so no import loop through student_resume
    from models.run_result import RunResult
    from models.student_resume import StudentResume

RESULTS_PER_RUN = 5


class RunSnapshot:
    """One saved run. The resume is a copy taken when the run happened,
    so later edits to the user's resume do not change it"""

    def __init__(
        self,
        run_id: int,
        user_id: int,
        created_at: str,
        resume: StudentResume,
        results: list[RunResult],
        feedback: list[str],
    ):
        self.__run_id = run_id
        self.__user_id = user_id
        self.__created_at = created_at
        self.__resume = resume
        self.__results = results
        self.__feedback = feedback

    def get_run_id(self):
        return self.__run_id

    def get_user_id(self):
        return self.__user_id

    def get_created_at(self):
        return self.__created_at

    def get_resume(self):
        return self.__resume

    def get_results(self):
        return self.__results

    def get_feedback(self):
        return self.__feedback

    def fetch_run_snapshot_details(self):
        return {
            "run_id": self.__run_id,
            "user_id": self.__user_id,
            "created_at": self.__created_at,
            "resume": self.__resume.fetch_Student_Resume_details(),
            "results": [result.fetch_run_result_details() for result in self.__results],
            "feedback": self.__feedback,
        }
