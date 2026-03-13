# app/services/task_service.py
"""
Task Service

Handles task persistence and execution results.
Compatible with both string and dict ExecutionResults.
"""

from typing import Optional, Union, Dict, List
from uuid import uuid4
from datetime import datetime, timezone

from app.schemas.task import TaskCreate, TaskRead, TaskStatus


class TaskService:
    """
    Task persistence layer.

    Currently in-memory storage.
    Handles creation and retrieval of TaskRead objects.
    """

    def __init__(self) -> None:
        # Internal storage: task_id -> TaskRead
        self._tasks: Dict[str, TaskRead] = {}

    def create(
        self,
        task_in: TaskCreate,
        execution_result: Optional[Union[str, Dict]] = None,
    ) -> TaskRead:
        """
        Create a new task.

        Arguments:
        - task_in: TaskCreate object containing description and input.
        - execution_result: Optional output from execution (string or dict).

        Behavior:
        - If execution_result is dict: extract "output".
        - If execution_result is string: store as-is.
        - Determines task status based on presence of execution_result.
        """

        task_id = str(uuid4())  # Generate unique ID
        result_value: Optional[Union[str, Dict]] = None

        # Safe extraction of output
        if isinstance(execution_result, dict):
            result_value = execution_result.get("output")
        elif isinstance(execution_result, str):
            result_value = execution_result
        else:
            result_value = None

        # Determine task status
        status = TaskStatus.completed if execution_result else TaskStatus.pending

        # Build TaskRead object
        task = TaskRead(
            id=task_id,
            name=getattr(task_in, "name", None),
            description=task_in.description,
            status=status,
            result=result_value,
            input=task_in.input,
            created_at=datetime.now(timezone.utc),
        )

        # Store in internal dictionary
        self._tasks[task_id] = task
        return task

    def get(self, task_id: str) -> Optional[TaskRead]:
        """
        Retrieve a task by ID.
        """
        return self._tasks.get(task_id)

    # ==================================================
    # Aliases for backward compatibility
    # ==================================================

    def create_task(self, task_in: TaskCreate) -> TaskRead:
        """
        Create a new task (alias for create()).
        """
        return self.create(task_in)

    def get_task(self, task_id: str) -> Optional[TaskRead]:
        """
        Retrieve a task by ID (alias for get()).
        """
        return self.get(task_id)

    def list_tasks(self, skip: int = 0, limit: int = 100) -> List[TaskRead]:
        """
        List all tasks with optional pagination.
        """
        tasks = list(self._tasks.values())
        return tasks[skip:skip + limit]

    def complete_task(
        self,
        task_id: str,
        result: Optional[Union[str, Dict]] = None,
    ) -> Optional[TaskRead]:
        """
        Mark a task as completed with an optional result.
        """
        task = self._tasks.get(task_id)
        if task is None:
            return None

        # Create updated task with completed status
        updated_task = TaskRead(
            id=task.id,
            name=task.name,
            description=task.description,
            status=TaskStatus.completed,
            result=result,
            execution_result=task.execution_result,
            input=task.input,
            created_at=task.created_at,
            completed_at=datetime.now(timezone.utc),
        )
        self._tasks[task_id] = updated_task
        return updated_task

    def fail_task(
        self,
        task_id: str,
        error: str,
    ) -> Optional[TaskRead]:
        """
        Mark a task as failed with an error message.
        """
        task = self._tasks.get(task_id)
        if task is None:
            return None

        # Create updated task with failed status
        updated_task = TaskRead(
            id=task.id,
            name=task.name,
            description=task.description,
            status=TaskStatus.failed,
            result={"error": error},
            execution_result=task.execution_result,
            input=task.input,
            created_at=task.created_at,
            completed_at=datetime.now(timezone.utc),
        )
        self._tasks[task_id] = updated_task
        return updated_task
