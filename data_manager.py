import csv
import os

INTERNSHIP_DATA = "/app/OpportunityFit/data"

def get_file_path(filename):
    """Ensure file exists and return file path"""
    try:
        os.makedirs(INTERNSHIP_DATA, exist_ok=True)
        return os.path.join(INTERNSHIP_DATA, filename)
    except Exception as e:
        print(f"[Error] Failed to access directory {INTERNSHIP_DATA}: {e}")
        return None

def load_csv(filename):
    """Read CSV file"""
    path = get_file_path(filename)
    if not path or not os.path.exists(path):
        print(f"[Info] File '{filename}' does not exist yet.")
        return []

    try:
        with open(path, mode="r", encoding="utf-8") as file:
            reader = csv.DictReader(file)
            return list(reader)
    except FileNotFoundError:
        print(f"[Error] File '{filename}' not found.")
        return []
    except Exception as e:
        print(f"[Error] Failed to read '{filename}': {e}")
        return []

def save_csv(filename, data, fieldnames):
    """Save a list of dictionaries to a CSV file"""
    path = get_file_path(filename)
    if not path:
        return False

    try:
        with open(path, mode="w", newline="", encoding="utf-8") as file:
            writer = csv.DictWriter(file, fieldnames=fieldnames)
            writer.writeheader()
            writer.writerows(data)
        print(f"[Success] Saved data to '{filename}'.")
        return True
    except PermissionError:
        print(f"[Error] Permission denied writing to '{filename}'.")
        return False
    except Exception as e:
        print(f"[Error] Failed to save '{filename}': {e}")
        return False