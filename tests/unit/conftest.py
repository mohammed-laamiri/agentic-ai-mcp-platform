# tests/unit/conftest.py

"""
Pytest fixtures for the Task API

Provides an in-memory SQLite DB, session, and FastAPI test client
for integration tests.
"""

import pytest
from fastapi.testclient import TestClient
from sqlmodel import SQLModel, Session, create_engine
from sqlalchemy.orm import sessionmaker

from app.main import app
from app.core.db import get_session

# -----------------------------
# Test DB setup
# -----------------------------
TEST_SQLITE_URL = "sqlite:///:memory:"
engine = create_engine(TEST_SQLITE_URL, connect_args={"check_same_thread": False})
TestingSessionLocal = sessionmaker(bind=engine, expire_on_commit=False)

@pytest.fixture(scope="module")
def session():
    # Create tables
    SQLModel.metadata.create_all(engine)
    db = TestingSessionLocal()
    yield db
    db.close()
    SQLModel.metadata.drop_all(engine)

# -----------------------------
# Test client
# -----------------------------
@pytest.fixture(scope="module")
def client(session: Session):
    # Override get_session dependency
    def override_get_session():
        yield session

    app.dependency_overrides[get_session] = override_get_session
    yield TestClient(app)
    app.dependency_overrides.clear()
