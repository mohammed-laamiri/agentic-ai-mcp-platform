"""
Tool execution result schema.

Returned by all tools.
"""

from pydantic import BaseModel
from typing import Any


class ToolExecutionResult(BaseModel):
    tool_id: str
    success: bool
    output: Any | None = None
    error: str | None = None
