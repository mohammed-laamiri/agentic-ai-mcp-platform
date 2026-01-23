from enum import Enum
from pydantic import BaseModel, Field


class TaskStatus(str, Enum):
    PENDING = "pending"
    RUNNING = "running"
    COMPLETED = "completed"
    FAILED = "failed"


class TaskBase(BaseModel):
    """
    Represents a unit of work executed by an agent.
    """

    input: str = Field(..., description="User or system input")
    status: TaskStatus = TaskStatus.PENDING


class TaskCreate(TaskBase):
    """
    Schema for task submission.
    """
    pass


class TaskRead(TaskBase):
    """
    Schema returned after execution.
    """

    id: str
    output: str | None = None
