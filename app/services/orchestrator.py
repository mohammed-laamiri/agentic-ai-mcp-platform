"""
Orchestrator.

Coordinates high-level workflows without owning business logic.

Acts as the system conductor:
- Knows WHAT happens next
- Does NOT know HOW things are implemented
"""

from typing import Optional
from uuid import uuid4

from app.schemas.agent import AgentRead
from app.schemas.task import TaskCreate, TaskRead
from app.schemas.execution import ExecutionResult
from app.schemas.execution_plan import ExecutionPlan
from app.schemas.execution_strategy import ExecutionStrategy
from app.schemas.agent_execution_context import AgentExecutionContext
from app.schemas.execution_context import ExecutionContext
from app.schemas.tool_call import ToolCall

from app.services.agent_service import AgentService
from app.services.task_service import TaskService
from app.services.planner_agent import PlannerAgent
from app.services.tool_execution_engine import ToolExecutionEngine
from app.services.tool_registry import ToolRegistry
from app.services.memory_writer import MemoryWriter
from app.services.rag.retrieval_service import RetrievalService


class Orchestrator:
    """
    High-level workflow coordinator.
    """

    def __init__(
        self,
        task_service: TaskService,
        agent_service: AgentService,
        tool_registry: ToolRegistry,
        memory_writer: MemoryWriter,
        retrieval_service: Optional[RetrievalService] = None,
        planner_agent: Optional[PlannerAgent] = None,
    ) -> None:
        self._task_service = task_service
        self._agent_service = agent_service
        self._planner_agent = planner_agent or PlannerAgent()
        self._tool_engine = ToolExecutionEngine(tool_registry=tool_registry)
        self._memory_writer = memory_writer
        self._retrieval_service = retrieval_service

    # ==================================================
    # Public API
    # ==================================================

    def run(self, agent: AgentRead, task_in: TaskCreate) -> TaskRead:
        agent_context = AgentExecutionContext()

        if self._retrieval_service and hasattr(task_in, "embedding"):
            chunks = self._retrieval_service.retrieve(query_embedding=task_in.embedding)
            agent_context.add_retrieved_chunks(chunks)

        plan = self._plan(agent, task_in, agent_context)
        result = self._execute_plan(agent, task_in, plan, agent_context)

        return self._task_service.create(
            task_in=task_in,
            execution_result=result.dict(),
        )

    def execute(self, agent: AgentRead, task_in: TaskCreate) -> ExecutionResult:
        agent_context = AgentExecutionContext()

        if self._retrieval_service and hasattr(task_in, "embedding"):
            chunks = self._retrieval_service.retrieve(query_embedding=task_in.embedding)
            agent_context.add_retrieved_chunks(chunks)

        plan = self._plan(agent, task_in, agent_context)
        return self._execute_plan(agent, task_in, plan, agent_context)

    # ==================================================
    # Planning
    # ==================================================

    def _plan(self, agent: AgentRead, task_in: TaskCreate, context: AgentExecutionContext) -> ExecutionPlan:
        return self._planner_agent.plan(agent=agent, task=task_in, context=context)

    # ==================================================
    # Helpers
    # ==================================================

    def _build_execution_result(self, raw_result: dict) -> ExecutionResult:
        """
        Normalize agent output into ExecutionResult contract.
        """
        payload = {
            "execution_id": raw_result.get("execution_id", str(uuid4())),
            "output": raw_result.get("output"),
            "tool_calls": raw_result.get("tool_calls", []),
        }
        return ExecutionResult(**payload)

    # ==================================================
    # Strategy normalization
    # ==================================================

    def _normalize_strategy(self, strategy) -> ExecutionStrategy:
        if isinstance(strategy, ExecutionStrategy):
            return strategy

        if isinstance(strategy, str):
            strategy_lower = strategy.lower()
            for member in ExecutionStrategy:
                if member.value.lower() == strategy_lower:
                    return member

        raise ValueError(f"Unknown strategy: {strategy}")

    # ==================================================
    # Validation
    # ==================================================

    def _validate_plan(self, plan: ExecutionPlan) -> None:
        strategy = self._normalize_strategy(plan.strategy)

        if strategy == ExecutionStrategy.SINGLE_AGENT:
            if plan.steps:
                raise ValueError("SINGLE_AGENT must not define steps")

        elif strategy == ExecutionStrategy.MULTI_AGENT:
            if not plan.steps or len(plan.steps) < 2:
                raise ValueError("MULTI_AGENT requires at least two agents")

    # ==================================================
    # Execution Dispatcher
    # ==================================================

    def _execute_plan(
        self,
        agent: AgentRead,
        task_in: TaskCreate,
        plan: ExecutionPlan,
        agent_context: AgentExecutionContext,
    ) -> ExecutionResult:
        strategy = self._normalize_strategy(plan.strategy)
        self._validate_plan(plan)

        if strategy == ExecutionStrategy.SINGLE_AGENT:
            result = self._execute_single_agent(agent, task_in, agent_context)
        elif strategy == ExecutionStrategy.MULTI_AGENT:
            result = self._execute_multi_agent_sequential(task_in, plan, agent_context)
        else:
            raise ValueError(f"Unsupported strategy: {strategy}")

        if agent_context.tool_calls:
            self._tool_engine.execute_batch(
                tool_calls=agent_context.tool_calls,
                context=agent_context,
                fail_fast=True,
            )

        session_context = ExecutionContext(
            task_id=getattr(task_in, "id", "unknown-task"),
            user_input=task_in.description,
        )

        self._memory_writer.write(
            execution_result=result,
            agent_context=agent_context,
            session_context=session_context,
        )

        return result

    # ==================================================
    # Execution Strategies
    # ==================================================

    def _execute_single_agent(
        self, agent: AgentRead, task_in: TaskCreate, context: AgentExecutionContext
    ) -> ExecutionResult:
        raw_result = self._agent_service.execute(agent, task_in, context)

        for call in raw_result.get("tool_calls", []):
            context.tool_calls.append(ToolCall(**call))

        result = self._build_execution_result(raw_result)

        session_context = ExecutionContext(
            task_id=getattr(task_in, "id", "unknown-task"),
            user_input=task_in.description,
        )

        self._memory_writer.write(
            execution_result=result,
            agent_context=context,
            session_context=session_context,
        )

        return result

    def _execute_multi_agent_sequential(
        self, task_in: TaskCreate, plan: ExecutionPlan, context: AgentExecutionContext
    ) -> ExecutionResult:
        current_input = task_in.description
        final_result: Optional[ExecutionResult] = None

        for agent in plan.steps:
            intermediate_task = TaskCreate(
                description=current_input,
                input={"text": current_input},
                embedding=getattr(task_in, "embedding", None),
            )

            raw_result = self._agent_service.execute(agent, intermediate_task, context)

            for call in raw_result.get("tool_calls", []):
                context.tool_calls.append(ToolCall(**call))

            step_result = self._build_execution_result(raw_result)
            final_result = step_result
            current_input = step_result.output or ""

            session_context = ExecutionContext(
                task_id=getattr(task_in, "id", "unknown-task"),
                user_input=intermediate_task.description,
            )

            self._memory_writer.write(
                execution_result=step_result,
                agent_context=context,
                session_context=session_context,
            )

        if final_result is None:
            raise RuntimeError("Multi-agent execution produced no result")

        return final_result
