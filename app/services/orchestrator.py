# app/services/orchestrator.py

"""
Orchestrator Service.

Coordinates high-level workflows for task execution without owning business logic.

Acts as the system conductor:
- Knows WHAT happens next (planning)
- Delegates HOW things are executed (agent & tool execution)
- Integrates MCP-compliant tool execution
- Persists results using TaskService & MemoryWriter
"""

from typing import Optional, List

from app.schemas.agent import AgentRead
from app.schemas.task import TaskCreate, TaskRead
from app.schemas.execution import ExecutionResult
from app.schemas.execution_plan import ExecutionPlan
from app.schemas.execution_strategy import ExecutionStrategy
from app.schemas.agent_execution_context import AgentExecutionContext
from app.schemas.tool_call import ToolCall
from app.schemas.execution_context import ExecutionContext

from app.services.agent_service import AgentService
from app.services.task_service import TaskService
from app.services.planner_agent import PlannerAgent
from app.services.tool_execution_engine import ToolExecutionEngine
from app.services.tool_registry import ToolRegistry
from app.services.memory_writer import MemoryWriter


class OrchestratorService:
    """
    High-level workflow coordinator.

    Responsibilities:
    - Run tasks via agents
    - Apply single or multi-agent strategies
    - Trigger MCP tool executions
    - Persist execution results via TaskService & MemoryWriter
    """

    def __init__(
        self,
        task_service: TaskService,
        agent_service: AgentService,
        tool_registry: ToolRegistry,
        memory_writer: MemoryWriter,
        planner_agent: Optional[PlannerAgent] = None,
    ) -> None:
        self._task_service = task_service
        self._agent_service = agent_service
        self._planner_agent = planner_agent or PlannerAgent()
        self._tool_engine = ToolExecutionEngine(tool_registry=tool_registry)
        self._memory_writer = memory_writer
        self._tool_registry = tool_registry

    # ==================================================
    # Public API
    # ==================================================

    def run(self, agent: AgentRead, task_in: TaskCreate) -> TaskRead:
        """
        Execute a task and persist result via TaskService.
        """
        context = AgentExecutionContext()
        plan = self._plan(agent, task_in, context)
        result = self._execute_plan(agent, task_in, plan, context)

        # Persist task domain object
        return self._task_service.create(
            task_in=task_in,
            execution_result=result.dict(),
        )

    def execute(self, agent: AgentRead, task_in: TaskCreate) -> ExecutionResult:
        """
        Execute a task without persistence.
        Returns raw ExecutionResult for testing or transient executions.
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
        """
        Generate an execution plan using PlannerAgent.
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
        Validates execution plan structure.
        Ensures strategy consistency and step requirements.
        """
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
        """
        Dispatch task execution according to strategy.
        Handles agent execution, tool execution, and result persistence.
        """
        self._validate_plan(plan)

        try:
            # -----------------------------
            # Agent execution phase
            # -----------------------------
            if plan.strategy == ExecutionStrategy.SINGLE_AGENT:
                result = self._execute_single_agent(agent, task_in, context)
            elif plan.strategy == ExecutionStrategy.MULTI_AGENT:
                result = self._execute_multi_agent_branching(task_in, plan, context)
            else:
                raise ValueError(f"Unsupported strategy: {plan.strategy}")

            # -----------------------------
            # Tool execution phase (MCP)
            # -----------------------------
            tool_results: List[ExecutionResult] = []
            if context.tool_calls:
                tool_results = self._tool_engine.execute_batch(
                    tool_calls=context.tool_calls,
                    context=context,
                    fail_fast=True,
                )
            result.child_results = (result.child_results or []) + tool_results

            # -----------------------------
            # Persist execution with MemoryWriter
            # -----------------------------
            exec_context = ExecutionContext(
                session_id="session-placeholder",
                user_id=None,
                strategy=plan.strategy,
                metadata={
                    "task_description": task_in.description,
                    "run_id": context.run_id,
                    "status": context.status,
                },
                tool_registry=self._tool_registry,
            )

            self._memory_writer.write(
                execution_result=result,
                agent_context=context,
                session_context=exec_context,
            )

            context.mark_completed("completed")
            return result

        except Exception as exc:
            context.mark_completed("failed")
            raise exc

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
        Execute a single agent task.
        """
        raw_result = self._agent_service.execute(agent, task_in, context)

        # Collect tool calls
        tool_calls = raw_result.get("tool_calls", [])
        for call in tool_calls:
            context.add_tool_call(ToolCall(**call))

        return ExecutionResult(**raw_result)

    def _execute_multi_agent_sequential(
        self,
        task_in: TaskCreate,
        plan: ExecutionPlan,
        context: AgentExecutionContext,
    ) -> ExecutionResult:
        """
        Execute multiple agents sequentially, passing outputs as inputs.
        """
        current_input = task_in.description
        final_result: Optional[ExecutionResult] = None

        for agent in plan.steps:
            intermediate_task = TaskCreate(
                description=current_input,
                input=current_input,
            )

            raw_result = self._agent_service.execute(agent, intermediate_task, context)

            # Collect tool calls
            tool_calls = raw_result.get("tool_calls", [])
            for call in tool_calls:
                context.add_tool_call(ToolCall(**call))

            final_result = ExecutionResult(**raw_result)
            current_input = final_result.output or ""

        if final_result is None:
            raise RuntimeError("Multi-agent execution produced no result")

        return final_result

    def _execute_multi_agent_branching(
        self,
        task_in: TaskCreate,
        plan: ExecutionPlan,
        parent_context: AgentExecutionContext,
    ) -> ExecutionResult:
        """
        Execute multiple agents in branching/parallel style.
        Aggregates all results as child_results.
        """
        child_results: List[ExecutionResult] = []
        for agent in plan.steps:
            # Each agent gets its own isolated context
            context = AgentExecutionContext(run_id=parent_context.run_id)
            intermediate_task = TaskCreate(
                description=task_in.description,
                input=task_in.description,
            )

            raw_result = self._agent_service.execute(agent, intermediate_task, context)

            # Merge tool calls into parent
            tool_calls = raw_result.get("tool_calls", [])
            for call in tool_calls:
                parent_context.add_tool_call(ToolCall(**call))

            child_results.append(ExecutionResult(**raw_result))

        # Return aggregated ExecutionResult
        aggregated_result = ExecutionResult(
            execution_id="aggregated-" + (task_in.description or "task"),
            output=None,
            status="SUCCESS",
            child_results=child_results,
        )

        return aggregated_result
