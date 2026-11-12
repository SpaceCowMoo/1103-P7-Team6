# database/serializers.py
# ResumeSerializer: StudentResume object <-> JSON text for the resume_json columns.
# This is the only place that knows how a resume is stored. If the team changes
# StudentResume, or we stop using JSON, only this class needs to change.

import json

from Past_internship_done_class import PastInternship
from Student_Resume_Class import StudentResume


class ResumeSerializer:
    @staticmethod
    def to_json(resume: StudentResume) -> str:
        return json.dumps(resume.fetch_Student_Resume_details())

    @staticmethod
    def from_json(text: str) -> StudentResume:
        data = json.loads(text)
        past_internships = [PastInternship(**item) for item in data.pop("Past_internships", [])]
        return StudentResume(**data, Past_internships=past_internships)
