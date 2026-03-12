# app/services/orchestrator.py

"""
Async Orchestrator Service.

Coordinates high-level workflows for task execution without owning business logic.

Acts as the system conductor:
- Knows WHAT happens next (planning)
- Delegates HOW things are executed (agent & tool execution)
- Integrates MCP-compliant tool execution
- Persists results using TaskService & MemoryWriter

Supports:
- Async execution for non-blocking operations
- Streaming execution events for real-time monitoring
- Backward-compatible sync methods
"""

from typing import Optional, List, AsyncGenerator

from app.schemas.agent import AgentRead
from app.schemas.task import TaskCreate, TaskRead
from app.schemas.execution import ExecutionResult
from app.schemas.execution_plan import ExecutionPlan
from app.schemas.execution_strategy import ExecutionStrategy
from app.schemas.agent_execution_context import AgentExecutionContext
from app.schemas.tool_call import ToolCall
from app.schemas.context import ExecutionContext
from app.schemas.execution_event import ExecutionEvent, ExecutionEventType

from app.services.agent_service import AgentService
from app.services.task_service import TaskService
from app.services.planner_agent import PlannerAgent
from app.services.tool_execution_engine import ToolExecutionEngine
from app.services.tool_registry import ToolRegistry
from app.services.memory_writer import MemoryWriter


