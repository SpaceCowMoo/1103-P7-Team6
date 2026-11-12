# database/data_manager.py
# DataManager: the one object the rest of the app uses for storage.
# It opens the database and builds one repository per table.
#
#   dm = DataManager.open(DB_PATH, INTERNSHIP_DATA)
#   dm.internships   InternshipRepository  -> Internship objects
#   dm.users         UserRepository        -> StudentProfile objects
#   dm.resumes       ResumeRepository      -> StudentResume objects
#   dm.runs          RunRepository         -> RunSnapshot objects
#   dm.close()
#
# See database_example.py for how to use each one.

from .connection import TABLES, Database
from .csv_loader import InternshipCsvLoader
from .repositories import InternshipRepository, ResumeRepository, RunRepository, UserRepository


class DataManager:
    def __init__(self, db: Database):
        self.__db = db
        self.__internships = InternshipRepository(db)
        self.__users = UserRepository(db)
        self.__resumes = ResumeRepository(db)
        self.__runs = RunRepository(db, self.__internships)

    @classmethod
    def open(cls, db_path: str, csv_path: str | None = None) -> "DataManager":
        """Open the database, create missing tables, and load the CSV if internships is empty.
        db_path=":memory:" gives a throwaway database (good for tests)"""
        db = Database(db_path)
        try:
            db.create_schema()
            manager = cls(db)
            if csv_path is not None:
                manager.load_internships_if_empty(csv_path)
        except Exception:
            db.close()
            raise
        return manager

    def load_internships_if_empty(self, csv_path: str) -> int:
        """Load the CSV only the first time, so CRUD changes are kept.
        Returns how many rows were loaded (0 if internships already had rows)"""
        if not self.__db.is_empty("internships"):
            return 0
        return InternshipCsvLoader(self.__internships).load(csv_path)

    def table_counts(self) -> dict[str, int]:
        """Row count of every table, e.g. {"internships": 654, "users": 2, ...}"""
        return {table: self.__db.count(table) for table in TABLES}

    @property
    def internships(self) -> InternshipRepository:
        return self.__internships

    @property
    def users(self) -> UserRepository:
        return self.__users

    @property
    def resumes(self) -> ResumeRepository:
        return self.__resumes

    @property
    def runs(self) -> RunRepository:
        return self.__runs

    def close(self):
        self.__db.close()
