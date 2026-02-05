"""
Tool result schema.

Represents the outcome of a tool execution.

Returned by:
- Tool executors
- Runtime engines
"""

from typing import Any, Dict, Optional
from pydantic import BaseModel, Field


class ToolResult(BaseModel):
    """
    Result of a tool execution.

    This object is SAFE to store, log, and return.
    """

    tool_id: str = Field(
        ...,
        description="ID of the executed tool",
    )

    success: bool = Field(
        ...,
        description="Whether the tool execution succeeded",
    )

    output: Optional[Any] = Field(
        default=None,
        description="Tool output payload",
    )

    error: Optional[str] = Field(
        default=None,
        description="Error message if execution failed",
    )

    metadata: Dict[str, Any] = Field(
        default_factory=dict,
        description="Execution metadata (latency, cost, retries, etc.)",
    )

    execution_id: Optional[str] = Field(
        default=None,
        description="Unique execution ID for MCP tracking"
    )

    retries: int = Field(
        default=0,
        description="Number of retries attempted for this tool call"
    )
