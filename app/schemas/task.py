from enum import Enum
from typing import Optional, Dict, Union
from datetime import datetime

from pydantic import BaseModel, Field


class TaskStatus(str, Enum):
    """
    Task lifecycle status.
    """
    pending = "pending"
    in_progress = "in_progress"
    completed = "completed"
    failed = "failed"


class TaskCreate(BaseModel):
    """
    Task creation input.
    """

    description: str
    input: Optional[Dict] = Field(
        default=None,
        description="Optional execution input payload",
    )


class TaskRead(BaseModel):
    """
    Task read model.
    """

    id: str
    description: str
    status: TaskStatus
    result: Optional[Union[Dict, str]] = None
    input: Optional[Dict] = None
    created_at: Optional[datetime] = None
