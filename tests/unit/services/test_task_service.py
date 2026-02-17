"""
Unit tests for TaskService.

Uses an in-memory SQLite database to ensure isolation.

Tests:
- Task creation
- Task retrieval by ID
- Task listing
- Task completion
- Task failure
"""

import pytest
from sqlmodel import SQLModel, Session, create_engine

from app.models.task import Task
from app.services.task_service import TaskService
from app.schemas.task import TaskCreate, TaskStatus


# ==================================================
# Test database setup
# ==================================================
@pytest.fixture(name="session")
def session_fixture():
    """
    Provides a fresh SQLModel session for each test.
    Uses in-memory SQLite database.
    """
    engine = create_engine("sqlite:///:memory:", echo=False)
    SQLModel.metadata.create_all(engine)
    with Session(engine) as session:
        yield session


@pytest.fixture(name="task_service")
def task_service_fixture():
    """
    Provides a TaskService instance wired with test DB session.
    """
    return TaskService()


# ==================================================
# Tests
# ==================================================
def test_create_task(task_service: TaskService):
    # Include 'name' to satisfy TaskCreate schema
    task_in = TaskCreate(name="Test Task", description="Test Task", input={"foo": "bar"})
    task_read = task_service.create_task(task_in)

    assert task_read.id is not None
    assert task_read.name == "Test Task"
    assert task_read.description == "Test Task"
    assert task_read.status == TaskStatus.pending
    assert task_read.input == {"foo": "bar"}


def test_get_task(task_service: TaskService):
    task_in = TaskCreate(name="Retrieve Task", description="Retrieve Task")
    created_task = task_service.create_task(task_in)

    retrieved_task = task_service.get_task(created_task.id)
    assert retrieved_task is not None
    assert retrieved_task.id == created_task.id
    assert retrieved_task.name == "Retrieve Task"
    assert retrieved_task.description == "Retrieve Task"


def test_list_tasks(task_service: TaskService):
    for i in range(3):
        task_in = TaskCreate(name=f"Task {i}", description=f"Task {i}")
        task_service.create_task(task_in)

    tasks = task_service.list_tasks()
    assert len(tasks) == 3
    assert tasks[0].name == "Task 0"
    assert tasks[0].description == "Task 0"
    assert tasks[1].name == "Task 1"
    assert tasks[1].description == "Task 1"
    assert tasks[2].name == "Task 2"
    assert tasks[2].description == "Task 2"


def test_complete_task(task_service: TaskService):
    task_in = TaskCreate(name="Complete Me", description="Complete Me")
    created_task = task_service.create_task(task_in)

    completed_task = task_service.complete_task(created_task.id, result={"message": "Done successfully"})
    assert completed_task.status == TaskStatus.completed
    assert completed_task.result == {"message": "Done successfully"}


def test_fail_task(task_service: TaskService):
    task_in = TaskCreate(name="Fail Me", description="Fail Me")
    created_task = task_service.create_task(task_in)

    failed_task = task_service.fail_task(created_task.id, error="Something went wrong")
    assert failed_task.status == TaskStatus.failed
    assert failed_task.result == {"error": "Something went wrong"}
