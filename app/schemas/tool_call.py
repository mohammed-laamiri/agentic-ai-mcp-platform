"""
Tool call schema.

Represents a request to invoke a tool.

This is a PURE CONTRACT object:
- Created by agents or planners
- Interpreted by execution runtimes
- Never executes anything itself
"""

from typing import Any, Dict, Optional
from pydantic import BaseModel, Field


class ToolCall(BaseModel):
    """
    Intent to invoke a tool.

    Architectural role:
    - Declares WHAT tool should be called
    - Declares WITH WHAT inputs
    - Does NOT perform execution
    """

    tool_id: str = Field(
        ...,
        description="Unique identifier of the tool to invoke",
    )

    arguments: Dict[str, Any] = Field(
        default_factory=dict,
        description="Arguments passed to the tool",
    )

    call_id: Optional[str] = Field(
        default=None,
        description="Optional correlation ID for tracing",
    )
