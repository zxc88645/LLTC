import os
import sqlite3
from pathlib import Path


def get_database_path() -> Path:
    """Return the path to the SQLite database file."""
    db_dir = Path(os.environ.get("DATABASE_DIR", "data"))
    db_dir.mkdir(parents=True, exist_ok=True)
    return db_dir / "ssh_ai.db"


def init_database() -> None:
    """Initialise the database file and set secure permissions."""
    db_path = get_database_path()
    conn = sqlite3.connect(db_path)
    conn.close()
    os.chmod(db_path, 0o600)
