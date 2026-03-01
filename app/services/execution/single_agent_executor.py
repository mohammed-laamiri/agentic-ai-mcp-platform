"""
Async SingleAgentExecutor

Executes a single agent in an asynchronous manner.

Responsibilities:
- Receive a single agent
- Execute agent logic via AgentService asynchronously
- Return normalized ExecutionResult
"""

from app.schemas.agent import AgentRead
from app.schemas.task import TaskCreate
from app.schemas.execution import ExecutionResult
from app.schemas.agent_execution_context import AgentExecutionContext

from app.services.agent_service import AgentService


class SingleAgentExecutor:
    """
    Async executor for a single agent.
    """

    def __init__(self, agent_service: AgentService) -> None:
        self._agent_service = agent_service

    async def execute(
        self,
        agent: AgentRead,
        task_in: TaskCreate,
        context: AgentExecutionContext,
    ) -> ExecutionResult:
        """
        Execute a single agent asynchronously.

        Parameters
        ----------
        agent : AgentRead
            Agent to execute
        task_in : TaskCreate
            Input task
        context : AgentExecutionContext
            Shared execution context

        Returns
        -------
        ExecutionResult
            Normalized execution result
        """
        if agent is None or task_in is None or context is None:
            raise ValueError("agent, task_in, and context must all be provided")

        # Await agent service execution
        raw_result = await self._agent_service.execute(agent=agent, task=task_in, context=context)

        # Normalize to ExecutionResult
        if isinstance(raw_result, ExecutionResult):
            return raw_result

        if isinstance(raw_result, dict):
            return ExecutionResult(**raw_result)

        raise TypeError(
            f"AgentService.execute must return ExecutionResult or dict, got {type(raw_result)}"
        )
    
    async def _execute_single_agent_stream(
        self,
        agent: AgentRead,
        task: TaskCreate,
        context: AgentExecutionContext,
    ):
        """
        Stream events from single agent execution.
        """

        raw_result = await self._agent_service.execute(agent, task, context)

        # If agent returns streaming tokens (future support)
        if hasattr(raw_result, "__aiter__"):
            async for token in raw_result:
                yield {"type": "token", "content": token}
            return

        # Normal execution fallback
        if isinstance(raw_result, dict):
            yield {"type": "result", "data": raw_result}
        elif isinstance(raw_result, ExecutionResult):
            yield {"type": "result", "data": raw_result.model_dump()}