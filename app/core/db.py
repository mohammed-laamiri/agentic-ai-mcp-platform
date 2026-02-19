"""
app/core/db.py

Database Core Module.

Single source of truth for database connectivity.
Supports both production and in-memory test databases.
"""

from typing import Generator, Optional

from sqlmodel import SQLModel, Session, create_engine

from app.core.config import get_settings

# ============================================================
# Global engine placeholder (lazy init)
# ============================================================
_engine: Optional[any] = None

# ============================================================
# Engine Factory
# ============================================================
def get_engine(test_engine: Optional[any] = None):
    """
    Lazily create and return the SQLAlchemy engine.

    If `test_engine` is provided, returns it (for testing with in-memory DB).
    Otherwise, creates engine from settings.
    """
    global _engine

    if test_engine is not None:
        _engine = test_engine
        return _engine

    if _engine is None:
        settings = get_settings()
        database_url = settings.DATABASE_URL
        _engine = create_engine(
            database_url,
            echo=True,
            connect_args={"check_same_thread": False}
            if database_url.startswith("sqlite")
            else {},
        )
    return _engine


# ============================================================
# Session Dependency
# ============================================================
def get_session(test_engine: Optional[any] = None) -> Generator[Session, None, None]:
    """
    FastAPI dependency that provides a DB session.
    Can accept a test_engine for testing purposes.
    """
    engine = get_engine(test_engine)
    with Session(engine) as session:
        yield session


# ============================================================
# Database Initialization
# ============================================================
def init_db(test_engine: Optional[any] = None) -> None:
    """
    Initialize database schema.
    Safe to call multiple times.
    Supports test_engine for in-memory DB.
    """
    engine = get_engine(test_engine)
    SQLModel.metadata.create_all(engine)
