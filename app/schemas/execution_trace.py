"""
Execution Trace Schema.

Represents a structured observability event during runtime.

Used for:
- Tool execution tracing
- Agent execution tracing
- Orchestrator lifecycle tracing
- Observability and debugging
"""

from datetime import datetime, timezone
from typing import Any, Dict, Optional
from uuid import uuid4

from pydantic import BaseModel, Field


class ExecutionEvent(BaseModel):
    """
    A single execution trace event.
    """

    event_id: str = Field(default_factory=lambda: str(uuid4()))

    run_id: Optional[str] = Field(
        default=None,
        description="Execution run identifier",
    )

    parent_span_id: Optional[str] = Field(
        default=None,
        description="Parent span for nested tracing",
    )

    span_id: str = Field(
        default_factory=lambda: str(uuid4()),
        description="Unique span identifier",
    )

    event_type: str = Field(
        ...,
        description="Type of event (tool_start, tool_finish, agent_start, etc.)",
    )

    name: str = Field(
        ...,
        description="Tool name, agent name, or system component",
    )

    status: str = Field(
        default="running",
        description="running | success | error",
    )

    metadata: Dict[str, Any] = Field(
        default_factory=dict,
        description="Additional structured metadata",
    )

    timestamp: datetime = Field(
        default_factory=lambda: datetime.now(timezone.utc),
    )

    duration_ms: Optional[float] = Field(
        default=None,
        description="Execution duration in milliseconds",
    )


    model_config = {
        "arbitrary_types_allowed": True
    }
