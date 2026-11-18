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

The tests run inside the same `internlink` image built in the Installation section. If you haven't built it yet:

```bash
docker build -t internlink .
```

1. **Run the logic test script:**

```bash
docker run --rm internlink python test_script.py
```

2. **Run the AI manager tests** (uses a mock AI client, so no Gemini API calls are made):

```bash
docker run --rm internlink python -m unittest test_ai_manager_oop -v
```

3. **Run the database and IO manager tests** (everything in `tests/`):

```bash
docker run --rm internlink python -m unittest discover -s tests -v
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

## Note on `.env`

The project has no `.dockerignore` yet, so `COPY . .` in the `Dockerfile` copies your local `.env` (including `GEMINI_API_KEY`) into the Docker image. `.env` is listed in `.gitignore`, so it is not committed to the repository, but anyone with the built image can read the key. Do not push or share the image until this is fixed.

**TODO:** Add a `.dockerignore` file that excludes `.env`, and pass the variables at runtime instead:

```bash
docker run --rm -it --env-file .env -v "${PWD}/data:/app/internlink/data" internlink
```
