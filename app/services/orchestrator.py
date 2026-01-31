"""
app/services/orchestrator.py

Coordinates high-level workflows without owning business logic.

Acts as the system "conductor":
- Knows WHAT happens next
- Does NOT know HOW things are implemented
"""

from app.schemas.agent import AgentRead
from app.schemas.task import TaskCreate, TaskRead
from app.schemas.execution import ExecutionResult
from app.schemas.execution_plan import ExecutionPlan
from app.schemas.execution_strategy import ExecutionStrategy
from app.schemas.agent_execution_context import AgentExecutionContext
from app.services.agent_service import AgentService
from app.services.task_service import TaskService
from app.services.planner_agent import PlannerAgent


class OrchestratorService:
    """
    High-level workflow coordinator.

    Architectural role:
    - Interpret execution plans
    - Delegate execution
    - Preserve domain boundaries
    """

    def __init__(
        self,
        task_service: TaskService,
        agent_service: AgentService,
        planner_agent: PlannerAgent | None = None,
    ) -> None:
        """
        Initialize the orchestrator with injected dependencies.
        """
        self._task_service = task_service
        self._agent_service = agent_service
        self._planner_agent = planner_agent or PlannerAgent()

    # ==================================================
    # Public API
    # ==================================================

    def run(self, agent: AgentRead, task_in: TaskCreate) -> TaskRead:
        """
        Run a task using orchestration and persist the result.
        """

        context = AgentExecutionContext()

        plan = self._plan(
            agent=agent,
            task_in=task_in,
            context=context,
        )

        execution_result = self._execute_plan(
            agent=agent,
            task_in=task_in,
            plan=plan,
            context=context,
        )

        return self._task_service.create(
            task_in=task_in,
            execution_result=execution_result.dict(),
        )

    def execute(self, agent: AgentRead, task_in: TaskCreate) -> ExecutionResult:
        """
        Execute a task WITHOUT persistence.

        Used by /agent/execute endpoint.
        """
        context = AgentExecutionContext()

        plan = self._plan(
            agent=agent,
            task_in=task_in,
            context=context,
        )

        return self._execute_plan(
            agent=agent,
            task_in=task_in,
            plan=plan,
            context=context,
        )

    # ==================================================
    # Internal orchestration steps
    # ==================================================

    def _plan(
        self,
        agent: AgentRead,
        task_in: TaskCreate,
        context: AgentExecutionContext,
    ) -> ExecutionPlan:
        """
        Planning phase.
        """
        return self._planner_agent.plan(
            agent=agent,
            task=task_in,
            context=context,
        )

    # ==================================================
    # Execution plan validation
    # ==================================================

    def _validate_plan(self, plan: ExecutionPlan) -> None:
        """
        Validate execution plan before execution.

        Acts as a safety barrier between planning and execution.
        """
        if plan.strategy == ExecutionStrategy.SINGLE_AGENT:
            if plan.steps:
                raise ValueError(
                    "SINGLE_AGENT strategy must not include execution steps"
                )

        elif plan.strategy == ExecutionStrategy.MULTI_AGENT:
            if not plan.steps:
                raise ValueError(
                    "MULTI_AGENT strategy requires at least one execution step"
                )
            if len(plan.steps) < 2:
                raise ValueError(
                    "MULTI_AGENT strategy requires at least two agents"
                )
        else:
            raise ValueError(f"Unknown execution strategy: {plan.strategy}")

    # ==================================================
    # Execution strategies
    # ==================================================

    def _execute_plan(
        self,
        agent: AgentRead,
        task_in: TaskCreate,
        plan: ExecutionPlan,
        context: AgentExecutionContext,
    ) -> ExecutionResult:
        """
        Interpret and execute an execution plan.
        """

        # Validate plan before execution
        self._validate_plan(plan)

        if plan.strategy == ExecutionStrategy.SINGLE_AGENT:
            return self._execute_single_agent(
                agent=agent,
                task_in=task_in,
                context=context,
            )

        if plan.strategy == ExecutionStrategy.MULTI_AGENT:
            return self._execute_multi_agent_sequential(
                task_in=task_in,
                plan=plan,
                context=context,
            )

        raise ValueError(f"Unsupported execution strategy: {plan.strategy}")

    def _execute_single_agent(
        self,
        agent: AgentRead,
        task_in: TaskCreate,
        context: AgentExecutionContext,
    ) -> ExecutionResult:
        """
        Execute a task using a single agent.
        """
        result = self._agent_service.execute(
            agent=agent,
            task=task_in,
            context=context,
        )

        return ExecutionResult(**result)

    def _execute_multi_agent_sequential(
        self,
        task_in: TaskCreate,
        plan: ExecutionPlan,
        context: AgentExecutionContext,
    ) -> ExecutionResult:
        """
        Execute multiple agents sequentially.

        Rules:
        - Agents are executed in order
        - Output of previous agent becomes input of next agent
        """

        current_input = task_in.description
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
