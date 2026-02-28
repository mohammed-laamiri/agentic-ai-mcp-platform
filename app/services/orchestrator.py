"""
Orchestrator Service

Coordinates high-level workflows.

Responsibilities:
- Request execution plan from PlannerAgent
- Validate execution plan
- Delegate execution to ExecutionService
- Maintain execution context lifecycle
- Persist results via TaskService (optional)
- Future extension: RAG integration, multi-agent orchestration
"""

from typing import Optional

from app.schemas.agent import AgentRead
from app.schemas.task import TaskCreate, TaskRead
from app.schemas.execution import ExecutionResult
from app.schemas.execution_plan import ExecutionPlan
from app.schemas.execution_strategy import ExecutionStrategy
from app.schemas.agent_execution_context import AgentExecutionContext

from app.services.agent_service import AgentService
from app.services.task_service import TaskService
from app.services.planner_agent import PlannerAgent
from app.services.execution.execution_service import ExecutionService


class OrchestratorService:
    """
    High-level workflow coordinator.

    Responsibilities:
    - Request execution plan from PlannerAgent
    - Validate execution plan
    - Delegate execution to ExecutionService
    - Maintain execution context lifecycle
    - Persist results via TaskService (optional)

    Does NOT:
    - Execute agents directly
    - Execute tools directly
    """

    def __init__(
        self,
        task_service: TaskService,
        agent_service: AgentService,
        planner_agent: PlannerAgent,
        execution_service: ExecutionService,
    ) -> None:
        """
        Initialize OrchestratorService.

        Parameters
        ----------
        task_service : TaskService
            Service to persist tasks and results
        agent_service : AgentService
            Service to execute individual agent logic
        planner_agent : PlannerAgent
            Service to generate execution plans
        execution_service : ExecutionService
            Service to execute plans (single or multi-agent)
        """
        self._task_service = task_service
        self._agent_service = agent_service
        self._planner_agent = planner_agent
        self._execution_service = execution_service

    # ---------------- Persisted execution ----------------
    def run(self, agent: AgentRead, task_in: TaskCreate) -> TaskRead:
        """
        Execute a task and persist the result.

        This is the main entry point for orchestrated task execution
        where results need to be saved.

        Parameters
        ----------
        agent : AgentRead
            Agent to execute
        task_in : TaskCreate
            Input task

        Returns
        -------
        TaskRead
            Persisted task with execution results
        """
        context = AgentExecutionContext()  # shared mutable context for this execution

        try:
            # 1️⃣ Generate execution plan
            plan = self._planner_agent.plan(agent=agent, task=task_in, context=context)

            # 2️⃣ Validate plan
            self._validate_plan(plan)

            # 3️⃣ Execute plan
            result = self._execution_service.execute_plan(plan=plan, task_in=task_in, context=context)

            # 4️⃣ Mark context as completed
            context.mark_completed()

            # 5️⃣ Persist task with results
            return self._task_service.create(task_in=task_in, execution_result=result.dict())

        except Exception as exc:
            # Mark failed if any exception occurs
            context.mark_failed(str(exc))
            raise

    # ---------------- Non-persisted execution ----------------
    def execute(self, agent: AgentRead, task_in: TaskCreate) -> ExecutionResult:
        """
        Execute a task without persisting the result.

        Useful for testing, preview, or ephemeral executions.

        Parameters
        ----------
        agent : AgentRead
            Agent to execute
        task_in : TaskCreate
            Input task

        Returns
        -------
        ExecutionResult
            Execution result without persistence
        """
        context = AgentExecutionContext()

        try:
            # Generate execution plan
            plan = self._planner_agent.plan(agent=agent, task=task_in, context=context)

            # Validate plan
            self._validate_plan(plan)

            # Execute plan
            result = self._execution_service.execute_plan(plan=plan, task_in=task_in, context=context)

            # Mark as completed
            context.mark_completed()

            return result

        except Exception as exc:
            # Mark failed in case of exception
            context.mark_failed(str(exc))
            raise

    # ---------------- Plan validation ----------------
    def _validate_plan(self, plan: ExecutionPlan) -> None:
        """
        Validate the execution plan before dispatching.

        Ensures:
        - SINGLE_AGENT plan has exactly one step
        - MULTI_AGENT plan has at least two steps
        - Unknown strategies are rejected

        Parameters
        ----------
        plan : ExecutionPlan
            Plan produced by PlannerAgent

        Raises
        ------
        ValueError
            If plan is invalid
        """
        if plan.strategy == ExecutionStrategy.SINGLE_AGENT:
            if not plan.steps or len(plan.steps) != 1:
                raise ValueError("SINGLE_AGENT requires exactly one agent step")
        elif plan.strategy == ExecutionStrategy.MULTI_AGENT:
            if not plan.steps or len(plan.steps) < 2:
                raise ValueError("MULTI_AGENT requires at least two agent steps")
        else:
            raise ValueError(f"Unknown execution strategy: {plan.strategy}")