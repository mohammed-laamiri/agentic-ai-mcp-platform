"""
Orchestrator.

Coordinates high-level workflows without owning business logic.

Acts as the system conductor:
- Knows WHAT happens next
- Does NOT know HOW things are implemented
"""

from app.schemas.agent import AgentRead
from app.schemas.task import TaskCreate, TaskRead
from app.schemas.execution import ExecutionResult
from app.schemas.execution_plan import ExecutionPlan
from app.schemas.execution_strategy import ExecutionStrategy
from app.schemas.agent_execution_context import AgentExecutionContext
from app.schemas.execution_context import ExecutionContext
from app.schemas.tool_call import ToolCall

from app.services.agent_service import AgentService
from app.services.task_service import TaskService
from app.services.planner_agent import PlannerAgent
from app.services.tool_execution_engine import ToolExecutionEngine
from app.services.tool_registry import ToolRegistry
from app.services.memory_writer import MemoryWriter


class Orchestrator:
    """
    High-level workflow coordinator.
    """

    def __init__(
        self,
        task_service: TaskService,
        agent_service: AgentService,
        tool_registry: ToolRegistry,
        memory_writer: MemoryWriter,
        planner_agent: PlannerAgent | None = None,
    ) -> None:
        self._task_service = task_service
        self._agent_service = agent_service
        self._planner_agent = planner_agent or PlannerAgent()
        self._tool_engine = ToolExecutionEngine(tool_registry=tool_registry)
        self._memory_writer = memory_writer

    # ==================================================
    # Public API
    # ==================================================

    def run(self, agent: AgentRead, task_in: TaskCreate) -> TaskRead:
        """
        Run a task using orchestration and persist result.
        """
        agent_context = AgentExecutionContext()

        plan = self._plan(agent, task_in, agent_context)
        result = self._execute_plan(agent, task_in, plan, agent_context)

        return self._task_service.create(
            task_in=task_in,
            execution_result=result.dict(),
        )

    def execute(self, agent: AgentRead, task_in: TaskCreate) -> ExecutionResult:
        """
        Execute a task without persistence.
        """
        agent_context = AgentExecutionContext()

        plan = self._plan(agent, task_in, agent_context)
        return self._execute_plan(agent, task_in, plan, agent_context)

    # ==================================================
    # Planning
    # ==================================================

    def _plan(
        self,
        agent: AgentRead,
        task_in: TaskCreate,
        context: AgentExecutionContext,
    ) -> ExecutionPlan:
        return self._planner_agent.plan(
            agent=agent,
            task=task_in,
            context=context,
        )

    # ==================================================
    # Validation
    # ==================================================

    def _validate_plan(self, plan: ExecutionPlan) -> None:
        if plan.strategy == ExecutionStrategy.SINGLE_AGENT:
            if plan.steps:
                raise ValueError("SINGLE_AGENT must not define steps")

        elif plan.strategy == ExecutionStrategy.MULTI_AGENT:
            if not plan.steps or len(plan.steps) < 2:
                raise ValueError("MULTI_AGENT requires at least two agents")

        else:
            raise ValueError(f"Unknown strategy: {plan.strategy}")

    # ==================================================
    # Execution Dispatcher
    # ==================================================

    def _execute_plan(
        self,
        agent: AgentRead,
        task_in: TaskCreate,
        plan: ExecutionPlan,
        agent_context: AgentExecutionContext,
    ) -> ExecutionResult:
        self._validate_plan(plan)

        if plan.strategy == ExecutionStrategy.SINGLE_AGENT:
            result = self._execute_single_agent(agent, task_in, agent_context)

        elif plan.strategy == ExecutionStrategy.MULTI_AGENT:
            result = self._execute_multi_agent_sequential(task_in, plan, agent_context)

        else:
            raise ValueError(f"Unsupported strategy: {plan.strategy}")

        # Execute tool calls AFTER agent reasoning
        if agent_context.tool_calls:
            self._tool_engine.execute_batch(
                tool_calls=agent_context.tool_calls,
                context=agent_context,
                fail_fast=True,
            )

        # Persist execution memory
        session_context = ExecutionContext(
            task_id=getattr(task_in, "id", "unknown"),
            user_input=task_in.description,
        )

        self._memory_writer.write(
            execution_result=result,
            agent_context=agent_context,
            session_context=session_context,
        )

        return result

    # ==================================================
    # Execution Strategies
    # ==================================================

    def _execute_single_agent(
        self,
        agent: AgentRead,
        task_in: TaskCreate,
        context: AgentExecutionContext,
    ) -> ExecutionResult:
        raw_result = self._agent_service.execute(agent, task_in, context)

        for call in raw_result.get("tool_calls", []):
            context.tool_calls.append(ToolCall(**call))

        return ExecutionResult(**raw_result)

    def _execute_multi_agent_sequential(
        self,
        task_in: TaskCreate,
        plan: ExecutionPlan,
        context: AgentExecutionContext,
    ) -> ExecutionResult:
        current_input = task_in.description
        final_result: ExecutionResult | None = None

        for agent in plan.steps:
            intermediate_task = TaskCreate(
                description=current_input,
                input=current_input,
            )

            raw_result = self._agent_service.execute(
                agent,
                intermediate_task,
                context,
            )

            for call in raw_result.get("tool_calls", []):
                context.tool_calls.append(ToolCall(**call))

            final_result = ExecutionResult(**raw_result)
            current_input = final_result.output or ""

        if final_result is None:
            raise RuntimeError("Multi-agent execution produced no result")

        return final_result
