"""
Task service.

Responsible for:
- Creating task records
- Managing task lifecycle
- Returning domain-level task responses
"""

from datetime import datetime
from uuid import uuid4

from app.schemas.task import TaskCreate, TaskRead, TaskStatus


class TaskService:
    """
    Handles task domain logic.
    """

    def create(self, task_in: TaskCreate, execution_result: dict) -> TaskRead:
        """
        Create a task record from execution results.
        """
        return TaskRead(
            id=str(uuid4()),
            description=task_in.description,
            status=TaskStatus.completed,
            result=execution_result["output"],
            created_at=datetime.utcnow(),
        )


    def complete_task(self, task: TaskRead, output: str) -> TaskRead:
        """
        Mark a task as completed.
        """
        task.status = TaskStatus.COMPLETED
        task.output = output
        return task

    def fail_task(self, task: TaskRead, error: str) -> TaskRead:
        """
        Mark a task as failed.
        """
        task.status = TaskStatus.FAILED
        task.output = error
        return task
