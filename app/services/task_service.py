from typing import Optional, Dict, List, Any
from uuid import uuid4
from datetime import datetime

from app.schemas.task import TaskCreate, TaskRead
from app.models.task import Task  # simple class or ORM


class TaskService:
    """
    Service layer for task management.
    Handles in-memory storage, creation, updates, and task status changes.
    """

    def __init__(self):
        self._tasks: Dict[str, Task] = {}

    def create_task(self, task_create: TaskCreate) -> TaskRead:
        task_id = str(uuid4())
        now = datetime.utcnow()
        task = Task(
            id=task_id,
            name=task_create.name,
            description=task_create.description,
            status=task_create.status,
            priority=task_create.priority,
            input=task_create.input or {},
            result={},
            created_at=now,
            updated_at=now,
            started_at=None,
            completed_at=None,
            project_id=None,
        )
        self._tasks[task_id] = task
        return TaskRead(**vars(task))

    def get_task(self, task_id: str) -> Optional[TaskRead]:
        task = self._tasks.get(task_id)
        return TaskRead(**vars(task)) if task else None

    def list_tasks(self, skip: int = 0, limit: int = 100) -> List[TaskRead]:
        tasks = list(self._tasks.values())[skip : skip + limit]
        return [TaskRead(**vars(t)) for t in tasks]

    def complete_task(self, task_id: str, result: Optional[Dict[str, Any]] = None) -> Optional[TaskRead]:
        task = self._tasks.get(task_id)
        if not task:
            return None
        task.status = "completed"
        task.result = result or {}
        task.completed_at = datetime.utcnow()
        task.updated_at = datetime.utcnow()
        return TaskRead(**vars(task))

    def fail_task(self, task_id: str, error: str) -> Optional[TaskRead]:
        task = self._tasks.get(task_id)
        if not task:
            return None
        task.status = "failed"
        task.result = {"error": error}
        task.completed_at = datetime.utcnow()
        task.updated_at = datetime.utcnow()
        return TaskRead(**vars(task))
