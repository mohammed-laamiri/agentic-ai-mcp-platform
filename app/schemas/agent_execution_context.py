"""
Agent Execution Context.

Execution-scoped context object used during
a single orchestrator run.

Architectural intent:
- Created by the Orchestrator
- Read-only for agents
- Collects execution metadata and tool spans
"""

from datetime import datetime, timezone
from typing import List, Dict, Any, Optional
from uuid import uuid4

from pydantic import BaseModel, Field, ConfigDict

from app.schemas.tool_call import ToolCall
from app.schemas.tool_result import ToolResult


class AgentExecutionContext(BaseModel):
    """
    Execution-scoped context for a single orchestration run.

    IMPORTANT:
    - Agents must treat this as READ-ONLY
    - Orchestrator owns mutation
    """

    model_config = ConfigDict(validate_assignment=True)

    # -------------------------------------------------
    # Core Run Metadata
    # -------------------------------------------------

    run_id: str = Field(
        default_factory=lambda: str(uuid4()),
        description="Unique identifier for this execution run",
    )

    started_at: datetime = Field(
        default_factory=lambda: datetime.now(timezone.utc),
        description="Timestamp when orchestration began",
    )

    finished_at: Optional[datetime] = Field(
        default=None,
        description="Timestamp when orchestration finished",
    )

    status: str = Field(
        default="running",
        description="Execution status: running | completed | failed",
    )

    # -------------------------------------------------
    # Tool Spans
    # -------------------------------------------------

    tool_calls: List[ToolCall] = Field(
        default_factory=list,
        description="Tool calls declared by agents during execution",
    )

    tool_results: List[ToolResult] = Field(
        default_factory=list,
        description="Results produced by tool execution engine",
    )

    # -------------------------------------------------
    # Optional Execution Metadata
    # -------------------------------------------------

    metadata: Dict[str, Any] = Field(
        default_factory=dict,
        description="Arbitrary execution metadata (latency, tokens, costs, etc.)",
    )

    # -------------------------------------------------
    # MCP Helpers (Safe, Non-Breaking)
    # -------------------------------------------------

    def add_tool_call(self, call: ToolCall) -> None:
        """
        Append a tool call to the execution context.
        Ensures correlation ID exists.
        """
        call.ensure_call_id()
        self.tool_calls.append(call)

    def add_tool_result(self, result: ToolResult) -> None:
        """
        Append a tool result to the execution context.
        """
        self.tool_results.append(result)

    def mark_completed(self, status: str = "completed") -> None:
        """
        Mark execution as finished.
        """
        self.status = status
        self.finished_at = datetime.now(timezone.utc)

    def to_mcp_dict(self) -> Dict[str, Any]:
        """
        MCP-safe serialization.
        """
        return {
            "run_id": self.run_id,
            "status": self.status,
            "started_at": self.started_at.isoformat(),
            "finished_at": self.finished_at.isoformat() if self.finished_at else None,
            "tool_calls": [c.to_mcp_dict() for c in self.tool_calls],
            "tool_results": [r.model_dump() for r in self.tool_results],
            "metadata": self.metadata,
        }
