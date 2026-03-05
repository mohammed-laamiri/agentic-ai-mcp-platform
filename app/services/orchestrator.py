"""
Async Orchestrator

Coordinates workflows:
- Plans tasks via PlannerAgent
- Executes tasks via ExecutionService
- Persists via TaskService
"""

from typing import AsyncGenerator

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


class OrchestratorService:
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

            # Persist task with execution output (directly assign, no .get())
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
                    context.mark_failed(event.error)
            if not context.completed:
                context.mark_failed("Execution did not complete properly")
        except Exception as exc:
            context.mark_failed(str(exc))
            yield ExecutionEvent(type=ExecutionEventType.EXECUTION_FAILED, error=str(exc))
            raise

    def _validate_plan(self, plan: ExecutionPlan) -> None:
        if plan.strategy == ExecutionStrategy.SINGLE_AGENT and (not plan.steps or len(plan.steps) != 1):
            raise ValueError("SINGLE_AGENT requires exactly one agent step")
        if plan.strategy == ExecutionStrategy.MULTI_AGENT and (not plan.steps or len(plan.steps) < 2):
            raise ValueError("MULTI_AGENT requires at least two agent steps")