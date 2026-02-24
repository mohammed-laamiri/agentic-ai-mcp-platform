"""
MultiAgentExecutor

Executes multiple agents sequentially using shared execution context.
"""

from typing import List

from app.schemas.agent import AgentRead
from app.schemas.task import TaskCreate
from app.schemas.execution import ExecutionResult
from app.schemas.agent_execution_context import AgentExecutionContext

from app.services.agent_service import AgentService


class MultiAgentExecutor:
    """
    Executes multiple agents sequentially.

    Responsibilities:
    - Execute agents in order
    - Pass output of previous agent to next agent
    - Maintain shared execution context
    - Return final ExecutionResult
    """

    def __init__(self, agent_service: AgentService) -> None:
        self._agent_service = agent_service

    # ==================================================
    # Public API
    # ==================================================

    def execute(
        self,
        agents: List[AgentRead],
        task: TaskCreate,
        context: AgentExecutionContext,
    ) -> ExecutionResult:
        """
        Execute agents sequentially.

        Input → Agent1 → Agent2 → Agent3 → Final Output
        """

        if not agents:
            raise ValueError("MultiAgentExecutor requires at least one agent")

        current_input = task.description or ""
        final_result: ExecutionResult | None = None

        for agent in agents:

            intermediate_task = TaskCreate(
                description=current_input,
                input=current_input,
            )

            raw_result = self._agent_service.execute(
                agent=agent,
                task=intermediate_task,
                context=context,
            )

            final_result = ExecutionResult(**raw_result)

            # Pass output forward
            current_input = final_result.output or ""

        if final_result is None:
            raise RuntimeError("Multi-agent execution produced no result")

        return final_result