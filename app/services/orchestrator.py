"""
Async Orchestrator

Coordinates workflows:
- Plans tasks via PlannerAgent
- Executes tasks via ExecutionService
- Persists via TaskService
"""

import asyncio
from typing import AsyncGenerator, Optional, List
from uuid import uuid4

from app.schemas.agent import AgentRead
from app.schemas.task import TaskCreate, TaskRead
from app.schemas.execution import ExecutionResult
from app.schemas.execution_plan import ExecutionPlan
from app.schemas.execution_strategy import ExecutionStrategy
from app.schemas.agent_execution_context import AgentExecutionContext
from app.schemas.execution_event import ExecutionEvent, ExecutionEventType

from app.services.agent_service import AgentService
from app.services.task_service import TaskService
from app.services.planner_agent import PlannerAgent
from app.services.execution.execution_service import ExecutionService
from app.services.tool_registry import ToolRegistry
from app.services.memory_writer import MemoryWriter


class OrchestratorService:
    def __init__(
        self,
        task_service: TaskService,
        agent_service: AgentService,
        planner_agent: Optional[PlannerAgent] = None,
        execution_service: Optional[ExecutionService] = None,
        tool_registry: Optional[ToolRegistry] = None,
        memory_writer: Optional[MemoryWriter] = None,
    ) -> None:
        self._task_service = task_service
        self._agent_service = agent_service
        self._planner_agent = planner_agent or PlannerAgent()
        self._execution_service = execution_service or ExecutionService()
        self._tool_registry = tool_registry
        self._memory_writer = memory_writer

    # ==========================================================
    # Async methods (original API)
    # ==========================================================

    async def run(self, agent: AgentRead, task_in: TaskCreate) -> TaskRead:
        context = AgentExecutionContext()
        try:
            plan = await self._planner_agent.plan(agent, task_in, context)
            self._validate_plan(plan)

            # Execute plan
            execution_result: ExecutionResult = await self._execution_service.execute_plan(
                agent, task_in, plan=plan, context=context
            )

            context.mark_completed()

            # Persist task with execution output
            return self._task_service.create(
                task_in=task_in,
                execution_result=execution_result.output,
            )

        except Exception as exc:
            context.mark_failed(str(exc))
            raise

    async def execute(self, agent: AgentRead, task_in: TaskCreate) -> ExecutionResult:
        context = AgentExecutionContext()
        plan = await self._planner_agent.plan(agent, task_in, context)
        self._validate_plan(plan)
        return await self._execution_service.execute_plan(agent, task_in, plan=plan, context=context)

    async def stream_execute(self, agent: AgentRead, task_in: TaskCreate) -> AsyncGenerator[ExecutionEvent, None]:
        context = AgentExecutionContext()
        try:
            yield ExecutionEvent(type=ExecutionEventType.PLANNING_STARTED)
            plan = await self._planner_agent.plan(agent, task_in, context)
            yield ExecutionEvent(
                type=ExecutionEventType.PLAN_CREATED,
                strategy=plan.strategy.value,
                steps=[step.model_dump() for step in plan.steps],
            )
            self._validate_plan(plan)
            yield ExecutionEvent(type=ExecutionEventType.EXECUTION_STARTED)
            async for event in self._execution_service.stream_execute_plan(agent, task_in, plan, context):
                yield event
                if event.type == ExecutionEventType.EXECUTION_COMPLETED:
                    context.mark_completed()
                if event.type == ExecutionEventType.EXECUTION_FAILED:
                    context.mark_failed(event.error or "Unknown error")
            if context.status != "completed":
                context.mark_failed("Execution did not complete properly")
        except Exception as exc:
            context.mark_failed(str(exc))
            yield ExecutionEvent(type=ExecutionEventType.EXECUTION_FAILED, error=str(exc))
            raise

    # ==========================================================
    # Sync methods (backward compatibility)
    # ==========================================================

    def run_sync(self, agent: AgentRead, task_in: TaskCreate) -> TaskRead:
        """Synchronous wrapper for run()."""
        context = AgentExecutionContext()
        try:
            # Use sync planning
            plan = self._planner_agent.plan_sync(agent, task_in, context)
            self._validate_plan(plan)

            # Execute with sync method
            execution_result = self._execute_plan_sync(agent, task_in, plan, context)

            context.mark_completed()

            # Persist task
            return self._task_service.create(
                task_in=task_in,
                execution_result={"output": execution_result.output} if execution_result.output else None,
            )
        except Exception as exc:
            context.mark_failed(str(exc))
            raise

    def execute_sync(self, agent: AgentRead, task_in: TaskCreate) -> ExecutionResult:
        """Synchronous wrapper for execute()."""
        context = AgentExecutionContext()
        try:
            plan = self._planner_agent.plan_sync(agent, task_in, context)
            self._validate_plan(plan)
            result = self._execute_plan_sync(agent, task_in, plan, context)

            # Track tool calls in context if any
            if context.tool_calls:
                pass  # Tool calls already tracked

            return result
        except Exception as exc:
            context.mark_failed(str(exc))
            raise

    def _execute_plan_sync(
        self,
        agent: AgentRead,
        task_in: TaskCreate,
        plan: ExecutionPlan,
        context: AgentExecutionContext,
    ) -> ExecutionResult:
        """Execute plan synchronously."""
        execution_id = str(uuid4())
        child_results: List[ExecutionResult] = []

        if plan.strategy == ExecutionStrategy.SINGLE_AGENT:
            # Single agent execution - use the provided agent directly
            result = self._agent_service.execute_sync(agent, task_in, context)
            if isinstance(result, dict):
                return ExecutionResult(
                    execution_id=execution_id,
                    status="SUCCESS",
                    output=result.get("output"),
                    error=result.get("error"),
                )
            elif isinstance(result, ExecutionResult):
                result.execution_id = execution_id
                return result
            else:
                return ExecutionResult(
                    execution_id=execution_id,
                    status="SUCCESS",
                    output=str(result),
                )

        elif plan.strategy == ExecutionStrategy.MULTI_AGENT:
            # Multi-agent execution
            current_output = None
            for step in plan.steps:
                step_agent = AgentRead(id=step.id, name=step.name)
                step_result = self._agent_service.execute_sync(step_agent, task_in, context)

                if isinstance(step_result, dict):
                    step_result = ExecutionResult(
                        execution_id=str(uuid4()),
                        status="SUCCESS",
                        output=step_result.get("output"),
                    )
                elif not isinstance(step_result, ExecutionResult):
                    step_result = ExecutionResult(
                        execution_id=str(uuid4()),
                        status="SUCCESS",
                        output=str(step_result),
                    )

                child_results.append(step_result)
                current_output = step_result.output

            return ExecutionResult(
                execution_id=execution_id,
                status="SUCCESS",
                output=current_output,
                child_results=child_results,
            )

        else:
            return ExecutionResult(
                execution_id=execution_id,
                status="ERROR",
                error=f"Unknown strategy: {plan.strategy}",
            )

    # ==========================================================
    # Validation
    # ==========================================================

    def _validate_plan(self, plan: ExecutionPlan) -> None:
        if plan.strategy == ExecutionStrategy.SINGLE_AGENT and plan.steps and len(plan.steps) != 1:
            raise ValueError("SINGLE_AGENT requires exactly one agent step")
        if plan.strategy == ExecutionStrategy.MULTI_AGENT and (not plan.steps or len(plan.steps) < 2):
            raise ValueError("MULTI_AGENT requires at least two agent steps")
