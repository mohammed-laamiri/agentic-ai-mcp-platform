"""
Orchestrator service.

Coordinates:
- Agent execution
- Task lifecycle
- Future MCP / LangGraph flows
"""

from app.schemas.agent import AgentRead
from app.schemas.task import TaskCreate, TaskRead
from app.services.agent_service import AgentService
from app.services.task_service import TaskService


class OrchestratorService:
    """
    High-level workflow coordinator.
    """

    def __init__(
        self,
        task_service: TaskService,
        agent_service: AgentService,
    ) -> None:
        self._task_service = task_service
        self._agent_service = agent_service

    def run(self, agent: AgentRead, task_in: TaskCreate) -> TaskRead:
        """
        Run a task using an agent.

        This method will later:
        - Invoke LangGraph
        - Call MCP tools
        - Handle retries and reflection
        """
        execution_result = self._agent_service.execute(
            agent=agent,
            task=task_in,
        )

        return self._task_service.create(
            task_in=task_in,
            execution_result=execution_result,
        )
