"""
Planner agent.

Responsible for deciding *how* a task should be executed and
assigning tools to agents (hook only, actual execution deferred).

This module implements:
- SINGLE_AGENT for simple tasks
- MULTI_AGENT (sequential) for complex tasks
- Tool assignment hooks for future integration
- RAG context retrieval to enhance planning decisions
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
    Decides execution strategy and assigns tools.

    Architectural role:
    - Chooses execution strategy
    - Defines agent order
    - Declares tool calls (hooks only, no execution here)
    - Retrieves RAG knowledge to enhance planning
    """

    def __init__(self, rag_service: RAGService | None = None) -> None:
        """
        Inject RAG service.

        Optional to preserve backward compatibility and testing flexibility.
        """
        self._rag_service = rag_service

    def plan(
        self,
        agent: AgentRead,
        task: TaskCreate,
        context: AgentExecutionContext | None = None,
    ) -> ExecutionPlan:
        """
        Produce an execution plan.

        Current rules:
        - Default: SINGLE_AGENT
        - Complex tasks: MULTI_AGENT (sequential)
        - Uses RAG context (if available) to enhance reasoning
        """

        task_text = (task.description or "").lower()

        # --------------------------------------------------
        # Retrieve RAG context (safe, optional)
        # --------------------------------------------------

        rag_context: List[str] = []

        if self._rag_service and task.description:
            try:
                rag_context = self._rag_service.retrieve(
                    query=task.description,
                    top_k=3,
                )
            except Exception:
                # Fail-safe: planning must never crash due to RAG
                rag_context = []

        rag_count = len(rag_context)

        # --------------------------------------------------
        # Determine task complexity
        # --------------------------------------------------

        is_complex = any(
            keyword in task_text
            for keyword in [
                "analyze",
                "research",
                "compare",
                "summarize",
                "find",
                "search",
                "explain",
            ]
        )

        # --------------------------------------------------
        # Multi-agent execution
        # --------------------------------------------------

        if is_complex:
            steps = self._assign_agents(task, lead_agent=agent)

            return ExecutionPlan(
                strategy=ExecutionStrategy.MULTI_AGENT,
                steps=steps,
                reason=(
                    "Task classified as complex; using sequential multi-agent execution. "
                    f"RAG context items retrieved: {rag_count}"
                ),
            )

        # --------------------------------------------------
        # Single-agent execution
        # --------------------------------------------------

        return ExecutionPlan(
            strategy=ExecutionStrategy.SINGLE_AGENT,
            steps=[agent],
            reason=(
                "Task classified as simple; using single-agent execution. "
                f"RAG context items retrieved: {rag_count}"
            ),
        )

    # ------------------------------------------
    # Agent assignment
    # ------------------------------------------

    def _assign_agents(
        self,
        task: TaskCreate,
        lead_agent: AgentRead,
    ) -> List[AgentRead]:
        """
        Assigns a sequence of agents to execute this task.

        Current behavior:
        - Placeholder: uses lead_agent twice
        - Future: specialized agents (ResearchAgent, AnalysisAgent, etc.)
        """
        return [lead_agent, lead_agent]

    # ------------------------------------------
    # Tool assignment hooks (future use)
    # ------------------------------------------

    def _assign_tools(
        self,
        task: TaskCreate,
        agent: AgentRead,
    ) -> List[ToolCall]:
        """
        Hook to assign tools to an agent.

        IMPORTANT:
        - Does NOT execute tools
        - Only declares ToolCall objects
        - Execution handled later by ToolExecutionEngine
        """
        return []