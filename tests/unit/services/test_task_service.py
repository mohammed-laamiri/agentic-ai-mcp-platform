"""
Unit tests for TaskService.
"""

from app.services.task_service import TaskService
from app.schemas.task import TaskCreate, TaskStatus


def test_task_creation_from_execution_result():
    service = TaskService()

    task_in = TaskCreate(description="Test task")
    execution_result = {
        "output": "Test output",
    }

    task = service.create(task_in=task_in, execution_result=execution_result)

    assert task.description == "Test task"
    assert task.status == TaskStatus.completed
    assert task.result == "Test output"
