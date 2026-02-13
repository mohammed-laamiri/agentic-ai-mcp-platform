# app/schemas/task.py

"""
Task Schemas for MCP Platform.

These schemas are used for API input/output and validation.

Responsibilities:
- Define input for task creation (`TaskCreate`)
- Define output for task reading (`TaskRead`)
- Use Pydantic v2 best practices (`model_validate` instead of deprecated `from_orm`)
- Include type hints and optional fields for API clients
"""

from enum import Enum
from typing import Optional, Dict, Union
from datetime import datetime

from pydantic import BaseModel, Field


# ==================================================
# Task Lifecycle Status
# ==================================================
class TaskStatus(str, Enum):
    """
    Enum for task lifecycle status.
    """
    pending = "pending"
    in_progress = "in_progress"
    completed = "completed"
    failed = "failed"


# ==================================================
# Task Creation Input Schema
# ==================================================
class TaskCreate(BaseModel):
    """
    Schema for creating a new task.

    Fields:
    - description: required human-readable task description
    - input: optional payload for execution
    """

    description: str = Field(..., description="Human-readable task description")
    input: Optional[Dict] = Field(
        default=None,
        description="Optional execution input payload",
    )

    model_config = {
        "from_attributes": True  # Required for SQLModel ORM compatibility in Pydantic v2
    }


# ==================================================
# Task Read / Output Schema
# ==================================================
class TaskRead(BaseModel):
    """
    Schema for reading a persisted task.

    Fields:
    - id: unique task identifier
    - description: task description
    - status: current task lifecycle status
    - result: output or error message
    - input: input payload
    - created_at: UTC timestamp of creation
    """

    id: str
    description: str
    status: TaskStatus
    result: Optional[Union[Dict, str]] = None
    input: Optional[Dict] = None
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None
    started_at: Optional[datetime] = None
    completed_at: Optional[datetime] = None
    project_id: Optional[str] = None
    priority: Optional[int] = None

    model_config = {
        "from_attributes": True  # Allows creating TaskRead from SQLModel ORM objects
    }
