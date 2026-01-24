"""
Orchestrator service.

Coordinates high-level workflows without owning business logic.

Acts as the system "conductor":
- Knows WHAT happens next
- Does NOT know HOW things are implemented
"""

from app.schemas.agent import AgentRead
from app.schemas.task import TaskCreate, TaskRead
from app.schemas.execution import ExecutionResult
from app.schemas.execution_plan import ExecutionPlan
from app.schemas.agent_execution_context import AgentExecutionContext
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
        Initialize the orchestrator.

        Dependencies are injected to:
        - Enable testing
        - Preserve loose coupling
        - Allow future swaps (LangGraph planners, etc.)
        """
        self._task_service = task_service
        self._agent_service = agent_service
        self._planner_agent = planner_agent

    def run(self, agent: AgentRead, task_in: TaskCreate) -> TaskRead:
        """
        Run a task using an agent.

        Workflow:
        1. Create execution context
        2. Plan execution
        3. Execute plan
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
        # Step 2: Execution phase
        # ==================================================
        execution_result: ExecutionResult = self._execute(
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
            execution_result=execution_result.model_dump(),
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

        Delegates planning to the PlannerAgent.
        """
        return self._planner_agent.plan(
            agent=agent,
            task=task_in,
            context=context,
        )

    def _execute(
        self,
        agent: AgentRead,
        task_in: TaskCreate,
        plan: ExecutionPlan,
        context: AgentExecutionContext,
    ) -> ExecutionResult:
        """
        Execution phase.

        NOTE:
        - Plan is currently not interpreted
        - This is intentional and temporary
        """
        return self._agent_service.execute(
            agent=agent,
            task=task_in,
            context=context,
        )
