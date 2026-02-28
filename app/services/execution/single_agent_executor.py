from app.schemas.agent import AgentRead
from app.schemas.task import TaskCreate
from app.schemas.execution import ExecutionResult
from app.schemas.agent_execution_context import AgentExecutionContext

from app.services.agent_service import AgentService


class SingleAgentExecutor:
    """
    Executes a single agent.
    """

    def __init__(self, agent_service: AgentService) -> None:
        self._agent_service = agent_service

    def execute(
        self,
        agent: AgentRead,
        task_in: TaskCreate,
        context: AgentExecutionContext,
    ) -> ExecutionResult:

        if agent is None or task_in is None or context is None:
            raise ValueError("agent, task_in, and context must all be provided")

        raw_result = self._agent_service.execute(
            agent=agent,
            task=task_in,
            context=context,
        )

        if isinstance(raw_result, ExecutionResult):
            return raw_result

        if isinstance(raw_result, dict):
            return ExecutionResult(**raw_result)

        raise TypeError(
            f"AgentService.execute must return ExecutionResult or dict, got {type(raw_result)}"
        )