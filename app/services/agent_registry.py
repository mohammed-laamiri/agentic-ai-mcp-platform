"""
Agent Registry
==============

Central registry responsible for resolving AgentRead schemas into
executable agent service instances.

Why this exists:
----------------

ExecutionPlan contains AgentRead objects, which are schemas.

Schemas are NOT executable.

This registry converts:

    AgentRead  →  Executable Agent Service

Architecture Flow:
------------------

PlannerAgent
    ↓
ExecutionPlan
    ↓
AgentRead
    ↓
AgentRegistry   ← THIS FILE
    ↓
AgentService instance
    ↓
ExecutionRuntime
"""

from typing import Dict

from app.schemas.agent import AgentRead

from app.services.agent_service import AgentService


class AgentRegistry:
    """
    Registry that maps agent names to executable agent service instances.

    This enables dynamic agent execution at runtime.
    """

    def __init__(self):
        """
        Initialize empty agent registry.
        """

        # Internal mapping:
        #
        # key   = agent name
        # value = agent service instance
        #
        self._agents: Dict[str, AgentService] = {}

    def register(
        self,
        agent_name: str,
        agent_service: AgentService,
    ) -> None:
        """
        Register agent service instance.

        Parameters
        ----------
        agent_name : str
            Unique agent identifier

        agent_service : AgentService
            Executable agent instance
        """

        if not agent_name:
            raise ValueError("agent_name cannot be empty")

        if agent_service is None:
            raise ValueError("agent_service cannot be None")

        self._agents[agent_name] = agent_service

    def get(
        self,
        agent: AgentRead,
    ) -> AgentService:
        """
        Resolve AgentRead schema to executable agent service.

        Parameters
        ----------
        agent : AgentRead

        Returns
        -------
        AgentService

        Raises
        ------
        ValueError if agent not registered
        """

        if agent is None:
            raise ValueError("AgentRead cannot be None")

        agent_name = agent.name

        if agent_name not in self._agents:
            raise ValueError(
                f"Agent not registered: {agent_name}"
            )

        return self._agents[agent_name]

    def list_agents(self) -> Dict[str, AgentService]:
        """
        Return all registered agents.

        Useful for debugging and observability.
        """

        return self._agents.copy()
