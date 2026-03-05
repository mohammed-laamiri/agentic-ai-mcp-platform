# app/services/task_service.py
"""
Task Service

Handles task persistence and execution results.
Compatible with both string and dict ExecutionResults.
"""

from typing import Optional, Union, Dict
from uuid import uuid4
from datetime import datetime

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
            description=task_in.description,
            status=status,
            result=result_value,
            input=task_in.input,
            created_at=datetime.utcnow(),
        )

        # Store in internal dictionary
        self._tasks[task_id] = task
        return task

    def get(self, task_id: str) -> Optional[TaskRead]:
        """
        Retrieve a task by ID.
        """
        return self._tasks.get(task_id)