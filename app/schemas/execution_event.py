"""
Execution Event Schema.

Used for streaming execution progress to clients.
"""

from enum import Enum
from typing import Optional, Any, List, Dict
from pydantic import BaseModel, Field


class ExecutionEventType(str, Enum):
    """Types of events emitted during execution."""
    PLANNING_STARTED = "planning_started"
    PLAN_CREATED = "plan_created"
    EXECUTION_STARTED = "execution_started"
    AGENT_STARTED = "agent_started"
    AGENT_COMPLETED = "agent_completed"
    TOOL_STARTED = "tool_started"
    TOOL_COMPLETED = "tool_completed"
    EXECUTION_COMPLETED = "execution_completed"
    EXECUTION_FAILED = "execution_failed"


class ExecutionEvent(BaseModel):
    """
    Event emitted during task execution.

    Used for real-time streaming of execution progress.
    """

    type: ExecutionEventType = Field(..., description="Type of execution event")

    # Optional fields based on event type
    strategy: Optional[str] = Field(default=None, description="Execution strategy")
    steps: Optional[List[Dict[str, Any]]] = Field(default=None, description="Plan steps")
    agent_id: Optional[str] = Field(default=None, description="Agent ID")
    agent_name: Optional[str] = Field(default=None, description="Agent name")
    tool_id: Optional[str] = Field(default=None, description="Tool ID")
    output: Optional[Any] = Field(default=None, description="Output data")
    error: Optional[str] = Field(default=None, description="Error message")
    metadata: Optional[Dict[str, Any]] = Field(default=None, description="Additional metadata")
