"""
Async MultiAgentExecutor

Executes multiple agents sequentially in an asynchronous manner.

Responsibilities:
- Execute agents in order asynchronously
- Pass context between agents
- Aggregate results safely
- Return unified ExecutionResult
"""

from typing import List

from app.schemas.agent import AgentRead
from app.schemas.task import TaskCreate
from app.schemas.execution import ExecutionResult
from app.schemas.agent_execution_context import AgentExecutionContext
from app.schemas.execution_plan import ExecutionPlan

from app.services.agent_service import AgentService


class MultiAgentExecutor:
    """
    Sequential async multi-agent executor.
    """

    def __init__(self, agent_service: AgentService | None = None) -> None:
        self._agent_service = agent_service or AgentService()

    async def execute(
        self,
        agents: List[AgentRead],
        task_in: TaskCreate,
        context: AgentExecutionContext,
    ) -> ExecutionResult:
        """
        Execute agents sequentially in async mode.

        Parameters
        ----------
        agents : List[AgentRead]
            Agents to execute
        task_in : TaskCreate
            Input task
        context : AgentExecutionContext
            Shared execution context

        Returns
        -------
        ExecutionResult
            Aggregated execution result
        """
        last_output = None

        try:
            for agent in agents:
                # Await agent execution
                result = await self._agent_service.execute(
                    agent=agent,
                    task=task_in,
                    context=context,
                )

                # Normalize dict to ExecutionResult
                if isinstance(result, dict):
                    result = ExecutionResult(**result)

                # Stop on error
                if result.status == "error":
                    return result

                # Store last output
                last_output = result.output

                # Update context metadata safely
                context.metadata["last_output"] = last_output

            # All agents executed successfully
            return ExecutionResult(
                status="success",
                output=last_output,
                child_results=[],
                error=None,
            )

        except Exception as exc:
            return ExecutionResult(
                status="error",
                output=None,
                child_results=[],
                error=f"Multi-agent execution failed: {str(exc)}",
            )
    async def _execute_multi_agent_stream(
        self,
        task: TaskCreate,
        plan: ExecutionPlan,
        context: AgentExecutionContext,
    ):
        """
        Stream multi-agent execution step-by-step.
        """

        for agent in plan.steps or []:
            yield {"type": "agent_start", "agent_id": agent.id}

            raw_result = await self._agent_service.execute(agent, task, context)

            if isinstance(raw_result, dict):
                yield {"type": "agent_result", "data": raw_result}
            elif isinstance(raw_result, ExecutionResult):
                yield {"type": "agent_result", "data": raw_result.model_dump()}    