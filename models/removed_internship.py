from models.internship import Internship


class RemovedInternship(Internship):
    """An Internship that no longer exists in the database. Only the job_id is known.
    Stands in for a job deleted after a run was saved, so display code can call
    the same getters without None checks"""

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
