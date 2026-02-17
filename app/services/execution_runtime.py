"""
Execution Runtime

Responsible for executing an ExecutionPlan produced by PlannerAgent.

This layer separates:

PLANNING  → handled by PlannerAgent
EXECUTION → handled by ExecutionRuntime
ORCHESTRATION → handled by OrchestratorService

Now also logs execution history via ExecutionHistoryRepository.
"""

from typing import Optional, List, Dict

from app.schemas.agent import AgentRead
from app.schemas.task import TaskCreate
from app.schemas.execution_plan import ExecutionPlan
from app.schemas.execution_strategy import ExecutionStrategy
from app.schemas.execution import ExecutionResult
from app.schemas.agent_execution_context import AgentExecutionContext
from app.schemas.tool_call import ToolCall

from app.services.agent_service import AgentService
from app.services.tool_execution_engine import ToolExecutionEngine
from app.repositories.execution_history_repository import ExecutionHistoryRepository


class ExecutionRuntime:
    """
    Execution engine responsible for executing plans safely and consistently.

    Does NOT persist tasks, only executes and returns ExecutionResult.

    Logs all executions to ExecutionHistoryRepository.
    """

    def __init__(
        self,
        agent_service: AgentService,
        tool_engine: ToolExecutionEngine,
        history_repo: Optional[ExecutionHistoryRepository] = None,
    ):
        self._agent_service = agent_service
        self._tool_engine = tool_engine
        self._history_repo = history_repo

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
        Logs execution to history if repository is provided.
        """

        if plan.strategy == ExecutionStrategy.SINGLE_AGENT:
            result = self._execute_single_agent(agent, task, context)
        elif plan.strategy == ExecutionStrategy.MULTI_AGENT:
            result = self._execute_multi_agent(task, plan, context)
        else:
            raise ValueError(f"Unsupported strategy: {plan.strategy}")

        # Execute tools if any were collected
        if context.tool_calls:
            tool_results = self._tool_engine.execute_batch(
                tool_calls=context.tool_calls,
                context=context,
                fail_fast=True,
            )
            result.child_results = (result.child_results or []) + tool_results

        # Log execution to history
        if self._history_repo:
            self._log_execution(result, task, context, plan)

        return result

    # ==================================================
    # Private helpers
    # ==================================================

    def _log_execution(
        self,
        result: ExecutionResult,
        task: TaskCreate,
        context: AgentExecutionContext,
        plan: ExecutionPlan,
    ) -> None:
        """
        Save execution record to ExecutionHistoryRepository.
        """
        record = {
            "task_name": task.name,
            "execution_id": getattr(result, "execution_id", None),
            "status": getattr(result, "status", "UNKNOWN"),
            "metadata": {
                "task_id": getattr(task, "id", None),
                "run_id": context.run_id,
                "strategy": plan.strategy.value if plan.strategy else None,
            },
            "child_results_count": len(result.child_results or []),
        }
        self._history_repo.save(record)

    # ==================================================
    # Single agent execution
    # ==================================================

    def _execute_single_agent(
        self,
        agent: AgentRead,
        task: TaskCreate,
        context: AgentExecutionContext,
    ) -> ExecutionResult:

        raw_result = self._agent_service.execute(agent, task, context)

        # collect tool calls
        tool_calls = raw_result.get("tool_calls", [])
        for call in tool_calls:
            context.add_tool_call(ToolCall(**call))

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
            child_context = AgentExecutionContext(run_id=parent_context.run_id)
            intermediate_task = TaskCreate(
                name=task.name,
                description=task.description,
                input=task.input,
                status=task.status,
                priority=task.priority,
            )
            raw_result = self._agent_service.execute(agent, intermediate_task, child_context)

            # merge tool calls
            tool_calls = raw_result.get("tool_calls", [])
            for call in tool_calls:
                parent_context.add_tool_call(ToolCall(**call))

            child_results.append(ExecutionResult(**raw_result))

        return ExecutionResult(
            execution_id=f"multi-{task.name}",
            output=None,
            status="SUCCESS",
            child_results=child_results,
        )
