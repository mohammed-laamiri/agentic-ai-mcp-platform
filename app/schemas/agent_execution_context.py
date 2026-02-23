"""
Agent Execution Context.

Execution-scoped context object used during
a single orchestrator run.

Architectural intent:
- Created by the Orchestrator
- Read-only for agents (mutation only via helper methods)
- Collects execution metadata
- Tracks tool calls and results
"""

from datetime import datetime, timezone
from typing import List, Optional, Dict, Any
from uuid import uuid4

from typing_extensions import Annotated

from pydantic import BaseModel, Field, ConfigDict

from app.schemas.tool_call import ToolCall
from app.schemas.tool_result import ToolResult


class AgentExecutionContext(BaseModel):
    """
    Execution-scoped context for a single orchestration run.

    IMPORTANT:
    - Created and owned by Orchestrator
    - Agents should treat this as READ-ONLY
    - Provides structured execution trace
    """

    # Required for proper typing and runtime behavior
    model_config = ConfigDict(arbitrary_types_allowed=True)

    # ==========================================================
    # Core execution identity
    # ==========================================================

    run_id: str = Field(
        default_factory=lambda: str(uuid4()),
        description="Unique identifier for this execution run",
    )

    started_at: datetime = Field(
        default_factory=lambda: datetime.now(timezone.utc),
        description="Execution start timestamp",
    )

    completed_at: Optional[datetime] = Field(
        default=None,
        description="Execution completion timestamp",
    )

    status: str = Field(
        default="running",
        description="Execution status (running, completed, failed)",
    )

    error: Optional[str] = Field(
        default=None,
        description="Execution error if failed",
    )

    # ==========================================================
    # Tool execution tracking
    # ==========================================================

    tool_calls: Annotated[
        List[ToolCall],
        Field(default_factory=list, description="Tool calls issued during execution"),
    ]

    tool_results: Annotated[
        List[ToolResult],
        Field(default_factory=list, description="Tool results produced during execution"),
    ]

    # ==========================================================
    # Additional runtime metadata
    # ==========================================================

    metadata: Annotated[
        Dict[str, Any],
        Field(default_factory=dict, description="Execution metadata"),
    ]

    # ==========================================================
    # Safe helper methods (Orchestrator-owned mutations)
    # ==========================================================

    def add_tool_call(self, tool_call: ToolCall) -> None:
        """Register a tool call in execution trace."""
        self.tool_calls.append(tool_call)

    def add_tool_result(self, tool_result: ToolResult) -> None:
        """Register a tool result in execution trace."""
        self.tool_results.append(tool_result)

    def mark_completed(self) -> None:
        """Mark execution as completed."""
        self.completed_at = datetime.now(timezone.utc)
        self.status = "completed"

    def mark_failed(self, error: str) -> None:
        """Mark execution as failed."""
        self.completed_at = datetime.now(timezone.utc)
        self.status = "failed"
        self.error = error

    # ==========================================================
    # Convenience helpers
    # ==========================================================

    def is_running(self) -> bool:
        return self.status == "running"

    def is_completed(self) -> bool:
        return self.status == "completed"

    def is_failed(self) -> bool:
        return self.status == "failed"