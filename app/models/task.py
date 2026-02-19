# app/models/task.py

from typing import Optional, Dict, Any, List
from datetime import datetime

class Task:
    """
    In-memory Task model for Agentic AI MCP Platform.
    Compatible with TaskService and TaskRead schema.
    """
    def __init__(
        self,
        id: str,
        name: str,
        description: Optional[str],
        status: str,
        priority: int,
        input: Optional[Dict[str, Any]] = None,
        result: Optional[Any] = None,
        created_at: Optional[datetime] = None,
        updated_at: Optional[datetime] = None,
        started_at: Optional[datetime] = None,
        completed_at: Optional[datetime] = None,
        project_id: Optional[str] = None,
    ):
        self.id = id
        self.name = name
        self.description = description
        self.status = status
        self.priority = priority
        self.input = input or {}
        self.result = result
        self.created_at = created_at
        self.updated_at = updated_at
        self.started_at = started_at
        self.completed_at = completed_at
        self.project_id = project_id
