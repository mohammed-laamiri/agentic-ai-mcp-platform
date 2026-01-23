from enum import Enum
from pydantic import BaseModel, Field


class AgentType(str, Enum):
    PLANNER = "planner"
    EXECUTOR = "executor"
    TOOL = "tool"
    RAG = "rag"
    CRITIC = "critic"


class AgentBase(BaseModel):
    """
    Base attributes shared by all agents.
    """

    name: str = Field(..., description="Human-readable agent name")
    agent_type: AgentType
    description: str | None = None


class AgentCreate(AgentBase):
    """
    Schema for creating an agent.
    """
    pass


class AgentRead(AgentBase):
    """
    Schema returned to API consumers.
    """

    id: str
