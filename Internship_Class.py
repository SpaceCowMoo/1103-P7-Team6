import csv
import os

# Columns of the internships table (and internships.csv), in order
INTERNSHIP_COLUMNS = [
    "job_id", "company_name", "company_type", "industry", "job_title", "relevant_course",
    "monthly_allowance", "work_mode", "duration_months", "required_skills",
    "location_district", "job_description",
]
INTERNSHIP_NUMBER_COLUMNS = {"job_id", "monthly_allowance", "duration_months"}


class Internship:
    def __init__(self, job_id, company_name, company_type, industry, job_title, relevant_course, monthly_allowance, work_mode, duration_months, required_skills, location_district, job_description):
        self.__job_id = job_id
        self.__company_name = company_name
        self.__company_type = company_type
        self.__industry = industry
        self.__job_title = job_title
        self.__relevant_course = relevant_course
        self.__monthly_allowance = monthly_allowance
        self.__work_mode = work_mode
        self.__duration_months = duration_months
        self.__required_skills = required_skills
        self.__location_district = location_district
        self.__job_description = job_description

    def get_job_id(self):
        return self.__job_id

    def get_company_name(self):
        return self.__company_name

    def get_company_type(self):
        return self.__company_type

    def get_industry(self):
        return self.__industry

    def get_job_title(self):
        return self.__job_title

    def get_relevant_course(self):
        return self.__relevant_course

    def get_monthly_allowance(self):
        return self.__monthly_allowance

    def get_work_mode(self):
        return self.__work_mode

    def get_duration_months(self):
        return self.__duration_months

    def get_required_skills(self):
        return self.__required_skills

    def get_location_district(self):
        return self.__location_district

    def get_job_description(self):
        return self.__job_description

    def fetch_internship_details(self):
        return {
            "job_id": self.__job_id,
            "company_name": self.__company_name,
            "company_type": self.__company_type,
            "industry": self.__industry,
            "job_title": self.__job_title,
            "relevant_course": self.__relevant_course,
            "monthly_allowance": self.__monthly_allowance,
            "work_mode": self.__work_mode,
            "duration_months": self.__duration_months,
            "required_skills": self.__required_skills,
            "location_district": self.__location_district,
            "job_description": self.__job_description,
        }

    # ---------- database: read and write the internships table ----------
    # db is the Database object from Database.open()

    @classmethod
    def get(cls, db, job_id):
        """One internship, or None if the job_id doesn't exist"""
        row = db.fetch_one("SELECT * FROM internships WHERE job_id = ?", (job_id,))
        return cls(**dict(row)) if row else None

    @classmethod
    def list_all(cls, db, limit=50, partial=False, **filters):
        """Internships matching the filters, by job_id. limit=-1 means no limit.
        partial=True matches text columns by substring, ignoring case
        e.g. Internship.list_all(db, limit=-1, work_mode="Hybrid")"""
        query = "SELECT * FROM internships WHERE 1=1"
        values = []
        for column, value in filters.items():
            if value is None:
                continue
            if column not in INTERNSHIP_COLUMNS:
                raise ValueError(f"Unknown column: {column}")
            if partial and column not in INTERNSHIP_NUMBER_COLUMNS:
                query += f" AND {column} LIKE ? COLLATE NOCASE"
                values.append(f"%{value}%")
            else:
                query += f" AND {column} = ?"
                values.append(value)
        query += " ORDER BY job_id ASC LIMIT ?"
        values.append(limit)
        return [cls(**dict(row)) for row in db.fetch_all(query, values)]

    @classmethod
    def create(cls, db, fields):
        """Save a new internship (job_id is made by SQLite). Returns the new Internship"""
        with db.transaction():
            job_id = db.insert("internships", _editable_fields(fields))
        return cls.get(db, job_id)

    def update(self, db, changes):
        """Save changes to this internship, e.g. {"monthly_allowance": 1200}.
        Returns True if it was updated; this object then has the new values"""
        changes = _editable_fields(changes)
        if not changes:
            return False
        set_clause = ", ".join(f"{column} = ?" for column in changes)
        with db.transaction():
            cursor = db.execute(f"UPDATE internships SET {set_clause} WHERE job_id = ?",
                                [*changes.values(), self.__job_id])
        if cursor.rowcount == 0:
            return False
        row = db.fetch_one("SELECT * FROM internships WHERE job_id = ?", (self.__job_id,))
        Internship.__init__(self, **dict(row))  # reload this object's fields from the saved row
        return True

    def delete(self, db):
        """Delete this internship. Returns True if it existed"""
        with db.transaction():
            cursor = db.execute("DELETE FROM internships WHERE job_id = ?", (self.__job_id,))
        return cursor.rowcount > 0

    @classmethod
    def load_csv(cls, db, path):
        """Load every row of internships.csv. Returns how many rows were loaded.
        Nothing is saved if any row is invalid"""
        if not os.path.exists(path):
            raise FileNotFoundError(f"CSV not found: {path}")
        with open(path, newline="", encoding="utf-8-sig") as file:
            rows = list(csv.DictReader(file))
        # Line 1 is the header, so the first data row is line 2
        validated = [cls._validate_csv_row(row, line) for line, row in enumerate(rows, start=2)]
        with db.transaction():
            for row in validated:
                db.insert("internships", row, replace=True)
        return len(validated)

    @staticmethod
    def _validate_csv_row(row, line_number):
        """Check one CSV row. Returns only the internship columns, with numbers as int"""
        if None in row:  # more values than header columns
            raise ValueError(f"Line {line_number}: too many fields")
        missing = [column for column in INTERNSHIP_COLUMNS if row.get(column) is None]
        if missing:
            raise ValueError(f"Line {line_number}: missing fields: {', '.join(missing)}")

        for field in set(INTERNSHIP_COLUMNS) - INTERNSHIP_NUMBER_COLUMNS:
            if not row[field].strip():
                raise ValueError(f"Line {line_number}: {field} is blank")
        try:
            numbers = {column: int(row[column]) for column in INTERNSHIP_NUMBER_COLUMNS}
        except ValueError as error:
            raise ValueError(f"Line {line_number}: invalid numeric value") from error
        if numbers["job_id"] <= 0 or numbers["monthly_allowance"] < 0 or numbers["duration_months"] <= 0:
            raise ValueError(f"Line {line_number}: numeric value is out of range")

        cleaned = {column: row[column] for column in INTERNSHIP_COLUMNS}
        cleaned.update(numbers)
        return cleaned


def _editable_fields(data):
    """Keep only internship columns the user may set (job_id is made by SQLite)"""
    return {k: v for k, v in data.items() if k in INTERNSHIP_COLUMNS and k != "job_id"}


internship = Internship
