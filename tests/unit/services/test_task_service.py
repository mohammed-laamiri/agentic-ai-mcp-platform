# tests/unit/services/test_task_service.py

"""
Unit tests for TaskService.

TaskService uses in-memory storage (Dict), not database.
Tests:
- Task creation
- Task retrieval by ID
- Task listing
- Task completion
- Task failure
"""

import pytest

from app.services.task_service import TaskService
from app.schemas.task import TaskCreate, TaskStatus


@pytest.fixture(name="task_service")
def task_service_fixture():
    """
    Provides a fresh TaskService instance for each test.
    TaskService uses in-memory storage, so each instance is isolated.
    """
    return TaskService()


# ==================================================
# Tests
# ==================================================
def test_create_task(task_service: TaskService):
    task_in = TaskCreate(name="Test Task", description="Test Description", input={"foo": "bar"})
    task_read = task_service.create_task(task_in)

    assert task_read.id is not None
    assert task_read.name == "Test Task"
    assert task_read.description == "Test Description"
    assert task_read.status == TaskStatus.pending
    assert task_read.input == {"foo": "bar"}


def test_get_task(task_service: TaskService):
    task_in = TaskCreate(name="Retrieve Task", description="To be retrieved")
    created_task = task_service.create_task(task_in)

    retrieved_task = task_service.get_task(created_task.id)
    assert retrieved_task is not None
    assert retrieved_task.id == created_task.id
    assert retrieved_task.name == "Retrieve Task"


def test_list_tasks(task_service: TaskService):
    for i in range(3):
        task_in = TaskCreate(name=f"Task {i}", description=f"Description {i}")
        task_service.create_task(task_in)

    tasks = task_service.list_tasks()
    assert len(tasks) == 3
    assert tasks[0].name == "Task 0"
    assert tasks[1].name == "Task 1"
    assert tasks[2].name == "Task 2"


def test_complete_task(task_service: TaskService):
    task_in = TaskCreate(name="Complete Me", description="To be completed")
    created_task = task_service.create_task(task_in)

    completed_task = task_service.complete_task(created_task.id, result={"output": "Done"})
    assert completed_task.status == TaskStatus.completed
    assert completed_task.result == {"output": "Done"}
    assert completed_task.completed_at is not None


def test_fail_task(task_service: TaskService):
    task_in = TaskCreate(name="Fail Me", description="To be failed")
    created_task = task_service.create_task(task_in)

    failed_task = task_service.fail_task(created_task.id, error="Something went wrong")
    assert failed_task.status == TaskStatus.failed
    assert failed_task.result == {"error": "Something went wrong"}
    assert failed_task.completed_at is not None
