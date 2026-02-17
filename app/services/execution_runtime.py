"""
Execution Runtime

Responsible for executing an ExecutionPlan produced by PlannerAgent.

This layer separates:

PLANNING  → handled by PlannerAgent
EXECUTION → handled by ExecutionRuntime
ORCHESTRATION → handled by OrchestratorService

This improves:
- separation of concerns
- testability
- extensibility
- future async / distributed execution
"""

from typing import Optional, List
import uuid

from app.schemas.agent import AgentRead
from app.schemas.task import TaskCreate
from app.schemas.execution_plan import ExecutionPlan
from app.schemas.execution_strategy import ExecutionStrategy
from app.schemas.execution import ExecutionResult
from app.schemas.agent_execution_context import AgentExecutionContext
from app.schemas.tool_call import ToolCall

from app.services.agent_service import AgentService
from app.services.tool_execution_engine import ToolExecutionEngine


class ExecutionRuntime:
    """
    Execution engine responsible for executing plans safely and consistently.

    Does NOT persist anything.
    Does NOT create tasks.

    Only executes and returns ExecutionResult.
    """

    def __init__(
        self,
        agent_service: AgentService,
        tool_engine: ToolExecutionEngine,
    ):
        self._agent_service = agent_service
        self._tool_engine = tool_engine

    # ==================================================
    # Public API
    # ==================================================

    def execute(
        self,
        agent: AgentRead,
        task: TaskCreate,
        plan: ExecutionPlan,
        context: AgentExecutionContext,
    ) -> ExecutionResult:
        """
        Entry point for executing any execution plan.
        """

        # --------------------------------------------------
        # Ensure context is properly initialized
        # --------------------------------------------------

        if context.run_id is None:
            context.run_id = self._generate_run_id()

        if context.tool_calls is None:
            context.tool_calls = []

        # --------------------------------------------------
        # Execute according to strategy
        # --------------------------------------------------

        if plan.strategy == ExecutionStrategy.SINGLE_AGENT:
            result = self._execute_single_agent(agent, task, context)

        elif plan.strategy == ExecutionStrategy.MULTI_AGENT:
            result = self._execute_multi_agent(task, plan, context)

        else:
            raise ValueError(f"Unsupported strategy: {plan.strategy}")

        # --------------------------------------------------
        # Execute collected tool calls
        # --------------------------------------------------

        if context.tool_calls:

            tool_results = self._tool_engine.execute_batch(
                tool_calls=context.tool_calls,
                context=context,
                fail_fast=True,
            )

            # Ensure child_results list exists
            if result.child_results is None:
                result.child_results = []

            result.child_results.extend(tool_results)

        return result

    # ==================================================
    # Single agent execution
    # ==================================================

    def _execute_single_agent(
        self,
        agent: AgentRead,
        task: TaskCreate,
        context: AgentExecutionContext,
    ) -> ExecutionResult:

        raw_result = self._agent_service.execute(
            agent,
            task,
            context,
        )

        # --------------------------------------------------
        # Collect tool calls safely
        # --------------------------------------------------

        tool_calls = raw_result.get("tool_calls", [])

        for call in tool_calls:
            context.add_tool_call(ToolCall(**call))

        # --------------------------------------------------
        # Convert to ExecutionResult
        # --------------------------------------------------

        return ExecutionResult(**raw_result)

    # ==================================================
    # Multi agent execution
    # ==================================================

    def _execute_multi_agent(
        self,
        task: TaskCreate,
        plan: ExecutionPlan,
        parent_context: AgentExecutionContext,
    ) -> ExecutionResult:

        child_results: List[ExecutionResult] = []

        for agent in plan.steps or []:

            # Child context shares same run_id
            child_context = AgentExecutionContext(
                run_id=parent_context.run_id,
                tool_calls=[],
            )

            intermediate_task = TaskCreate(
                name=task.name,
                description=task.description,
                input=task.input,
                status=task.status,
                priority=task.priority,
            )

            raw_result = self._agent_service.execute(
                agent,
                intermediate_task,
                child_context,
            )

            # --------------------------------------------------
            # Merge tool calls upward to parent context
            # --------------------------------------------------

            tool_calls = raw_result.get("tool_calls", [])

            for call in tool_calls:
                parent_context.add_tool_call(ToolCall(**call))

            child_results.append(
                ExecutionResult(**raw_result)
            )

        return ExecutionResult(
            execution_id=f"multi-{parent_context.run_id}",
            output=None,
            status="SUCCESS",
            child_results=child_results,
        )

    # ==================================================
    # Helpers
    # ==================================================

    def _generate_run_id(self) -> str:
        """
        Generate unique execution run ID.
        """
        return f"run-{uuid.uuid4()}"
