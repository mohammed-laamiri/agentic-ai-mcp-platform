"""
Task Service.

Responsibilities:
- Handle task domain logic
- Persist tasks using TaskRepository
- Manage task lifecycle transitions: pending → completed/failed
- Return TaskRead objects
"""

from typing import List, Optional
from datetime import datetime
from uuid import uuid4

from sqlmodel import Session
from app.models.task import Task
from app.schemas.task import TaskCreate, TaskRead, TaskStatus


class TaskService:
    """Service for Task operations."""

    def __init__(self, session: Session):
        # Local import to break circular dependency
        from app.repositories.task_repository import TaskRepository
        self.repo = TaskRepository(session)

    # -------------------------
    # Create Task
    # -------------------------
    def create_task(self, task_in: TaskCreate, project_id: Optional[str] = None) -> TaskRead:
        task = Task(
            id=str(uuid4()),
            name=(task_in.description or "Unnamed Task")[:50],
            description=task_in.description,
            input=task_in.input,
            status=TaskStatus.pending,
            project_id=project_id,
            created_at=datetime.utcnow(),
            updated_at=datetime.utcnow(),
        )
        persisted_task = self.repo.create(task)
        return TaskRead.model_validate(persisted_task)

    # -------------------------
    # Retrieval
    # -------------------------
    def get_task(self, task_id: str) -> Optional[TaskRead]:
        task = self.repo.get(task_id)
        return TaskRead.model_validate(task) if task else None

    def list_tasks(self, skip: int = 0, limit: int = 100) -> List[TaskRead]:
        tasks = self.repo.list(skip=skip, limit=limit)
        return [TaskRead.model_validate(t) for t in tasks]

    # -------------------------
    # Lifecycle
    # -------------------------
    def complete_task(self, task_id: str, result: str) -> Optional[TaskRead]:
        task = self.repo.get(task_id)
        if not task:
            return None
        task.mark_completed(result)
        updated_task = self.repo.update(task)
        return TaskRead.model_validate(updated_task)

    def fail_task(self, task_id: str, error: str) -> Optional[TaskRead]:
        task = self.repo.get(task_id)
        if not task:
            return None
        task.mark_failed(error)
        updated_task = self.repo.update(task)
        return TaskRead.model_validate(updated_task)
