"""Database configuration and setup for SQLite."""

import os
from pathlib import Path
from sqlalchemy import create_engine, event
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from sqlalchemy.engine import Engine
import sqlite3


def _get_database_dir() -> Path:
    """Get the directory where the database file is stored."""
    return Path(os.environ.get("DATABASE_DIR", "data"))


def _get_database_url() -> str:
    """Build the database URL from environment variables."""
    db_dir = _get_database_dir()
    db_dir.mkdir(exist_ok=True)
    if "DATABASE_DIR" in os.environ:
        return f"sqlite:///{db_dir}/ssh_ai.db"
    return os.environ.get("DATABASE_URL", f"sqlite:///{db_dir}/ssh_ai.db")


def _create_engine():
    """Create a new SQLAlchemy engine based on current settings."""
    return create_engine(
        _get_database_url(),
        connect_args={"check_same_thread": False},
        echo=False,  # Set to True for SQL debugging
    )


# Create initial engine and session factory
engine = _create_engine()
# Enable foreign key constraints for SQLite
@event.listens_for(Engine, "connect")
def set_sqlite_pragma(dbapi_connection, connection_record):
    if isinstance(dbapi_connection, sqlite3.Connection):
        cursor = dbapi_connection.cursor()
        cursor.execute("PRAGMA foreign_keys=ON")
        cursor.close()

# Create session factory
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# Base class for all database models
Base = declarative_base()


def get_db():
    """Get database session."""
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


def init_database():
    """Initialize database tables using current environment settings."""
    global engine
    # Recreate engine in case environment changed
    engine.dispose()
    engine = _create_engine()
    SessionLocal.configure(bind=engine)

    Base.metadata.create_all(bind=engine)

    # Set proper permissions on database file
    db_file = _get_database_dir() / "ssh_ai.db"
    if db_file.exists():
        os.chmod(db_file, 0o600)


def get_database_path():
    """Get the path to the database file."""
    return _get_database_dir() / "ssh_ai.db"