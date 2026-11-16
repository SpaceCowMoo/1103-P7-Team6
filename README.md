# 1103-P7-Team6

# INTERNLINK

## Installation

1. **Clone the repository:**

```bash
git clone https://github.com/SpaceCowMoo/1103-P7-Team6.git
cd 1103-P7-Team6
```

2. **Set up the Environment Variables:**

Windows (PowerShell):
```bash
Copy-Item .env.example .env
```

macOS / Linux / Git Bash:
```bash
cp .env.example .env
```

3. **Build the Docker image:**

```bash
docker build -t internlink .
```

4. **Run the Application:**

Windows (PowerShell):
```bash
docker run --rm -it -v "${PWD}/data:/app/internlink/data" internlink
```

macOS / Linux / Git Bash:
```bash
docker run --rm -it -v "$(pwd)/data:/app/internlink/data" internlink
```

## Running Tests

To run the test script, use the following Docker commands:

1. **Build the test image:**

```bash
docker build -t internlink-test .
```

2. **Run the test script:**

```bash
docker run --rm internlink-test python test_script.py
```

## Database

All stored data is read and written by the `DataManager` class in `data_manager.py`. The SQLite connection, table definitions and transactions are in `storage/database.py`. The data files live in `data/`: `internships.csv` and the SQLite file `internlink.db`.

Create or open the database and show the row count of every table (uses `INTERNSHIP_DB` and `INTERNSHIP_DATA` from `.env`, or pass the paths):

```bash
python data_manager.py data/internlink.db data/internships.csv
```

There are no migrations. If you change `SCHEMA_SQL` in `storage/database.py`, delete the `.db` file and run the command again. The tables are recreated and the internships are reloaded from the CSV. Users, resumes and runs are lost.

Run the database tests:

```bash
python -m unittest discover -s tests
```

See `database_example.py` for how to call every `DataManager` method. Running it creates a fresh `data/example.db`, uses every method once and prints OK or FAIL for each step. It never touches `data/internlink.db`:

```bash
python database_example.py
```
