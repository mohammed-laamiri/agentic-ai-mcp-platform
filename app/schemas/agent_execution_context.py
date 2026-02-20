"""
Agent Execution Context.

Execution-scoped context object used during
a single orchestrator run.

Architectural intent:
- Created by the Orchestrator
- Read-only for agents (conceptually)
- Collects execution metadata
- Stores execution trace
- Stores execution variables
"""

from datetime import datetime
from typing import List, Dict, Any, Optional
from uuid import uuid4

from pydantic import BaseModel, Field

from app.schemas.tool_call import ToolCall


class AgentExecutionContext(BaseModel):
    """
    Execution-scoped context for a single orchestration run.

    IMPORTANT:
    - Orchestrator owns mutation
    - Agents should treat this as read-only
    """

    # ==========================================================
    # Core identity
    # ==========================================================

    run_id: str = Field(
        default_factory=lambda: str(uuid4()),
        description="Unique identifier for this execution run",
    )

    started_at: datetime = Field(
        default_factory=datetime.utcnow,
        description="Timestamp when orchestration began",
    )

    # ==========================================================
    # Tool Calls
    # ==========================================================

    tool_calls: List[ToolCall] = Field(default_factory=list)

    # ==========================================================
    # Execution Trace
    # ==========================================================

    execution_trace: List[Dict[str, Any]] = Field(default_factory=list)

    # ==========================================================
    # Execution Variables
    # ==========================================================

    variables: Dict[str, Any] = Field(default_factory=dict)

    # ==========================================================
    # Pydantic v2 fix: ensure proper runtime types
    # ==========================================================

    def model_post_init(self, __context: Any) -> None:
        """
        Ensures mutable fields are proper runtime objects,
        not FieldInfo (fixes pylint + typing issues).
        """

        if self.tool_calls is None:
            self.tool_calls = []

        if self.execution_trace is None:
            self.execution_trace = []

        if self.variables is None:
            self.variables = {}

    # ==========================================================
    # Variable Access API
    # ==========================================================

    def get_variable(
        self,
        key: str,
        default: Optional[Any] = None,
    ) -> Any:
        return self.variables.get(key, default)

    def set_variable(
        self,
        key: str,
        value: Any,
    ) -> None:
        self.variables[key] = value

    # ==========================================================
    # Execution Trace API
    # ==========================================================

    def add_trace(
        self,
        event_type: str,
        payload: Optional[Dict[str, Any]] = None,
    ) -> None:
        event = {
            "timestamp": datetime.utcnow().isoformat(),
            "run_id": self.run_id,
            "type": event_type,
            "payload": payload or {},
        }

        self.execution_trace.append(event)

    # ==========================================================
    # Helpers
    # ==========================================================

    def duration_seconds(self) -> float:
        return (datetime.utcnow() - self.started_at).total_seconds()

    # ==========================================================
    # Pydantic config
    # ==========================================================

    class Config:
        arbitrary_types_allowed = True
