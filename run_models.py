# run_models.py
# Classes for one saved run of the matching tool (the search history).
#
#   RunSnapshot        one run: when it ran, a copy of the resume at that moment,
#                      the top 5 results and the AI feedback
#   RunResult          one ranked job inside a run: rank, score and the Listing
#   RemovedInternship  stands in for an internship deleted after the run was saved,
#                      so display code can call the same getters without None checks

from Internship_Class import Internship
from listing_Class import Listing
from Student_Resume_Class import StudentResume


class RemovedInternship(Internship):
    """An Internship that no longer exists in the database. Only the job_id is known"""

    def __init__(self, job_id: int):
        super().__init__(
            job_id=job_id,
            company_name="",
            company_type="",
            industry="",
            job_title="Internship removed",
            relevant_course="",
            monthly_allowance=0,
            work_mode="",
            duration_months=0,
            required_skills="",
            location_district="",
            job_description="This internship was deleted after the run was saved.",
        )


class RunResult:
    """One ranked job in a run. rank 1 is the best match"""

    def __init__(self, rank: int, score: float, listing: Listing):
        self.__rank = rank
        self.__score = score
        self.__listing = listing

    def get_rank(self):
        return self.__rank

    def get_score(self):
        return self.__score

    def get_listing(self):
        return self.__listing

    def fetch_run_result_details(self):
        return {
            "rank": self.__rank,
            "score": self.__score,
            "listing": self.__listing.fetch_listing_details(),
        }


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
