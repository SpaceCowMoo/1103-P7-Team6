# Create (or open) the database and show how many rows each table has.
#
#   python -m database                         uses INTERNSHIP_DB / INTERNSHIP_DATA from .env
#   python -m database data/test.db data/internships.csv
#
# Changed SCHEMA_SQL? Delete the .db file and run this again.

import os
import sys

from dotenv import load_dotenv

from .connection import Database


def main():
    load_dotenv()
    db_path = sys.argv[1] if len(sys.argv) > 1 else os.getenv("INTERNSHIP_DB", "data/internlink.db")
    csv_path = sys.argv[2] if len(sys.argv) > 2 else os.getenv("INTERNSHIP_DATA", "data/internships.csv")

    print(f"Database: {db_path}")
    print(f"CSV:      {csv_path}")
    db = Database.open(db_path, csv_path)
    try:
        for table, count in db.table_counts().items():
            print(f"  {table:<12} {count} rows")
    finally:
        db.close()


if __name__ == "__main__":
    main()
