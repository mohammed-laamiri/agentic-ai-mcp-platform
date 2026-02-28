"""
Agent Execution Context schema.

Shared mutable context passed between planner, agents, and executors.

This enables:

• execution trace tracking
• metadata propagation
• multi-agent coordination
• future memory and state support
"""

from datetime import datetime
from typing import Optional, Dict, Any

from pydantic import BaseModel, Field


class AgentExecutionContext(BaseModel):
    """
    Shared execution state across the agent runtime.
    """

    # --------------------------------------------------
    # Execution metadata storage
    # --------------------------------------------------

    metadata: Dict[str, Any] = Field(
        default_factory=dict,
        description="Flexible metadata storage for execution pipeline",
    )

    # --------------------------------------------------
    # Execution trace tracking
    # --------------------------------------------------

    last_agent_id: Optional[str] = Field(
        default=None,
        description="ID of the most recently executed agent",
    )

    last_execution_time: Optional[datetime] = Field(
        default=None,
        description="Timestamp of last agent execution",
    )

    # --------------------------------------------------
    # Optional future extensions
    # --------------------------------------------------

    session_id: Optional[str] = Field(
        default=None,
        description="Execution session identifier",
    )

    user_id: Optional[str] = Field(
        default=None,
        description="Optional user identifier",
    )