"""
PlannerExecutor (Async-ready)

High-level service that connects planning and execution layers.

Flow:

    Task
      ↓
    PlannerAgent.plan()   <-- now awaited
      ↓
    ExecutionPlan
      ↓
    ExecutionService.execute_plan(agent=...)
      ↓
    ExecutionResult

Responsibilities:
- Planning orchestration
- Execution orchestration
- Result normalization
- Plan metadata attachment
"""

from typing import Optional

from app.schemas.agent import AgentRead
from app.schemas.task import TaskCreate
from app.schemas.execution import ExecutionResult
from app.schemas.execution_plan import ExecutionPlan
from app.schemas.agent_execution_context import AgentExecutionContext

from app.services.planner_agent import PlannerAgent
from app.services.execution.execution_service import ExecutionService


class PlannerExecutor:
    """
    Orchestrates planning + execution.

    This is the main entrypoint used by OrchestratorService.
    Async-ready.
    """

    def __init__(
        self,
        planner_agent: PlannerAgent,
        execution_service: ExecutionService,
    ) -> None:
        self._planner_agent = planner_agent
        self._execution_service = execution_service

    # ==========================================================
    # Main public API
    # ==========================================================

    async def plan_and_execute(
        self,
        agent: AgentRead,
        task: TaskCreate,
        context: Optional[AgentExecutionContext] = None,
    ) -> ExecutionResult:
        """
        Plan execution and execute safely.

        Always returns ExecutionResult.
        Never returns dict.
        Never throws unhandled exceptions.
        """

        if context is None:
            context = AgentExecutionContext()

        # ------------------------------------------------------
        # Step 1: Create execution plan (await async plan)
        # ------------------------------------------------------
        try:
            plan: ExecutionPlan = await self._planner_agent.plan(
                agent=agent,
                task=task,
                context=context,
            )
        except Exception as e:
            return ExecutionResult(
                status="error",
                error=f"PlannerAgent.plan() failed: {e}",
            )

        # Safety guard: ensure plan is correct type
        if isinstance(plan, dict):
            plan = ExecutionPlan(**plan)

        # ------------------------------------------------------
        # Step 2: Execute plan (pass agent explicitly)
        # ------------------------------------------------------
        try:
            result = await self._execution_service.execute_plan(
                plan=plan,
                task_in=task,
                context=context,
                agent=agent,
            )
        except Exception as e:
            return ExecutionResult(
                status="error",
                error=f"ExecutionService.execute_plan() failed: {e}",
            )

        # ------------------------------------------------------
        # Step 3: Normalize result
        # ------------------------------------------------------
        if isinstance(result, dict):
            result = ExecutionResult(**result)

        if not isinstance(result, ExecutionResult):
            result = ExecutionResult(
                status="error",
                error="ExecutionService returned invalid result type",
            )

        # ------------------------------------------------------
        # Step 4: Attach planning metadata safely
        # ------------------------------------------------------
        try:
            result.plan_reason = getattr(plan, "reason", None)
        except Exception:
            # Never break execution due to metadata
            pass

        # ------------------------------------------------------
        # Step 5: Return final result
        # ------------------------------------------------------
        return result

    # ==========================================================
    # Sync API (backward compatibility)
    # ==========================================================

    def plan_and_execute_sync(
        self,
        agent: AgentRead,
        task: TaskCreate,
        context: Optional[AgentExecutionContext] = None,
    ) -> ExecutionResult:
        """
        Synchronous version of plan_and_execute.
        """
        if context is None:
            context = AgentExecutionContext()

        # Step 1: Create execution plan (sync)
        try:
            plan = self._planner_agent.plan_sync(
                agent=agent,
                task=task,
                context=context,
            )
        except Exception as e:
            return ExecutionResult(
                status="error",
                error=f"PlannerAgent.plan() failed: {e}",
            )

        # Safety guard: ensure plan is correct type
        if isinstance(plan, dict):
            plan = ExecutionPlan(**plan)

        # Step 2: Execute plan (sync)
        try:
            result = self._execution_service.execute_plan_sync(
                plan=plan,
                task_in=task,
                context=context,
                agent=agent,
            )
        except Exception as e:
            return ExecutionResult(
                status="error",
                error=f"ExecutionService.execute_plan() failed: {e}",
            )

        # Step 3: Normalize result
        if isinstance(result, dict):
            result = ExecutionResult(**result)

        if not isinstance(result, ExecutionResult):
            result = ExecutionResult(
                status="error",
                error="ExecutionService returned invalid result type",
            )

        # Step 4: Attach planning metadata
        try:
            result.plan_reason = getattr(plan, "reason", None)
        except Exception:
            pass

        return result