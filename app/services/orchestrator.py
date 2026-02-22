"""
Orchestrator Service.

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
from app.schemas.tool_call import ToolCall

from app.services.agent_service import AgentService
from app.services.task_service import TaskService
from app.services.planner_agent import PlannerAgent


class OrchestratorService:
    """
    High-level workflow coordinator.
    """

    def __init__(
        self,
        task_service: TaskService,
        agent_service: AgentService,
        planner_agent: PlannerAgent,
    ) -> None:
        """
        Orchestrator requires a fully configured PlannerAgent.

        This prevents hidden dependencies and keeps architecture explicit.
        """
        self._task_service = task_service
        self._agent_service = agent_service
        self._planner_agent = planner_agent

    # ==================================================
    # Public API
    # ==================================================

    def run(self, agent: AgentRead, task_in: TaskCreate) -> TaskRead:
        """
        Run a task using orchestration and persist result.
        """
        context = AgentExecutionContext()

        plan = self._plan(agent, task_in, context)
        result = self._execute_plan(agent, task_in, plan, context)

        return self._task_service.create(
            task_in=task_in,
            execution_result=result.dict(),
        )

    def execute(self, agent: AgentRead, task_in: TaskCreate) -> ExecutionResult:
        """
        Execute a task without persistence.
        """
        context = AgentExecutionContext()

        plan = self._plan(agent, task_in, context)
        return self._execute_plan(agent, task_in, plan, context)

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
        context: AgentExecutionContext,
    ) -> ExecutionResult:
        self._validate_plan(plan)

        if plan.strategy == ExecutionStrategy.SINGLE_AGENT:
            return self._execute_single_agent(agent, task_in, context)

        if plan.strategy == ExecutionStrategy.MULTI_AGENT:
            return self._execute_multi_agent_sequential(task_in, plan, context)

        raise ValueError(f"Unsupported strategy: {plan.strategy}")

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

        tool_calls = raw_result.get("tool_calls", [])
        context.tool_calls.extend(ToolCall(**call) for call in tool_calls)

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

            tool_calls = raw_result.get("tool_calls", [])
            context.tool_calls.extend(ToolCall(**call) for call in tool_calls)

            final_result = ExecutionResult(**raw_result)
            current_input = final_result.output or ""

        if final_result is None:
            raise RuntimeError("Multi-agent execution produced no result")

        return final_result