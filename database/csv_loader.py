# database/csv_loader.py
# InternshipCsvLoader: reads and checks internships.csv, then hands the rows to
# InternshipRepository to save. Reading/checking lives here, saving lives in the repository.

import csv
import os

from .repositories import INTERNSHIP_COLUMNS, INTERNSHIP_NUMBER_COLUMNS, InternshipRepository


class InternshipCsvLoader:
    def __init__(self, internships: InternshipRepository):
        self.__internships = internships

    def load(self, path: str) -> int:
        """Load every row of the CSV. Returns how many rows were loaded.
        Nothing is saved if any row is invalid"""
        if not os.path.exists(path):
            raise FileNotFoundError(f"CSV not found: {path}")
        with open(path, newline="", encoding="utf-8-sig") as file:
            rows = list(csv.DictReader(file))
        # Line 1 is the header, so the first data row is line 2
        validated = [self._validate_row(row, line) for line, row in enumerate(rows, start=2)]
        self.__internships.import_rows(validated)
        return len(validated)

    @staticmethod
    def _validate_row(row: dict, line_number: int) -> dict:
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
