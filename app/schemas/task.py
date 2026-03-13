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
    name: str = Field(..., description="Task name")
    description: Optional[str] = Field(default=None, description="Task description")
    priority: int = Field(default=1, description="Task priority (1-5)")
    input: Optional[Dict] = Field(
        default=None,
        description="Optional execution input payload",
    )


class TaskRead(BaseModel):
    """
    Task read model.

    - Includes `result` for backward compatibility
    - Adds `execution_result` for orchestrator integration
    """
    id: str
    name: Optional[str] = None
    description: Optional[str] = None
    status: TaskStatus
    priority: int = 1
    result: Optional[Union[Dict, str]] = None
    execution_result: Optional[Dict] = None  # Added for orchestrator & execution service
    input: Optional[Dict] = None
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None
    completed_at: Optional[datetime] = None