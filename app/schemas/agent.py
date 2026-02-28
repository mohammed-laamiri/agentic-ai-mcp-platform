# app/schemas/agent.py

from enum import Enum
from typing import Optional, Dict, Any

from pydantic import BaseModel, Field


class AgentType(str, Enum):
    REACT = "react"
    PLANNER = "planner"


class AgentCreate(BaseModel):
    """
    Input payload for creating an Agent.
    """

    name: str
    agent_type: AgentType = Field(
        default=AgentType.PLANNER,
        description="Agent classification type",
    )


class AgentRead(BaseModel):
    """
    Read-only representation of an Agent.

    Used by services and orchestrator.
    Now includes `metadata` for runtime info like assigned tools.
    """

    id: str
    name: str
    agent_type: Optional[AgentType] = Field(
        default=None,
        description="Optional agent classification (not required for stubs)",
    )
    metadata: Dict[str, Any] = Field(
        default_factory=dict,
        description="Runtime metadata storage (assigned tools, planning info, etc.)",
    )