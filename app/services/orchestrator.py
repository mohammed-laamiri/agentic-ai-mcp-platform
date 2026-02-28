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

    Does NOT execute agents or tools directly.
    """

    def __init__(
        self,
        task_service: TaskService,
        agent_service: AgentService,
        planner_agent: PlannerAgent,
        execution_service: ExecutionService,
    ) -> None:
        self._task_service = task_service
        self._agent_service = agent_service
        self._planner_agent = planner_agent
        self._execution_service = execution_service

    # ---------------- Persisted execution ----------------
    def run(self, agent: AgentRead, task_in: TaskCreate) -> TaskRead:
        """
        Execute a task and persist the result.
        """
        context = AgentExecutionContext()

        try:
            plan = self._planner_agent.plan(agent=agent, task=task_in, context=context)
            self._validate_plan(plan)
            result = self._execution_service.execute_plan(plan=plan, task_in=task_in, context=context)
            context.mark_completed()
            return self._task_service.create(task_in=task_in, execution_result=result.dict())
        except Exception as exc:
            context.mark_failed(str(exc))
            raise

    # ---------------- Non-persisted execution ----------------
    def execute(self, agent: AgentRead, task_in: TaskCreate) -> ExecutionResult:
        """
        Execute a task without persisting the result.
        """
        context = AgentExecutionContext()

        try:
            plan = self._planner_agent.plan(agent=agent, task=task_in, context=context)
            self._validate_plan(plan)
            result = self._execution_service.execute_plan(plan=plan, task_in=task_in, context=context)
            context.mark_completed()
            return result
        except Exception as exc:
            context.mark_failed(str(exc))
            raise

    # ---------------- Plan validation ----------------
    def _validate_plan(self, plan: ExecutionPlan) -> None:
        """
        Ensure execution plan is valid before execution.
        """
        if plan.strategy == ExecutionStrategy.SINGLE_AGENT:
            if not plan.steps or len(plan.steps) != 1:
                raise ValueError("SINGLE_AGENT requires exactly one agent step")
        elif plan.strategy == ExecutionStrategy.MULTI_AGENT:
            if not plan.steps or len(plan.steps) < 2:
                raise ValueError("MULTI_AGENT requires at least two agent steps")
        else:
            raise ValueError(f"Unknown execution strategy: {plan.strategy}")