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
from app.schemas.tool_result import ToolResult

from app.services.agent_service import AgentService
from app.services.task_service import TaskService
from app.services.planner_agent import PlannerAgent
from app.services.v1.multi_agent import MultiAgentExecutor

from app.runtime.runtime import tool_execution_engine


class OrchestratorService:
    """
    High-level workflow coordinator.

    Responsibilities:
    - Request execution plan from PlannerAgent
    - Execute agents in correct order
    - Collect execution results
    - Execute tools safely
    - Persist results via TaskService (optional)
    - Maintain execution context
    """

    def __init__(
        self,
        task_service: TaskService,
        agent_service: AgentService,
        planner_agent: PlannerAgent,
    ) -> None:

        self._task_service = task_service
        self._agent_service = agent_service
        self._planner_agent = planner_agent

        # Multi-agent executor (your existing location)
        self._multi_agent_executor = MultiAgentExecutor(
            agent_service=self._agent_service
        )

    # ==================================================
    # Public API — Persisted execution
    # ==================================================

    def run(
        self,
        agent: AgentRead,
        task_in: TaskCreate,
    ) -> TaskRead:
        """
        Execute task and persist result.
        """

        context = AgentExecutionContext()

        try:

            plan = self._plan(
                agent=agent,
                task_in=task_in,
                context=context,
            )

            result = self._execute_plan(
                original_agent=agent,
                original_task=task_in,
                plan=plan,
                context=context,
            )

            context.mark_completed()

            return self._task_service.create(
                task_in=task_in,
                execution_result=result.dict(),
            )

        except Exception as exc:

            context.mark_failed(str(exc))
            raise

    # ==================================================
    # Public API — Non-persisted execution
    # ==================================================

    def execute(
        self,
        agent: AgentRead,
        task_in: TaskCreate,
    ) -> ExecutionResult:
        """
        Execute task without persistence.
        """

        context = AgentExecutionContext()

        try:

            plan = self._plan(
                agent=agent,
                task_in=task_in,
                context=context,
            )

            result = self._execute_plan(
                original_agent=agent,
                original_task=task_in,
                plan=plan,
                context=context,
            )

            context.mark_completed()

            return result

        except Exception as exc:

            context.mark_failed(str(exc))
            raise

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

    def _validate_plan(
        self,
        plan: ExecutionPlan,
    ) -> None:

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

            raise ValueError(
                f"Unknown execution strategy: {plan.strategy}"
            )

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

        elif plan.strategy == ExecutionStrategy.MULTI_AGENT:

            return self._execute_multi_agent(
                plan=plan,
                task_in=original_task,
                context=context,
            )

        raise ValueError(
            f"Unsupported execution strategy: {plan.strategy}"
        )

    # ==================================================
    # Single Agent Execution
    # ==================================================

    def _execute_single_agent(
        self,
        agent: AgentRead,
        task_in: TaskCreate,
        context: AgentExecutionContext,
    ) -> ExecutionResult:
        """
        Execute a single agent safely.
        """

        raw_result = self._agent_service.execute(
            agent=agent,
            task=task_in,
            context=context,
        )

        self._collect_tool_calls(
            raw_result=raw_result,
            context=context,
        )

        self._execute_tools(context)

        return ExecutionResult(**raw_result)

    # ==================================================
    # Multi-Agent Execution
    # ==================================================

    def _execute_multi_agent(
        self,
        plan: ExecutionPlan,
        task_in: TaskCreate,
        context: AgentExecutionContext,
    ) -> ExecutionResult:
        """
        Delegate to MultiAgentExecutor safely.
        """

        result = self._multi_agent_executor.execute(
            agents=plan.steps,
            task=task_in,
            context=context,
        )

        # Execute any tools collected during execution
        self._execute_tools(context)

        return result

    # ==================================================
    # Tool Call Collection
    # ==================================================

    def _collect_tool_calls(
        self,
        raw_result: dict,
        context: AgentExecutionContext,
    ) -> None:

        tool_calls = raw_result.get("tool_calls", [])

        if not tool_calls:
            return

        for call in tool_calls:

            if isinstance(call, ToolCall):

                context.add_tool_call(call)

            elif isinstance(call, dict):

                context.add_tool_call(
                    ToolCall(**call)
                )

    # ==================================================
    # Tool Execution
    # ==================================================

    def _execute_tools(
        self,
        context: AgentExecutionContext,
    ) -> None:
        """
        Execute all pending tool calls safely.
        """

        if not context.tool_calls:
            return

        for tool_call in context.tool_calls:

            result: ToolResult = tool_execution_engine.execute(
                tool_call
            )

            context.add_tool_result(result)

        # clear queue after execution
        context.tool_calls.clear()