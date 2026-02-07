"""
Tool call schema.

Represents a request to invoke a tool.

This is a PURE CONTRACT object:
- Created by agents or planners
- Interpreted by execution runtimes
- Never executes anything itself
"""

from typing import Any, Dict, Optional
from uuid import uuid4

from pydantic import BaseModel, Field, field_validator


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

    # -------------------------------------------------
    # MCP Hardening (non-breaking)
    # -------------------------------------------------

    @field_validator("tool_id")
    @classmethod
    def validate_tool_id(cls, v: str) -> str:
        if not v or not v.strip():
            raise ValueError("tool_id must be non-empty")
        return v

    @field_validator("call_id", mode="before")
    @classmethod
    def normalize_call_id(cls, v: Optional[str]) -> Optional[str]:
        """
        Ensure call_id is either None or a safe string.
        """
        if v is None:
            return None
        return str(v)

    # -------------------------------------------------
    # Helpers
    # -------------------------------------------------

    def ensure_call_id(self) -> str:
        """
        Ensure this ToolCall has a call_id and return it.
        """
        if not self.call_id:
            self.call_id = str(uuid4())
        return self.call_id

    def to_mcp_dict(self) -> Dict[str, Any]:
        """
        MCP-safe serialization.
        """
        return {
            "tool_id": self.tool_id,
            "arguments": self.arguments,
            "call_id": self.call_id,
        }
