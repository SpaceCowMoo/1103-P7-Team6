# database package: everything that stores data in SQLite.
# The rest of the app only needs:  from database import DataManager

from .data_manager import DataManager

__all__ = ["DataManager"]
