"""
Tool result schema.

Represents the outcome of a tool execution.

Returned by:
- ToolExecutor
- ToolExecutionEngine
"""

from typing import Any, Optional
from datetime import datetime
from pydantic import BaseModel


class ToolResult(BaseModel):
    """
    Canonical result of tool execution.

    This is the runtime contract between:
    - Executor
    - Engine
    - Orchestrator
    - API layer
    """

    tool_call_id: Optional[str] = None

    tool_id: str

    # execution state
    status: str  # "success" | "error"

    # tool output
    output: Optional[Any] = None

    # error message (if failed)
    error: Optional[str] = None

    # observability
    started_at: datetime
    finished_at: datetime