# database package: the SQLite connection and table definitions.
# The rest of the app only needs:  from database import Database

from .connection import Database

__all__ = ["Database"]
