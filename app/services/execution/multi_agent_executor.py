from typing import List

from app.schemas.agent import AgentRead
from app.schemas.task import TaskCreate
from app.schemas.execution import ExecutionResult
from app.schemas.agent_execution_context import AgentExecutionContext

from app.services.agent_service import AgentService


class MultiAgentExecutor:
    """
    Executes multiple agents sequentially.
    """

    def __init__(self, agent_service: AgentService | None = None) -> None:
        self._agent_service = agent_service or AgentService()

    def execute(
        self,
        agents: List[AgentRead],
        task_in: TaskCreate,
        context: AgentExecutionContext,
    ) -> ExecutionResult:

        last_output = None

        try:
            for agent in agents:
                result = self._agent_service.execute(
                    agent=agent,
                    task=task_in,
                    context=context,
                )

                if isinstance(result, dict):
                    result = ExecutionResult(**result)

                if result.status == "error":
                    return result

                last_output = result.output

                # Update context metadata safely
                context.metadata["last_output"] = last_output

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