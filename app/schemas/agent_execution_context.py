from datetime import datetime, timezone
from typing import Optional, Dict, Any, List, Union
from uuid import uuid4

from pydantic import BaseModel, Field


class AgentExecutionContext(BaseModel):
    """
    Shared execution state across the agent runtime.
    """

    # ---------------- Execution identifiers ----------------
    run_id: str = Field(default_factory=lambda: str(uuid4()))
    session_id: Optional[str] = None
    user_id: Optional[str] = None
    metadata: Dict[str, Any] = Field(default_factory=dict)

    # ---------------- Execution lifecycle ----------------
    status: str = "pending"
    started_at: Optional[datetime] = None
    completed_at: Optional[datetime] = None
    finished_at: Optional[datetime] = None  # Alias for completed_at
    error: Optional[str] = None

    # ---------------- Execution trace ----------------
    last_agent_id: Optional[str] = None
    last_execution_time: Optional[datetime] = None

    # ---------------- Tool tracking ----------------
    tool_calls: List[Any] = Field(default_factory=list)
    tool_results: List[Any] = Field(default_factory=list)

    # ---------------- Lifecycle methods ----------------
    def mark_running(self) -> None:
        self.status = "running"
        self.started_at = datetime.now(timezone.utc)

    def mark_completed(self, status: str = "completed") -> None:
        self.status = status
        now = datetime.now(timezone.utc)
        self.completed_at = now
        self.finished_at = now

    def mark_failed(self, error: str) -> None:
        self.status = "failed"
        now = datetime.now(timezone.utc)
        self.completed_at = now
        self.finished_at = now
        self.error = error

    # ---------------- Output methods (for backward compatibility) ----------------
    def set_final_output(self, output: str) -> None:
        """Set the final output in metadata."""
        self.metadata["final_output"] = output

    # ---------------- Tool tracking methods ----------------
    def add_tool_call(self, tool_call: Any) -> None:
        """Add a tool call to the tracking list."""
        self.tool_calls.append(tool_call)

    def add_tool_result(self, tool_result: Any) -> None:
        """Add a tool result to the tracking list."""
        self.tool_results.append(tool_result)
