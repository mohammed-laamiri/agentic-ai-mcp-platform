"""
Planner agent.

Responsible for deciding *how* a task should be executed and
assigning tools to agents (hook only, actual execution deferred).

Implements:
- SINGLE_AGENT execution
- MULTI_AGENT sequential execution
- Tool assignment hooks
- RAG-enhanced planning
"""

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
    Decides execution strategy and agent sequencing.

    Architectural role:
    - Chooses execution strategy
    - Assigns execution steps
    - Declares tool calls (future use)
    - Uses RAG to enhance planning quality

    IMPORTANT:
    - Does NOT execute agents
    - Does NOT execute tools
    """

    def __init__(self, rag_service: RAGService | None = None) -> None:
        self._rag_service = rag_service

    # ==================================================
    # Main planning entrypoint
    # ==================================================

    def plan(
        self,
        agent: AgentRead,
        task: TaskCreate,
        context: AgentExecutionContext | None = None,
    ) -> ExecutionPlan:
        """
        Produce execution plan.

        Safe, deterministic planning logic.
        """

        task_text = (task.description or "").lower()

        # --------------------------------------------------
        # Retrieve RAG context safely
        # --------------------------------------------------

        rag_context: List[str] = []

        if self._rag_service and task.description:
            try:
                rag_context = self._rag_service.retrieve(
                    query=task.description,
                    top_k=3,
                )
            except Exception:
                rag_context = []

        rag_count = len(rag_context)

        # --------------------------------------------------
        # Determine complexity
        # --------------------------------------------------

        is_complex = self._is_complex_task(task_text)

        # --------------------------------------------------
        # MULTI_AGENT strategy
        # --------------------------------------------------

        if is_complex:

            steps = self._assign_agents(
                task=task,
                lead_agent=agent,
            )

            if context:
                context.metadata["planning_strategy"] = "multi_agent"
                context.metadata["rag_context_count"] = rag_count

            return ExecutionPlan(
                strategy=ExecutionStrategy.MULTI_AGENT,
                steps=steps,
                reason=(
                    "Task classified as complex; sequential multi-agent execution selected. "
                    f"RAG items retrieved: {rag_count}"
                ),
            )

        # --------------------------------------------------
        # SINGLE_AGENT strategy
        # --------------------------------------------------

        if context:
            context.metadata["planning_strategy"] = "single_agent"
            context.metadata["rag_context_count"] = rag_count

        return ExecutionPlan(
            strategy=ExecutionStrategy.SINGLE_AGENT,
            steps=[agent],
            reason=(
                "Task classified as simple; single-agent execution selected. "
                f"RAG items retrieved: {rag_count}"
            ),
        )

    # ==================================================
    # Complexity detection
    # ==================================================

    def _is_complex_task(self, task_text: str) -> bool:
        """
        Detect whether task requires multi-agent execution.
        """

        complexity_keywords = [
            "analyze",
            "research",
            "compare",
            "summarize",
            "investigate",
            "evaluate",
            "explain",
            "search",
            "find",
            "review",
        ]

        return any(keyword in task_text for keyword in complexity_keywords)

    # ==================================================
    # Agent assignment
    # ==================================================

    def _assign_agents(
        self,
        task: TaskCreate,
        lead_agent: AgentRead,
    ) -> List[AgentRead]:
        """
        Assign agents in execution order.

        Current behavior:
        - Uses lead agent twice (placeholder)

        Future:
        - ResearchAgent
        - AnalysisAgent
        - ToolAgent
        - SynthesisAgent
        """

        return [
            lead_agent,
            lead_agent,
        ]

    # ==================================================
    # Tool assignment hook (future)
    # ==================================================

    def _assign_tools(
        self,
        task: TaskCreate,
        agent: AgentRead,
    ) -> List[ToolCall]:
        """
        Hook to assign tools to agent.

        Tools are declared, not executed here.
        """

        return []