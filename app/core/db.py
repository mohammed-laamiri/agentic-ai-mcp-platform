"""
Database Core Module.

This module is the *single source of truth* for database connectivity
inside the Agentic AI MCP Platform.

Responsibilities:
- Create the SQLModel / SQLAlchemy engine
- Manage DB sessions safely
- Provide FastAPI dependency injection
- Centralize future DB configuration (SQLite → Postgres, etc.)

This layer MUST NOT:
- Contain models
- Contain business logic
- Contain repositories
- Know anything about agents or orchestration

Think of this as the infrastructure foundation for persistence.
"""

from typing import Generator

from sqlmodel import SQLModel, Session, create_engine

from app.core.config import Settings


# ============================================================
# Database URL Resolution
# ============================================================
"""
We resolve the database URL from settings.

Today:
- Default: SQLite (local dev)

Tomorrow:
- Postgres (RDS, Aurora, etc.)
- MySQL
- Any SQLAlchemy compatible backend

This keeps the platform environment-agnostic.
"""

DATABASE_URL = Settings.DATABASE_URL


# ============================================================
# Engine Creation
# ============================================================
"""
The engine manages the connection pool and communication
between Python and the database.

echo=True:
- Logs SQL queries (great for development/debugging)
- Should be False in production.
"""

engine = create_engine(
    DATABASE_URL,
    echo=True,
    connect_args={"check_same_thread": False} if DATABASE_URL.startswith("sqlite") else {},
)


# ============================================================
# Session Factory
# ============================================================
"""
Session is the unit-of-work pattern.

Each request:
- Opens a session
- Uses it
- Commits / rolls back
- Closes safely

We never share sessions across requests.
"""


def get_session() -> Generator[Session, None, None]:
    """
    FastAPI dependency that provides a DB session.

    Usage:
        def endpoint(session: Session = Depends(get_session))

    Lifecycle:
        - Open session
        - Yield to caller
        - Always close after request
    """
    with Session(engine) as session:
        yield session


# ============================================================
# Database Initialization
# ============================================================
"""
Called once on application startup.

It creates tables based on SQLModel metadata.

Later improvements may include:
- Alembic migrations
- Versioning
- Seeding
"""


def init_db() -> None:
    """
    Initialize database schema.

    This scans all SQLModel models and creates tables.

    IMPORTANT:
    - Should be called on app startup
    - Safe to call multiple times
    """
    SQLModel.metadata.create_all(engine)
