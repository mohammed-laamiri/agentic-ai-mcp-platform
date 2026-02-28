"""
MultiAgentExecutor

Executes agents sequentially for MULTI_AGENT strategy.

Responsibilities:
- Execute agents in order
- Pass context between agents
- Aggregate results safely
- Return unified ExecutionResult
"""

from typing import List

from app.schemas.agent import AgentRead
from app.schemas.task import TaskCreate
from app.schemas.execution import ExecutionResult
from app.schemas.agent_execution_context import AgentExecutionContext

from app.services.agent_service import AgentService


class MultiAgentExecutor:
    """
    Sequential multi-agent executor.

    Production-safe implementation.
    """

    def __init__(self, agent_service: AgentService | None = None) -> None:
        self._agent_service = agent_service or AgentService()

    # ==========================================================
    # Main execution
    # ==========================================================

    def execute(
        self,
        agents: List[AgentRead],
        task_in: TaskCreate,
        context: AgentExecutionContext,
    ) -> ExecutionResult:
        """
        Execute agents sequentially.

        Always returns ExecutionResult.
        Never returns dict.
        Never throws unhandled exceptions.
        """

        last_output = None

        try:

            for agent in agents:

                result = self._agent_service.execute(
                    agent=agent,
                    task=task_in,
                    context=context,
                )

                # Normalize result if dict
                if isinstance(result, dict):
                    result = ExecutionResult(**result)

                # If execution failed → stop
                if result.status == "error":
                    return result

                # Store last output
                last_output = result.output

                # Update context memory safely
                if context and hasattr(context, "memory"):
                    context.memory["last_output"] = last_output

            # All agents executed successfully
            return ExecutionResult(
                status="success",
                output=last_output,
                error=None,
            )

        except Exception as exc:

            return ExecutionResult(
                status="error",
                output=None,
                error=f"Multi-agent execution failed: {str(exc)}",
            )