"""
ExecutionService

Central execution dispatcher.

This service selects the correct executor based on ExecutionStrategy.

This keeps OrchestratorService clean and prevents execution logic duplication.
"""

from app.schemas.execution_strategy import ExecutionStrategy
from app.schemas.execution_plan import ExecutionPlan
from app.schemas.execution import ExecutionResult
from app.schemas.agent_execution_context import AgentExecutionContext
from app.schemas.task import TaskCreate

from app.services.execution.single_agent_executor import SingleAgentExecutor
from app.services.execution.multi_agent_executor import MultiAgentExecutor

from app.services.agent_service import AgentService


class ExecutionService:
    """
    Dispatches execution to correct executor.
    """

    def __init__(
        self,
        agent_service: AgentService,
    ) -> None:

        self._single_executor = SingleAgentExecutor(
            agent_service=agent_service,
        )

        self._multi_executor = MultiAgentExecutor(
            agent_service=agent_service,
        )

    # ==================================================
    # Public API
    # ==================================================

    def execute_plan(
        self,
        plan: ExecutionPlan,
        task_in: TaskCreate,   # ← MATCH YOUR EXECUTORS
        context: AgentExecutionContext,
    ) -> ExecutionResult:
        """
        Execute based on execution plan.
        """

        if plan.strategy == ExecutionStrategy.SINGLE_AGENT:

            return self._single_executor.execute(
                agent=plan.steps[0],
                task_in=task_in,     # ← FIXED
                context=context,
            )

        if plan.strategy == ExecutionStrategy.MULTI_AGENT:

            return self._multi_executor.execute(
                agents=plan.steps,
                task_in=task_in,     # ← FIXED
                context=context,
            )

        raise ValueError(
            f"Unsupported execution strategy: {plan.strategy}"
        )