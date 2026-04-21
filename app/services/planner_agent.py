# app/services/planner_agent.py

from typing import List, Dict, Any
from app.schemas.agent import AgentRead
from app.schemas.task import TaskCreate
from app.schemas.execution_plan import ExecutionPlan
from app.schemas.execution_strategy import ExecutionStrategy
from app.schemas.agent_execution_context import AgentExecutionContext
from app.services.rag.rag_service import RAGService


class PlannerAgent:
    def __init__(self, rag_service: RAGService | None = None) -> None:
        self._rag_service = rag_service

    async def plan(
        self,
        agent: AgentRead,
        task: TaskCreate,
        context: AgentExecutionContext | None = None,
    ) -> ExecutionPlan:

        task_text = (task.description or "").lower()

        # -----------------------------
        # SAFE RAG
        # -----------------------------
        rag_context: List[str] = []
        if self._rag_service and task.description:
            try:
                result = self._rag_service.retrieve(query=task.description, top_k=3)
                rag_context = await result if hasattr(result, "__await__") else result
            except Exception:
                rag_context = []

        rag_count = len(rag_context)
        is_complex = self._is_complex_task(task_text)

        # -----------------------------
        # BUILD STEPS
        # -----------------------------
        if is_complex:
            steps = [agent, agent]
        else:
            steps = [agent]

        agent_steps = []

        for idx, a in enumerate(steps):
            a_step = AgentRead(id=str(idx), name=a.name)

            tools = self._assign_tools(task)

            # ✅ CRITICAL FIX: ALWAYS SAFE DICT
            a_step_dict = a_step.model_dump()
            a_step_dict["metadata"] = {
                "assigned_tools": tools
            }

            agent_steps.append(AgentRead(**a_step_dict))

        if context:
            context.metadata["planning_strategy"] = "multi_agent" if is_complex else "single_agent"
            context.metadata["rag_context_count"] = rag_count

        return ExecutionPlan(
            strategy=ExecutionStrategy.MULTI_AGENT if is_complex else ExecutionStrategy.SINGLE_AGENT,
            steps=agent_steps,
            reason=f"Task classified as {'complex' if is_complex else 'simple'}; RAG items: {rag_count}",
        )

    def _is_complex_task(self, task_text: str) -> bool:
        keywords = [
            "analyze", "research", "compare", "summarize", "investigate",
            "evaluate", "explain", "search", "find", "review",
        ]
        return any(k in task_text for k in keywords)

    # ✅ RETURN PURE DICTS (NO PYDANTIC OBJECTS)
    def _assign_tools(self, task: TaskCreate) -> List[Dict[str, Any]]:
        text = ((task.description or "") + " " + (task.name or "")).lower()

        tools = []

        if "echo" in text or "hello" in text or "test" in text:
            tools.append({
                "tool_id": "echo",
                "arguments": {
                    "message": task.description or task.name
                }
            })

        return tools

    # -----------------------------
    # SYNC VERSION (MATCHES ABOVE)
    # -----------------------------
    def plan_sync(
        self,
        agent: AgentRead,
        task: TaskCreate,
        context: AgentExecutionContext | None = None,
    ) -> ExecutionPlan:

        task_text = (task.description or "").lower()
        is_complex = self._is_complex_task(task_text)

        steps = [agent, agent] if is_complex else [agent]
        agent_steps = []

        for idx, a in enumerate(steps):
            a_step = AgentRead(id=str(idx), name=a.name)

            tools = self._assign_tools(task)

            a_step_dict = a_step.model_dump()
            a_step_dict["metadata"] = {
                "assigned_tools": tools
            }

            agent_steps.append(AgentRead(**a_step_dict))

        if context:
            context.metadata["planning_strategy"] = "multi_agent" if is_complex else "single_agent"

        return ExecutionPlan(
            strategy=ExecutionStrategy.MULTI_AGENT if is_complex else ExecutionStrategy.SINGLE_AGENT,
            steps=agent_steps,
            reason="Task classified automatically",
        )