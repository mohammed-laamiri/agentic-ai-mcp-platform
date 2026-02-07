"""
Agent Execution Context.

Execution-scoped context object used during
a single orchestrator run.

Architectural intent:
- Created by the Orchestrator
- Read-only for agents
- Collects execution metadata and tool spans
"""

from datetime import datetime
from typing import List, Optional
from uuid import uuid4

from pydantic import BaseModel, Field, PrivateAttr

from app.schemas.tool_call import ToolCall
from app.schemas.tool_result import ToolResult


class AgentExecutionContext(BaseModel):
    """
    Execution-scoped context for a single orchestration run.

    IMPORTANT:
    - Agents treat this as READ-ONLY
    - Orchestrator owns mutation
    """

    run_id: str = Field(default_factory=lambda: str(uuid4()))
    started_at: datetime = Field(default_factory=datetime.utcnow)
    finished_at: Optional[datetime] = None
    status: str = Field(default="running")

    # -------------------------------------------------
    # Runtime-only mutable state (NOT pydantic fields)
    # -------------------------------------------------

    _tool_calls: List[ToolCall] = PrivateAttr(default_factory=list)
    _tool_results: List[ToolResult] = PrivateAttr(default_factory=list)

    # -------------------------------------------------
    # Accessors (read-only for agents)
    # -------------------------------------------------

    @property
    def tool_calls(self) -> List[ToolCall]:
        return self._tool_calls

    @property
    def tool_results(self) -> List[ToolResult]:
        return self._tool_results

    # -------------------------------------------------
    # Mutation API (orchestrator only)
    # -------------------------------------------------

    def add_tool_call(self, call: ToolCall) -> None:
        """
        Append a tool call to the execution context.
        Ensures correlation ID exists.
        """
        call.ensure_call_id()
        self._tool_calls.append(call)

    def add_tool_result(self, result: ToolResult) -> None:
        """
        Append a tool result to the execution context.
        """
        self._tool_results.append(result)

    def mark_completed(self, status: str = "completed") -> None:
        """
        Mark execution as finished.
        """
        self.status = status
        self.finished_at = datetime.utcnow()
