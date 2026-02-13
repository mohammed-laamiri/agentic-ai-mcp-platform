# app/models/task.py

from typing import Optional, Union
from datetime import datetime
from sqlmodel import SQLModel, Field, Column
from sqlalchemy import JSON
from enum import Enum


class TaskStatus(str, Enum):
    pending = "pending"
    in_progress = "in_progress"
    completed = "completed"
    failed = "failed"


class Task(SQLModel, table=True):
    """
    Task ORM model.

    Fields:
    - id: unique task ID
    - name: short name
    - description: longer description
    - input: JSON dict of inputs
    - result: JSON dict or string of output/result
    - status: lifecycle status
    - timestamps: created, updated, started, completed
    - project_id: optional project association
    - priority: int priority
    """

    id: str = Field(primary_key=True)
    name: str
    description: str
    input: dict = Field(default_factory=dict, sa_column=Column(JSON))
    result: Optional[Union[str, dict]] = Field(default=None, sa_column=Column(JSON))
    status: TaskStatus = Field(default=TaskStatus.pending)

    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)
    started_at: Optional[datetime] = None
    completed_at: Optional[datetime] = None

    project_id: Optional[str] = None
    priority: int = 1  # default priority

    # ==================================================
    # Lifecycle methods
    # ==================================================
    def mark_started(self):
        self.status = TaskStatus.in_progress
        self.started_at = datetime.utcnow()
        self.updated_at = datetime.utcnow()

    def mark_completed(self, result: Union[str, dict]):
        self.status = TaskStatus.completed
        self.result = result
        self.completed_at = datetime.utcnow()
        self.updated_at = datetime.utcnow()

    def mark_failed(self, error: str):
        self.status = TaskStatus.failed
        self.result = error
        self.completed_at = datetime.utcnow()
        self.updated_at = datetime.utcnow()
