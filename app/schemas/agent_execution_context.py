from datetime import datetime
from typing import Optional, Dict, Any, List
from uuid import uuid4

from pydantic import BaseModel


class AgentExecutionContext(BaseModel):
    """
    Shared execution state across the agent runtime.
    """

    # ---------------- Execution identifiers ----------------
    run_id: str = str(uuid4())
    session_id: Optional[str] = None
    user_id: Optional[str] = None
    metadata: Dict[str, Any] = {}

    # ---------------- Execution lifecycle ----------------
    status: str = "pending"
    started_at: Optional[datetime] = None
    completed_at: Optional[datetime] = None
    error: Optional[str] = None

    # ---------------- Execution trace ----------------
    last_agent_id: Optional[str] = None
    last_execution_time: Optional[datetime] = None

    # ---------------- Tool tracking ----------------
    tool_calls: List[Dict[str, Any]] = []
    tool_results: List[Dict[str, Any]] = []

    # ---------------- Lifecycle methods ----------------
    def mark_running(self) -> None:
        self.status = "running"
        self.started_at = datetime.utcnow()

    def mark_completed(self, status: str = "completed") -> None:
        self.status = status
        self.completed_at = datetime.utcnow()

    def mark_failed(self, error: str) -> None:
        self.status = "failed"
        self.completed_at = datetime.utcnow()
        self.error = error

    # ---------------- Tool tracking methods ----------------
    def add_tool_call(self, tool_call: Dict[str, Any]) -> None:
        self.tool_calls.append(tool_call)

    def add_tool_result(self, tool_result: Dict[str, Any]) -> None:
        self.tool_results.append(tool_result)