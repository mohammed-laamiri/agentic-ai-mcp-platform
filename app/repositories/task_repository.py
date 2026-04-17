# app/repositories/task_repository.py

from typing import Optional, List
from sqlmodel import Session
from app.models.task import Task


class TaskRepository:
    def __init__(self, session: Session):
        self.session = session

    def add(self, task: Task) -> Task:
        self.session.add(task)
        self.session.commit()
        self.session.refresh(task)
        return task

    def get(self, task_id: int) -> Optional[Task]:
        return self.session.get(Task, task_id)

    def list(self, skip: int = 0, limit: int = 100) -> List[Task]:
        return self.session.exec(Task.select().offset(skip).limit(limit)).all()

    def update(self, task: Task) -> Task:
        self.session.add(task)
        self.session.commit()
        self.session.refresh(task)
        return task
