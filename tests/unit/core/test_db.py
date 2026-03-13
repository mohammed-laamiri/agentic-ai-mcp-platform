"""
Unit tests for database module.

Tests database engine and session management.
"""

import pytest
from sqlmodel import create_engine, Session, SQLModel

from app.core.db import get_engine, get_session, init_db


@pytest.fixture
def test_engine():
    """Create an in-memory SQLite engine for testing."""
    engine = create_engine("sqlite:///:memory:", echo=False)
    SQLModel.metadata.create_all(engine)
    return engine


def test_get_engine_with_test_engine(test_engine):
    """get_engine should return test engine when provided."""
    result = get_engine(test_engine)
    assert result is test_engine


def test_get_session_with_test_engine(test_engine):
    """get_session should yield session using test engine."""
    session_gen = get_session(test_engine)
    session = next(session_gen)

    assert isinstance(session, Session)

    # Clean up
    try:
        next(session_gen)
    except StopIteration:
        pass


def test_init_db_with_test_engine(test_engine):
    """init_db should initialize schema with test engine."""
    # Should not raise
    init_db(test_engine)
