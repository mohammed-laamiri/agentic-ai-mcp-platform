from typing import Optional, Any, Dict, Union, List
from pydantic import BaseModel, Field, Json
from enum import Enum
from datetime import datetime

# ----------------------------
# Task Status Enum
# ----------------------------
class TaskStatus(str, Enum):
    pending = "pending"
    in_progress = "in_progress"
    completed = "completed"
    failed = "failed"

# ----------------------------
# Base Task Schema
# ----------------------------
class TaskBase(BaseModel):
    name: str = Field(..., description="Name of the task")
    description: Optional[str] = Field(None, description="Task details")
    status: TaskStatus = Field(TaskStatus.pending, description="Current status of the task")
    priority: int = Field(1, description="Priority of the task")

# ----------------------------
# Task Creation Schema
# ----------------------------
class TaskCreate(TaskBase):
    input: Optional[Dict[str, Any]] = Field(default_factory=dict, description="Input parameters for the task")

# ----------------------------
# Task Read / Response Schema
# ----------------------------
class TaskRead(TaskBase):
    id: str = Field(..., description="Unique identifier for the task")
    input: Optional[Dict[str, Any]] = Field(default_factory=dict, description="Input parameters for the task")
    result: Optional[Dict[str, Any]] = Field(None, description="Output/result of the task")
    created_at: datetime
    updated_at: datetime
    started_at: Optional[datetime] = None
    completed_at: Optional[datetime] = None
    project_id: Optional[str] = None
