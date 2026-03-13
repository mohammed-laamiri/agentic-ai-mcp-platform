# app/services/planner_agent.py
from typing import List
from app.schemas.agent import AgentRead
from app.schemas.task import TaskCreate
from app.schemas.execution_plan import ExecutionPlan
from app.schemas.execution_strategy import ExecutionStrategy
from app.schemas.agent_execution_context import AgentExecutionContext
from app.schemas.tool_call import ToolCall
from app.services.rag.rag_service import RAGService


class PlannerAgent:
    """
    Planner Agent (Async-ready)
    Responsible for SINGLE_AGENT and MULTI_AGENT planning
    """

    def __init__(self, rag_service: RAGService | None = None) -> None:
        self._rag_service = rag_service

    async def plan(
        self,
        agent: AgentRead,
        task: TaskCreate,
        context: AgentExecutionContext | None = None,
    ) -> ExecutionPlan:
        task_text = (task.description or "").lower()

        # RAG context
        rag_context: List[str] = []
        if self._rag_service and task.description:
            try:
                result = self._rag_service.retrieve(query=task.description, top_k=3)
                rag_context = await result if hasattr(result, "__await__") else result
            except Exception:
                rag_context = []

        rag_count = len(rag_context)
        is_complex = self._is_complex_task(task_text)

        if is_complex:
            steps = self._assign_agents(task, agent)
            agent_steps_with_tools = []

            for idx, a in enumerate(steps):
                # Assign numeric step ID
                a_step = AgentRead(id=str(idx), name=a.name)
                tools = self._assign_tools(task, a)
                a_step.metadata = {"assigned_tools": tools}
                agent_steps_with_tools.append(a_step)

            if context:
                context.metadata["planning_strategy"] = "multi_agent"
                context.metadata["rag_context_count"] = rag_count

            return ExecutionPlan(
                strategy=ExecutionStrategy.MULTI_AGENT,
                steps=agent_steps_with_tools,
                reason=f"Task classified as complex; multi-agent execution. RAG items: {rag_count}",
            )

        # Single agent
        step_id = 0
        agent_step = AgentRead(id=str(step_id), name=agent.name)
        tools = self._assign_tools(task, agent)
        agent_step.metadata = {"assigned_tools": tools}

        if context:
            context.metadata["planning_strategy"] = "single_agent"
            context.metadata["rag_context_count"] = rag_count

        return ExecutionPlan(
            strategy=ExecutionStrategy.SINGLE_AGENT,
            steps=[agent_step],
            reason=f"Task classified as simple; single-agent execution. RAG items: {rag_count}",
        )

    def _is_complex_task(self, task_text: str) -> bool:
        keywords = [
            "analyze", "research", "compare", "summarize", "investigate",
            "evaluate", "explain", "search", "find", "review",
        ]
        return any(k in task_text for k in keywords)

    def _assign_agents(self, task: TaskCreate, lead_agent: AgentRead) -> List[AgentRead]:
        # Return a list of agents; we will assign numeric IDs in plan()
        return [lead_agent, lead_agent]

    def _assign_tools(self, task: TaskCreate, agent: AgentRead) -> List[ToolCall]:
        return []

    # ==========================================================
    # Sync method (backward compatibility)
    # ==========================================================

    def plan_sync(
        self,
        agent: AgentRead,
        task: TaskCreate,
        context: AgentExecutionContext | None = None,
    ) -> ExecutionPlan:
        """Synchronous planning method."""
        task_text = (task.description or "").lower()
        is_complex = self._is_complex_task(task_text)

        if is_complex:
            steps = self._assign_agents(task, agent)
            agent_steps_with_tools = []

            for idx, a in enumerate(steps):
                a_step = AgentRead(id=str(idx), name=a.name)
                tools = self._assign_tools(task, a)
                a_step.metadata = {"assigned_tools": tools}
                agent_steps_with_tools.append(a_step)

            if context:
                context.metadata["planning_strategy"] = "multi_agent"

            return ExecutionPlan(
                strategy=ExecutionStrategy.MULTI_AGENT,
                steps=agent_steps_with_tools,
                reason="Task classified as complex; multi-agent execution.",
            )

        # Single agent
        agent_step = AgentRead(id="0", name=agent.name)
        tools = self._assign_tools(task, agent)
        agent_step.metadata = {"assigned_tools": tools}

        if context:
            context.metadata["planning_strategy"] = "single_agent"

        return ExecutionPlan(
            strategy=ExecutionStrategy.SINGLE_AGENT,
            steps=[agent_step],
            reason="Task classified as simple; single-agent execution.",
        )