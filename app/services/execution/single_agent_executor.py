"""
SingleAgentExecutor

Responsible for executing ONE agent.
Does NOT orchestrate multiple agents.
Does NOT create plans.

This is the lowest-level execution unit.
"""

from app.schemas.agent import AgentRead
from app.schemas.task import TaskCreate
from app.schemas.execution import ExecutionResult
from app.schemas.agent_execution_context import AgentExecutionContext

from app.services.agent_service import AgentService


class SingleAgentExecutor:
    """
    Executes a single agent.

    Responsibilities:
    - Receive agent
    - Execute agent logic via AgentService
    - Return normalized ExecutionResult

    Does NOT:
    - Know about plans
    - Know about orchestration
    - Execute tools
    - Manage execution lifecycle
    """

    def __init__(
        self,
        agent_service: AgentService,
    ) -> None:
        self._agent_service = agent_service

    # ==================================================
    # Public API
    # ==================================================

    def execute(
        self,
        agent: AgentRead,
        task_in: TaskCreate,
        context: AgentExecutionContext,
    ) -> ExecutionResult:
        """
        Execute ONE agent.

        Parameters
        ----------
        agent : AgentRead
            Agent to execute

        task_in : TaskCreate
            Task input

        context : AgentExecutionContext
            Shared execution context

        Returns
        -------
        ExecutionResult
            Normalized execution result
        """

        # --------------------------------------------------
        # Validate inputs (safety)
        # --------------------------------------------------
        if agent is None:
            raise ValueError("agent cannot be None")

        if task_in is None:
            raise ValueError("task_in cannot be None")

        if context is None:
            raise ValueError("context cannot be None")

        # --------------------------------------------------
        # Execute agent via AgentService
        # IMPORTANT: use 'task' parameter name because
        # AgentService.execute expects 'task'
        # --------------------------------------------------
        raw_result = self._agent_service.execute(
            agent=agent,
            task=task_in,
            context=context,
        )

        # --------------------------------------------------
        # Normalize result into ExecutionResult
        # --------------------------------------------------
        if isinstance(raw_result, ExecutionResult):
            return raw_result

        if isinstance(raw_result, dict):
            return ExecutionResult(**raw_result)

        # --------------------------------------------------
        # Invalid result protection
        # --------------------------------------------------
        raise TypeError(
            "AgentService.execute must return ExecutionResult or dict, "
            f"got {type(raw_result)}"
        )