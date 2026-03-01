"""
Async Orchestrator Service

Coordinates high-level workflows in an async manner.

Responsibilities:
- Request execution plan from PlannerAgent
- Validate execution plan
- Delegate execution to async ExecutionService
- Maintain execution context lifecycle
- Persist results via TaskService (optional)
- Supports future async RAG and multi-agent orchestration
- Supports streaming execution (Phase 3)
"""

from typing import AsyncGenerator

from app.schemas.agent import AgentRead
from app.schemas.task import TaskCreate, TaskRead
from app.schemas.execution import ExecutionResult
from app.schemas.execution_plan import ExecutionPlan
from app.schemas.execution_strategy import ExecutionStrategy
from app.schemas.agent_execution_context import AgentExecutionContext
from app.schemas.execution_event import (
    ExecutionEvent,
    ExecutionEventType,
)

from app.services.agent_service import AgentService
from app.services.task_service import TaskService
from app.services.planner_agent import PlannerAgent
from app.services.execution.execution_service import ExecutionService


class OrchestratorService:
    """
    Async high-level workflow coordinator.
    """

    def __init__(
        self,
        task_service: TaskService,
        agent_service: AgentService,
        planner_agent: PlannerAgent,
        execution_service: ExecutionService,
    ) -> None:
        self._task_service = task_service
        self._agent_service = agent_service
        self._planner_agent = planner_agent
        self._execution_service = execution_service

    # ==========================================================
    # Persisted async execution
    # ==========================================================

    async def run(self, agent: AgentRead, task_in: TaskCreate) -> TaskRead:
        """
        Execute a task asynchronously and persist the result.
        """
        context = AgentExecutionContext()

        try:
            plan = await self._planner_agent.plan(
                agent=agent,
                task=task_in,
                context=context,
            )

            self._validate_plan(plan)

            result = await self._execution_service.execute_plan(
                agent=agent,
                task=task_in,
                plan=plan,
                context=context,
            )

            context.mark_completed()

            return self._task_service.create(
                task_in=task_in,
                execution_result=result.model_dump(),
            )

        except Exception as exc:
            context.mark_failed(str(exc))
            raise

    # ==========================================================
    # Non-persisted async execution
    # ==========================================================

    async def execute(self, agent: AgentRead, task_in: TaskCreate) -> ExecutionResult:
        """
        Execute a task asynchronously without persisting results.
        """
        context = AgentExecutionContext()

        try:
            plan = await self._planner_agent.plan(
                agent=agent,
                task=task_in,
                context=context,
            )

            self._validate_plan(plan)

            result = await self._execution_service.execute_plan(
                agent=agent,
                task=task_in,
                plan=plan,
                context=context,
            )

            context.mark_completed()

            return result

        except Exception as exc:
            context.mark_failed(str(exc))
            raise

    # ==========================================================
    # Streaming async execution (Typed + Fully Integrated)
    # ==========================================================

    async def stream_execute(
        self,
        agent: AgentRead,
        task_in: TaskCreate,
    ) -> AsyncGenerator[ExecutionEvent, None]:
        """
        Stream structured execution events.

        Emits strongly-typed ExecutionEvent objects.
        API layer handles SSE formatting.
        """

        context = AgentExecutionContext()

        try:
            # 🔹 Planning started
            yield ExecutionEvent(
                type=ExecutionEventType.PLANNING_STARTED
            )

            plan = await self._planner_agent.plan(
                agent=agent,
                task=task_in,
                context=context,
            )

            yield ExecutionEvent(
                type=ExecutionEventType.PLAN_CREATED,
                strategy=plan.strategy.value,
                steps=[step.model_dump() for step in plan.steps],
            )

            # 🔹 Validate plan
            self._validate_plan(plan)

            yield ExecutionEvent(
                type=ExecutionEventType.EXECUTION_STARTED
            )

            # 🔹 Forward execution service streaming events
            async for event in self._execution_service.stream_execute_plan(
                agent=agent,
                task=task_in,
                plan=plan,
                context=context,
            ):
                yield event

                if event.type == ExecutionEventType.EXECUTION_COMPLETED:
                    context.mark_completed()

                if event.type == ExecutionEventType.EXECUTION_FAILED:
                    context.mark_failed(event.error)

            # Safety guard
            if not context.completed:
                context.mark_failed("Execution did not complete properly")

        except Exception as exc:
            context.mark_failed(str(exc))

            yield ExecutionEvent(
                type=ExecutionEventType.EXECUTION_FAILED,
                error=str(exc),
            )

            raise

    # ==========================================================
    # Plan validation
    # ==========================================================

    def _validate_plan(self, plan: ExecutionPlan) -> None:
        """
        Validate the execution plan before dispatching.
        """
        if plan.strategy == ExecutionStrategy.SINGLE_AGENT:
            if not plan.steps or len(plan.steps) != 1:
                raise ValueError("SINGLE_AGENT requires exactly one agent step")

        elif plan.strategy == ExecutionStrategy.MULTI_AGENT:
            if not plan.steps or len(plan.steps) < 2:
                raise ValueError("MULTI_AGENT requires at least two agent steps")

        else:
            raise ValueError(f"Unknown execution strategy: {plan.strategy}")