class OrchestratorService:
    """
    High-level workflow coordinator.

    Responsibilities:
    - Run tasks via agents
    - Apply single or multi-agent strategies
    - Trigger MCP tool executions
    - Persist execution results via TaskService & MemoryWriter

    Provides both async and sync interfaces.
    """

    def __init__(
        self,
        task_service: TaskService,
        agent_service: AgentService,
        tool_registry: ToolRegistry,
        memory_writer: MemoryWriter,
        planner_agent: Optional[PlannerAgent] = None,
    ) -> None:
        self._task_service = task_service
        self._agent_service = agent_service
        self._planner_agent = planner_agent or PlannerAgent()
        self._tool_engine = ToolExecutionEngine(tool_registry=tool_registry)
        self._memory_writer = memory_writer
        self._tool_registry = tool_registry

    # ==================================================
    # Async Public API
    # ==================================================

    async def run(self, agent: AgentRead, task_in: TaskCreate) -> TaskRead:
        """
        Execute a task and persist result via TaskService (async).
        """
        context = AgentExecutionContext()
        try:
            plan = await self._plan(agent, task_in, context)
            result = await self._execute_plan(agent, task_in, plan, context)

            context.mark_completed()

            # Create task and complete it with execution result
            task_read = self._task_service.create_task(task_in)
            return self._task_service.complete_task(
                task_id=task_read.id,
                result=result.model_dump() if hasattr(result, 'model_dump') else result.dict(),
            )

        except Exception as exc:
            context.mark_failed(str(exc))
            raise

    async def execute(self, agent: AgentRead, task_in: TaskCreate) -> ExecutionResult:
        """
        Execute a task without persistence (async).
        Returns raw ExecutionResult for testing or transient executions.
        """
        context = AgentExecutionContext()
        plan = await self._plan(agent, task_in, context)
        return await self._execute_plan(agent, task_in, plan, context)

    async def stream_execute(
        self, agent: AgentRead, task_in: TaskCreate
    ) -> AsyncGenerator[ExecutionEvent, None]:
        """
        Stream execution events for real-time monitoring.

        Yields ExecutionEvent objects as execution progresses.
        """
        context = AgentExecutionContext()
        try:
            # Planning phase
            yield ExecutionEvent(type=ExecutionEventType.PLANNING_STARTED)

            plan = await self._plan(agent, task_in, context)

            yield ExecutionEvent(
                type=ExecutionEventType.PLAN_CREATED,
                strategy=plan.strategy.value,
                steps=[step.model_dump() for step in plan.steps] if plan.steps else [],
            )

            self._validate_plan(plan)

            # Execution phase
            yield ExecutionEvent(type=ExecutionEventType.EXECUTION_STARTED)

            # Execute based on strategy
            if plan.strategy == ExecutionStrategy.SINGLE_AGENT:
                yield ExecutionEvent(
                    type=ExecutionEventType.AGENT_STARTED,
                    agent_id=agent.id,
                    agent_name=agent.name,
                )

                result = await self._execute_single_agent(agent, task_in, context)

                yield ExecutionEvent(
                    type=ExecutionEventType.AGENT_COMPLETED,
                    agent_id=agent.id,
                    output=result.output,
                )

            elif plan.strategy == ExecutionStrategy.MULTI_AGENT:
                result = await self._execute_multi_agent_with_events(
                    task_in, plan, context
                )
                # Events are yielded inside the method
                for event in result.get("events", []):
                    yield event
                result = result["result"]
            else:
                raise ValueError(f"Unsupported strategy: {plan.strategy}")

            # Tool execution phase
            if context.tool_calls:
                for call in context.tool_calls:
                    yield ExecutionEvent(
                        type=ExecutionEventType.TOOL_STARTED,
                        tool_id=call.tool_id,
                    )

                tool_results = self._tool_engine.execute_batch(
                    tool_calls=context.tool_calls,
                    context=context,
                    fail_fast=True,
                )
                result.child_results = (result.child_results or []) + tool_results

                for tr in tool_results:
                    yield ExecutionEvent(
                        type=ExecutionEventType.TOOL_COMPLETED,
                        tool_id=tr.tool_id,
                        output=tr.output,
                        error=tr.error,
                    )

            # Persist and complete
            self._persist_execution(result, plan, context)
            context.mark_completed()

            yield ExecutionEvent(
                type=ExecutionEventType.EXECUTION_COMPLETED,
                output=result.output,
            )

        except Exception as exc:
            context.mark_failed(str(exc))
            yield ExecutionEvent(
                type=ExecutionEventType.EXECUTION_FAILED,
                error=str(exc),
            )
            raise

    # ==================================================
    # Sync Public API (backward compatibility)
    # ==================================================

    def run_sync(self, agent: AgentRead, task_in: TaskCreate) -> TaskRead:
        """
        Synchronous version of run() for backward compatibility.
        """
        context = AgentExecutionContext()
        plan = self._planner_agent.plan_sync(agent, task_in, context)
        result = self._execute_plan_sync(agent, task_in, plan, context)

        task_read = self._task_service.create_task(task_in)
        return self._task_service.complete_task(
            task_id=task_read.id,
            result=result.model_dump() if hasattr(result, 'model_dump') else result.dict(),
        )

    def execute_sync(self, agent: AgentRead, task_in: TaskCreate) -> ExecutionResult:
        """
        Synchronous version of execute() for backward compatibility.
        """
        context = AgentExecutionContext()
        plan = self._planner_agent.plan_sync(agent, task_in, context)
        return self._execute_plan_sync(agent, task_in, plan, context)

    # ==================================================
    # Planning
    # ==================================================

    async def _plan(
        self,
        agent: AgentRead,
        task_in: TaskCreate,
        context: AgentExecutionContext,
    ) -> ExecutionPlan:
        """
        Generate an execution plan using PlannerAgent (async).
        """
        return await self._planner_agent.plan(
            agent=agent,
            task=task_in,
            context=context,
        )

    # ==================================================
    # Plan Validation
    # ==================================================

    def _validate_plan(self, plan: ExecutionPlan) -> None:
        """
        Validates execution plan structure.
        Ensures strategy consistency and step requirements.
        """
        if plan.strategy == ExecutionStrategy.SINGLE_AGENT:
            if plan.steps:
                raise ValueError("SINGLE_AGENT must not define steps")
        elif plan.strategy == ExecutionStrategy.MULTI_AGENT:
            if not plan.steps or len(plan.steps) < 2:
                raise ValueError("MULTI_AGENT requires at least two agents")
        else:
            raise ValueError(f"Unknown strategy: {plan.strategy}")

    # ==================================================
    # Async Execution Dispatcher
    # ==================================================

    async def _execute_plan(
        self,
        agent: AgentRead,
        task_in: TaskCreate,
        plan: ExecutionPlan,
        context: AgentExecutionContext,
    ) -> ExecutionResult:
        """
        Dispatch task execution according to strategy (async).
        """
        self._validate_plan(plan)

        try:
            # Agent execution phase
            if plan.strategy == ExecutionStrategy.SINGLE_AGENT:
                result = await self._execute_single_agent(agent, task_in, context)
            elif plan.strategy == ExecutionStrategy.MULTI_AGENT:
                result = await self._execute_multi_agent_branching(task_in, plan, context)
            else:
                raise ValueError(f"Unsupported strategy: {plan.strategy}")

            # Tool execution phase (MCP)
            tool_results: List[ExecutionResult] = []
            if context.tool_calls:
                tool_results = self._tool_engine.execute_batch(
                    tool_calls=context.tool_calls,
                    context=context,
                    fail_fast=True,
                )
            result.child_results = (result.child_results or []) + tool_results

            # Persist execution
            self._persist_execution(result, plan, context)

            context.mark_completed("completed")
            return result

        except Exception as exc:
            context.mark_completed("failed")
            raise exc

    # ==================================================
    # Sync Execution Dispatcher (backward compatibility)
    # ==================================================

    def _execute_plan_sync(
        self,
        agent: AgentRead,
        task_in: TaskCreate,
        plan: ExecutionPlan,
        context: AgentExecutionContext,
    ) -> ExecutionResult:
        """
        Synchronous execution dispatcher for backward compatibility.
        """
        self._validate_plan(plan)

        try:
            if plan.strategy == ExecutionStrategy.SINGLE_AGENT:
                result = self._execute_single_agent_sync(agent, task_in, context)
            elif plan.strategy == ExecutionStrategy.MULTI_AGENT:
                result = self._execute_multi_agent_branching_sync(task_in, plan, context)
            else:
                raise ValueError(f"Unsupported strategy: {plan.strategy}")

            # Tool execution phase
            tool_results: List[ExecutionResult] = []
            if context.tool_calls:
                tool_results = self._tool_engine.execute_batch(
                    tool_calls=context.tool_calls,
                    context=context,
                    fail_fast=True,
                )
            result.child_results = (result.child_results or []) + tool_results

            self._persist_execution(result, plan, context)
            context.mark_completed("completed")
            return result

        except Exception as exc:
            context.mark_completed("failed")
            raise exc

    # ==================================================
    # Persistence Helper
    # ==================================================

    def _persist_execution(
        self,
        result: ExecutionResult,
        plan: ExecutionPlan,
        context: AgentExecutionContext,
    ) -> None:
        """Persist execution result to MemoryWriter."""
        exec_context = ExecutionContext(
            session_id="session-placeholder",
            user_id=None,
            strategy=plan.strategy.value if hasattr(plan.strategy, 'value') else str(plan.strategy),
            metadata={
                "run_id": context.run_id,
                "status": context.status,
            },
            tool_registry=None,
        )

        self._memory_writer.write(
            execution_result=result,
            agent_context=context,
            session_context=exec_context,
        )

    # ==================================================
    # Async Execution Strategies
    # ==================================================

    async def _execute_single_agent(
        self,
        agent: AgentRead,
        task_in: TaskCreate,
        context: AgentExecutionContext,
    ) -> ExecutionResult:
        """Execute a single agent task (async)."""
        # AgentService.execute is sync for now, but wrapped for async interface
        raw_result = self._agent_service.execute(agent, task_in, context)

        tool_calls = raw_result.get("tool_calls", [])
        for call in tool_calls:
            context.add_tool_call(ToolCall(**call))

        return ExecutionResult(**raw_result)

    async def _execute_multi_agent_branching(
        self,
        task_in: TaskCreate,
        plan: ExecutionPlan,
        parent_context: AgentExecutionContext,
    ) -> ExecutionResult:
        """Execute multiple agents in branching style (async)."""
        child_results: List[ExecutionResult] = []
        for agent in plan.steps:
            context = AgentExecutionContext(run_id=parent_context.run_id)
            intermediate_task = TaskCreate(
                name=task_in.name or "intermediate",
                description=task_in.description,
                input={"description": task_in.description} if task_in.description else {},
            )

            raw_result = self._agent_service.execute(agent, intermediate_task, context)

            tool_calls = raw_result.get("tool_calls", [])
            for call in tool_calls:
                parent_context.add_tool_call(ToolCall(**call))

            child_results.append(ExecutionResult(**raw_result))

        return ExecutionResult(
            execution_id="aggregated-" + (task_in.description or "task"),
            output=None,
            status="SUCCESS",
            child_results=child_results,
        )

    async def _execute_multi_agent_with_events(
        self,
        task_in: TaskCreate,
        plan: ExecutionPlan,
        parent_context: AgentExecutionContext,
    ) -> dict:
        """Execute multi-agent with event collection for streaming."""
        child_results: List[ExecutionResult] = []
        events: List[ExecutionEvent] = []

        for agent in plan.steps:
            events.append(ExecutionEvent(
                type=ExecutionEventType.AGENT_STARTED,
                agent_id=agent.id,
                agent_name=agent.name,
            ))

            context = AgentExecutionContext(run_id=parent_context.run_id)
            intermediate_task = TaskCreate(
                name=task_in.name or "intermediate",
                description=task_in.description,
                input={"description": task_in.description} if task_in.description else {},
            )

            raw_result = self._agent_service.execute(agent, intermediate_task, context)

            tool_calls = raw_result.get("tool_calls", [])
            for call in tool_calls:
                parent_context.add_tool_call(ToolCall(**call))

            result = ExecutionResult(**raw_result)
            child_results.append(result)

            events.append(ExecutionEvent(
                type=ExecutionEventType.AGENT_COMPLETED,
                agent_id=agent.id,
                output=result.output,
            ))

        aggregated = ExecutionResult(
            execution_id="aggregated-" + (task_in.description or "task"),
            output=None,
            status="SUCCESS",
            child_results=child_results,
        )

        return {"result": aggregated, "events": events}

    # ==================================================
    # Sync Execution Strategies (backward compatibility)
    # ==================================================

    def _execute_single_agent_sync(
        self,
        agent: AgentRead,
        task_in: TaskCreate,
        context: AgentExecutionContext,
    ) -> ExecutionResult:
        """Execute a single agent task (sync)."""
        raw_result = self._agent_service.execute(agent, task_in, context)

        tool_calls = raw_result.get("tool_calls", [])
        for call in tool_calls:
            context.add_tool_call(ToolCall(**call))

        return ExecutionResult(**raw_result)

    def _execute_multi_agent_branching_sync(
        self,
        task_in: TaskCreate,
        plan: ExecutionPlan,
        parent_context: AgentExecutionContext,
    ) -> ExecutionResult:
        """Execute multiple agents in branching style (sync)."""
        child_results: List[ExecutionResult] = []
        for agent in plan.steps:
            context = AgentExecutionContext(run_id=parent_context.run_id)
            intermediate_task = TaskCreate(
                name=task_in.name or "intermediate",
                description=task_in.description,
                input={"description": task_in.description} if task_in.description else {},
            )

            raw_result = self._agent_service.execute(agent, intermediate_task, context)

            tool_calls = raw_result.get("tool_calls", [])
            for call in tool_calls:
                parent_context.add_tool_call(ToolCall(**call))

            child_results.append(ExecutionResult(**raw_result))

        return ExecutionResult(
            execution_id="aggregated-" + (task_in.description or "task"),
            output=None,
            status="SUCCESS",
            child_results=child_results,
        )
