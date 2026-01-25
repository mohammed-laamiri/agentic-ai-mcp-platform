"""
Orchestrator service.

Coordinates high-level workflows without owning business logic.

Acts as the system "conductor":
- Knows WHAT happens next
- Does NOT know HOW things are implemented
"""

from app.schemas.agent import AgentRead
from app.schemas.task import TaskCreate, TaskRead
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

    def run(self, agent: AgentRead, task_in: TaskCreate) -> TaskRead:
        """
        Run a task using an agent.

        Workflow:
        1. Create execution context
        2. Generate execution plan
        3. Interpret & execute plan
        4. Persist result
        """

        # ==================================================
        # Step 0: Execution context
        # ==================================================
        context = AgentExecutionContext()

        # ==================================================
        # Step 1: Planning phase
        # ==================================================
        plan: ExecutionPlan = self._plan(
            agent=agent,
            task_in=task_in,
            context=context,
        )

        # ==================================================
        # Step 2: Execution phase (plan interpretation)
        # ==================================================
        execution_result: dict = self._execute_plan(
            agent=agent,
            task_in=task_in,
            plan=plan,
            context=context,
        )

        # ==================================================
        # Step 3: Persistence phase
        # ==================================================
        return self._task_service.create(
            task_in=task_in,
            execution_result=execution_result,
        )

    # ============================================================
    # Internal orchestration steps
    # ============================================================

    def _plan(
        self,
        agent: AgentRead,
        task_in: TaskCreate,
        context: AgentExecutionContext,
    ) -> ExecutionPlan:
        """
        Planning phase.

        Delegates decision-making to the PlannerAgent.
        """
        return self._planner_agent.plan(
            agent=agent,
            task=task_in,
            context=context,
        )

    def _execute_plan(
        self,
        agent: AgentRead,
        task_in: TaskCreate,
        plan: ExecutionPlan,
        context: AgentExecutionContext,
    ) -> dict:
        """
        Interpret and execute an execution plan.

        Current behavior:
        - Supports exactly ONE strategy: SINGLE_AGENT
        - Any other strategy is intentionally rejected
        """

        if plan.strategy == ExecutionStrategy.SINGLE_AGENT:
            return self._execute_single_agent(
                agent=agent,
                task_in=task_in,
                context=context,
            )

        raise ValueError(f"Unsupported execution strategy: {plan.strategy}")

    def _execute_single_agent(
        self,
        agent: AgentRead,
        task_in: TaskCreate,
        context: AgentExecutionContext,
    ) -> dict:
        """
        Execute a task using a single agent.

        This is the ONLY execution path currently supported.
        """
        return self._agent_service.execute(
            agent=agent,
            task=task_in,
            context=context,
        )
