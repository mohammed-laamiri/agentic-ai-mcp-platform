"""
Task service.

Responsible for:
- Creating task records
- Managing task lifecycle
- Returning domain-level task responses

This service represents the *task domain*.
It does NOT know:
- How agents work
- How orchestration is done
"""

from datetime import datetime
from uuid import uuid4

from app.schemas.task import TaskCreate, TaskRead, TaskStatus


class TaskService:
    """
    Handles task domain logic.

    This service SHOULD:
    - Own task state transitions
    - Return fully-formed TaskRead objects

    This service SHOULD NOT:
    - Execute agents
    - Contain orchestration logic
    """

    def create(self, task_in: TaskCreate, execution_result: dict) -> TaskRead:
        """
        Create a task record from execution results.

        This method represents the *first persistence step* of a task.
        In future iterations, this may:
        - Write to a database
        - Emit events
        - Trigger audit logs
        """

        return TaskRead(
            id=str(uuid4()),
            description=task_in.description,
            status=TaskStatus.completed,
            result=execution_result.get("output"),
            input=task_in.input,
            created_at=datetime.utcnow(),
        )

    def complete_task(self, task: TaskRead, output: str) -> TaskRead:
        """
        Mark a task as completed.

        This method exists for future state transitions
        when tasks live longer than a single request.
        """
        task.status = TaskStatus.completed
        task.result = output
        return task

    def fail_task(self, task: TaskRead, error: str) -> TaskRead:
        """
        Mark a task as failed.

        Future use cases:
        - Agent crashes
        - Tool failures
        - Validation errors
        """
        task.status = TaskStatus.failed
        task.result = error
        return task
