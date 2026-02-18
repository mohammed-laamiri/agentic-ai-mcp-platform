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

from app.schemas.agent import AgentRead
from app.schemas.task import TaskCreate
from app.schemas.execution_plan import ExecutionPlan
from app.schemas.execution_strategy import ExecutionStrategy
from app.schemas.execution import ExecutionResult
from app.schemas.agent_execution_context import AgentExecutionContext
from app.schemas.tool_call import ToolCall

from app.services.agent_service import AgentService
from app.services.tool_execution_engine import ToolExecutionEngine

from app.repositories.execution_history_repository import (
    ExecutionHistoryRepository,
)


class ExecutionRuntime:
    """
    Execution engine responsible for executing plans safely and consistently.

    Responsibilities:
    - Execute agent plans
    - Execute tool calls
    - Aggregate results
    - Persist execution history

    Does NOT create tasks.
    Does NOT write memory.

    Only executes and records execution history.
    """

    def __init__(
        self,
        agent_service: AgentService,
        tool_engine: ToolExecutionEngine,
        history_repository: Optional[ExecutionHistoryRepository] = None,
    ):
        self._agent_service = agent_service
        self._tool_engine = tool_engine
        self._history_repository = history_repository

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

        context.mark_running()

        try:

            if plan.strategy == ExecutionStrategy.SINGLE_AGENT:

                result = self._execute_single_agent(
                    agent,
                    task,
                    context,
                )

            elif plan.strategy == ExecutionStrategy.MULTI_AGENT:

                result = self._execute_multi_agent(
                    task,
                    plan,
                    context,
                )

            else:
                raise ValueError(
                    f"Unsupported strategy: {plan.strategy}"
                )

            # ==================================================
            # Execute tools if collected
            # ==================================================

            if context.tool_calls:

                tool_results = self._tool_engine.execute_batch(
                    tool_calls=context.tool_calls,
                    context=context,
                    fail_fast=True,
                )

                result.child_results = (
                    result.child_results or []
                ) + tool_results

            context.mark_completed("completed")

            # ==================================================
            # Persist execution history (SAFE)
            # ==================================================

            self._persist_history(
                agent=agent,
                task=task,
                result=result,
                context=context,
            )

            return result

        except Exception as exc:

            context.mark_completed("failed")

            self._persist_history(
                agent=agent,
                task=task,
                result=None,
                context=context,
                error=str(exc),
            )

            raise

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

        tool_calls = raw_result.get("tool_calls", [])

        for call in tool_calls:
            context.add_tool_call(
                ToolCall(**call)
            )

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

            child_context = AgentExecutionContext(
                run_id=parent_context.run_id
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

            tool_calls = raw_result.get("tool_calls", [])

            for call in tool_calls:

                parent_context.add_tool_call(
                    ToolCall(**call)
                )

            child_results.append(
                ExecutionResult(**raw_result)
            )

        return ExecutionResult(
            execution_id=f"multi-{task.name}",
            output=None,
            status="SUCCESS",
            child_results=child_results,
        )

    # ==================================================
    # History Persistence
    # ==================================================

    def _persist_history(
        self,
        agent: AgentRead,
        task: TaskCreate,
        result: Optional[ExecutionResult],
        context: AgentExecutionContext,
        error: Optional[str] = None,
    ) -> None:
        """
        Persist execution history safely.
        """

        if not self._history_repository:
            return

        try:

            self._history_repository.save(
                agent_id=agent.id,
                task_name=task.name,
                run_id=context.run_id,
                status=context.status,
                execution_result=(
                    result.model_dump()
                    if result
                    else None
                ),
                error=error,
                metadata={
                    "task_description": task.description,
                },
            )

        except Exception:
            # NEVER break execution because of logging
            pass
