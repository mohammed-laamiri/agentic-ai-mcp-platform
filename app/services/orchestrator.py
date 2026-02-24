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

# NEW — safe import
from app.services.v1.multi_agent import MultiAgentExecutor

from app.runtime.runtime import tool_execution_engine


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
        self._task_service = task_service
        self._agent_service = agent_service
        self._planner_agent = planner_agent

        # NEW — initialize multi-agent executor safely
        self._multi_agent_executor = MultiAgentExecutor(
            agent_service=self._agent_service
        )

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
        Execute single agent.
        """
        raw_result = self._agent_service.execute(
            agent=agent,
            task=task_in,
            context=context,
        )

        self._collect_tool_calls(raw_result, context)
        self._execute_tools(context)

        return ExecutionResult(**raw_result)

    def _execute_multi_agent_sequential(
        self,
        plan: ExecutionPlan,
        task_in: TaskCreate,
        context: AgentExecutionContext,
    ) -> ExecutionResult:
        """
        SAFE delegation to MultiAgentExecutor.

        This keeps orchestrator clean and prevents duplication.
        """

        # Delegate execution
        result = self._multi_agent_executor.execute(
            agents=plan.steps,
            task=task_in,
            context=context,
        )

        # Tools may still need execution depending on agent output
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

        for call in tool_calls:

            if isinstance(call, ToolCall):
                context.add_tool_call(call)

            elif isinstance(call, dict):
                context.add_tool_call(ToolCall(**call))

    # ==================================================
    # Tool Execution
    # ==================================================

    def _execute_tools(
        self,
        context: AgentExecutionContext,
    ) -> None:
        """
        Execute all pending tool calls using singleton runtime engine.
        """

        for tool_call in context.tool_calls:

            result: ToolResult = tool_execution_engine.execute(tool_call)

            context.add_tool_result(result)

        # Clear executed calls
        context.tool_calls.clear()