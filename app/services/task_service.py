# app/services/task_service.py

"""
Task Service.

Manages task domain logic, including:
- Creating and persisting task records
- Handling task lifecycle transitions
- Returning fully-formed TaskRead objects

This service represents the *task domain*. It DOES NOT:
- Execute agents
- Perform orchestration
- Call external tools
"""

from datetime import datetime
from typing import List, Optional
from uuid import uuid4

from app.schemas.task import TaskCreate, TaskRead, TaskStatus


class TaskService:
    """
    Handles task domain operations.

    Responsibilities:
    - Own task state transitions
    - Return fully-formed TaskRead objects
    - Provide methods for listing, retrieving, creating, completing, or failing tasks

    Restrictions:
    - Should not execute agents or orchestrators
    - Should not handle tool executions
    """

    def __init__(self) -> None:
        # In-memory task store for now (future DB integration)
        self._tasks: List[TaskRead] = []

    # ==================================================
    # Core Task Operations
    # ==================================================
    def create(self, task_in: TaskCreate, execution_result: dict) -> TaskRead:
        """
        Create a task record from execution results.

        This represents the *first persistence step* of a task.
        Future enhancements may include:
        - Database persistence
        - Event emission
        - Audit/logging integration
        """
        task = TaskRead(
            id=str(uuid4()),
            description=task_in.description,
            status=TaskStatus.completed if execution_result.get("status") == "SUCCESS" else TaskStatus.failed,
            result=execution_result.get("output") or execution_result.get("errors"),
            input=task_in.input,
            created_at=datetime.utcnow(),
        )

        self._tasks.append(task)
        return task

    def complete_task(self, task: TaskRead, output: str) -> TaskRead:
        """
        Mark a task as completed.

        Use cases:
        - Post-completion hooks
        - External system updates
        """
        task.status = TaskStatus.completed
        task.result = output
        return task

    def fail_task(self, task: TaskRead, error: str) -> TaskRead:
        """
        Mark a task as failed.

        Use cases:
        - Agent or tool failures
        - Logging or notification triggers
        """
        task.status = TaskStatus.failed
        task.result = error
        return task

    # ==================================================
    # Retrieval Operations
    # ==================================================
    def get_task(self, task_id: str) -> Optional[TaskRead]:
        """
        Retrieve a task by its unique ID.

        Returns None if not found.
        """
        return next((t for t in self._tasks if t.id == task_id), None)

    def list_tasks(self) -> List[TaskRead]:
        """
        List all tasks currently persisted in memory.

        Future enhancements:
        - Database query with filtering, pagination, and sorting
        """
        return self._tasks.copy()
