"""
Agent service.

This module is responsible for:
- Executing agent logic
- Calling tools (later)
- Interacting with LLMs (later)

For now, this is a deterministic stub implementation.
"""

from datetime import datetime
from uuid import uuid4

from app.schemas.agent import AgentRead
from app.schemas.task import TaskCreate


class AgentService:
    """
    Executes tasks using a given agent.

    NOTE:
    - This is intentionally a stub
    - Real LLM / LangGraph logic will replace this later
    """

    def execute(self, agent: AgentRead, task: TaskCreate) -> dict:
        """
        Execute a task using an agent.

        Returns a structured execution result.
        """
        return {
            "execution_id": str(uuid4()),
            "agent_id": agent.id,
            "agent_name": agent.name,
            "input": task.description,
            "output": f"[STUB RESPONSE] Agent '{agent.name}' processed task.",
            "timestamp": datetime.utcnow().isoformat(),
        }
