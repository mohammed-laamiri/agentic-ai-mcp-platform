"""
Tool result schema.

Represents the outcome of a tool execution.

Returned by:
- ToolExecutor
- ToolExecutionEngine
"""

from typing import Any, Optional, Dict
from datetime import datetime, timezone
from pydantic import BaseModel, Field


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

    # execution state - supports both success (bool) and status (str)
    success: bool = Field(default=True)
    status: Optional[str] = Field(default=None)

    # tool output
    output: Optional[Any] = None

    # error message (if failed)
    error: Optional[str] = None

    # additional tracking
    execution_id: Optional[str] = None
    retries: int = 0
    metadata: Dict[str, Any] = Field(default_factory=dict)

    # observability
    started_at: Optional[datetime] = Field(default_factory=lambda: datetime.now(timezone.utc))
    finished_at: Optional[datetime] = Field(default_factory=lambda: datetime.now(timezone.utc))

    @property
    def is_error(self) -> bool:
        """Returns True if this result represents an error."""
        return not self.success

    @property
    def has_output(self) -> bool:
        """Returns True if output is not None."""
        return self.output is not None

    def to_log_dict(self) -> Dict[str, Any]:
        """Return a log-safe dictionary representation."""
        return {
            "tool_id": self.tool_id,
            "tool_call_id": self.tool_call_id,
            "success": self.success,
            "error": self.error,
            "execution_id": self.execution_id,
            "retries": self.retries,
            "metadata": self.metadata,
        }
