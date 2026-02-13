"""
Task Repository.

Responsibilities:
- Encapsulates all CRUD operations on Task
- Provides clean interface for TaskService
"""

from typing import List, Optional
from sqlmodel import Session, select
from app.models.task import Task


class TaskRepository:
    """CRUD operations for Task."""

    def __init__(self, session: Session):
        self.session = session

    def create(self, task: Task) -> Task:
        self.session.add(task)
        self.session.commit()
        self.session.refresh(task)
        return task

    def get(self, task_id: str) -> Optional[Task]:
        statement = select(Task).where(Task.id == task_id)
        return self.session.exec(statement).first()

    def list(self, skip: int = 0, limit: int = 100) -> List[Task]:
        statement = select(Task).offset(skip).limit(limit)
        return self.session.exec(statement).all()

    def update(self, task: Task) -> Task:
        self.session.add(task)
        self.session.commit()
        self.session.refresh(task)
        return task
