"""
Execution schemas.

Defines execution result returned by agents and orchestrator.
"""

from datetime import datetime, timezone
from typing import Any, Optional, List

from pydantic import BaseModel, Field

from app.schemas.tool_call import ToolCall


class ExecutionResult(BaseModel):
    """
    Final result of agent execution.

    This object represents the structured output of an agent run,
    including tool calls, output, timing, and error information.
    """

    tool_call_id: Optional[str] = Field(
        default=None,
        description="Associated tool call identifier if applicable",
    )

    tool_id: Optional[str] = Field(
        default=None,
        description="Tool identifier if execution was tool-driven",
    )

    status: str = Field(
        ...,
        description="Execution status (success, error, running, etc.)",
    )

    output: Optional[Any] = Field(
        default=None,
        description="Primary output of the execution",
    )

    error: Optional[str] = Field(
        default=None,
        description="Error message if execution failed",
    )

    tool_calls: List[ToolCall] = Field(
        default_factory=list,
        description="Tool calls issued during execution",
    )

    started_at: datetime = Field(
        default_factory=lambda: datetime.now(timezone.utc),
        description="Execution start timestamp (UTC)",
    )

    finished_at: datetime = Field(
        default_factory=lambda: datetime.now(timezone.utc),
        description="Execution completion timestamp (UTC)",
    )