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

    Responsibilities:
    - Request execution plan from PlannerAgent
    - Execute agents in correct order
    - Collect execution results
    - Persist results via TaskService (optional)
    - Maintain execution context
    """

    def __init__(
        self,
        task_service: TaskService,
        agent_service: AgentService,
        planner_agent: PlannerAgent,
    ) -> None:
        """
        Explicit dependency injection.

        Prevents hidden coupling and improves testability.
        """
        self._task_service = task_service
        self._agent_service = agent_service
        self._planner_agent = planner_agent

    # ==================================================
    # Public API
    # ==================================================

    def run(self, agent: AgentRead, task_in: TaskCreate) -> TaskRead:
        """
        Execute task and persist result.
        """
        context = AgentExecutionContext()

        plan = self._plan(agent, task_in, context)

        result = self._execute_plan(
            original_agent=agent,
            original_task=task_in,
            plan=plan,
            context=context,
        )

        return self._task_service.create(
            task_in=task_in,
            execution_result=result.dict(),
        )

    def execute(self, agent: AgentRead, task_in: TaskCreate) -> ExecutionResult:
        """
        Execute task without persistence.
        """
        context = AgentExecutionContext()

        plan = self._plan(agent, task_in, context)

        return self._execute_plan(
            original_agent=agent,
            original_task=task_in,
            plan=plan,
            context=context,
        )

    # ==================================================
    # Planning
    # ==================================================

    def _plan(
        self,
        agent: AgentRead,
        task_in: TaskCreate,
        context: AgentExecutionContext,
    ) -> ExecutionPlan:
        """
        Request execution plan from PlannerAgent.
        """
        return self._planner_agent.plan(
            agent=agent,
            task=task_in,
            context=context,
        )

    # ==================================================
    # Plan Validation
    # ==================================================

    def _validate_plan(self, plan: ExecutionPlan) -> None:
        """
        Ensures execution plan integrity.
        """

        if plan.strategy == ExecutionStrategy.SINGLE_AGENT:

            if not plan.steps or len(plan.steps) != 1:
                raise ValueError(
                    "SINGLE_AGENT execution requires exactly one agent step"
                )

        elif plan.strategy == ExecutionStrategy.MULTI_AGENT:

            if not plan.steps or len(plan.steps) < 2:
                raise ValueError(
                    "MULTI_AGENT execution requires at least two agent steps"
                )

        else:
            raise ValueError(f"Unknown execution strategy: {plan.strategy}")

    # ==================================================
    # Execution Dispatcher
    # ==================================================

    def _execute_plan(
        self,
        original_agent: AgentRead,
        original_task: TaskCreate,
        plan: ExecutionPlan,
        context: AgentExecutionContext,
    ) -> ExecutionResult:
        """
        Dispatch execution based on strategy.
        """

        self._validate_plan(plan)

        if plan.strategy == ExecutionStrategy.SINGLE_AGENT:

            return self._execute_single_agent(
                agent=plan.steps[0],
                task_in=original_task,
                context=context,
            )

        if plan.strategy == ExecutionStrategy.MULTI_AGENT:

            return self._execute_multi_agent_sequential(
                plan=plan,
                task_in=original_task,
                context=context,
            )

        raise ValueError(f"Unsupported execution strategy: {plan.strategy}")

    # ==================================================
    # Execution Strategies
    # ==================================================

    def _execute_single_agent(
        self,
        agent: AgentRead,
        task_in: TaskCreate,
        context: AgentExecutionContext,
    ) -> ExecutionResult:
        """
        Execute using one agent.
        """

        raw_result = self._agent_service.execute(
            agent=agent,
            task=task_in,
            context=context,
        )

        self._collect_tool_calls(raw_result, context)

        return ExecutionResult(**raw_result)

    def _execute_multi_agent_sequential(
        self,
        plan: ExecutionPlan,
        task_in: TaskCreate,
        context: AgentExecutionContext,
    ) -> ExecutionResult:
        """
        Execute agents sequentially.

        Output of each agent becomes input to next agent.
        """

        current_input = task_in.description or ""

        final_result: ExecutionResult | None = None

        for agent in plan.steps:

            intermediate_task = TaskCreate(
                description=current_input,
                input=current_input,
            )

            raw_result = self._agent_service.execute(
                agent=agent,
                task=intermediate_task,
                context=context,
            )

            self._collect_tool_calls(raw_result, context)

            final_result = ExecutionResult(**raw_result)

            # Pass output to next agent
            current_input = final_result.output or ""

        if final_result is None:
            raise RuntimeError("Multi-agent execution produced no result")

        return final_result

    # ==================================================
    # Tool Call Collection
    # ==================================================

    def _collect_tool_calls(
        self,
        raw_result: dict,
        context: AgentExecutionContext,
    ) -> None:
        """
        Collect declared tool calls into execution context.
        """

        tool_calls = raw_result.get("tool_calls", [])

        if not tool_calls:
            return

        for call in tool_calls:

            if isinstance(call, ToolCall):
                context.tool_calls.append(call)

            elif isinstance(call, dict):
                context.tool_calls.append(ToolCall(**call))