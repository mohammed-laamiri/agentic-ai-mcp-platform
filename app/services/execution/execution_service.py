"""
ExecutionService — Central execution dispatcher

Responsibilities:
- Dispatch execution plans
- Integrate optional RAG retrieval
- Maintain clean service boundaries

Does NOT:
- Perform retrieval logic itself
- Know about Chroma internals
"""

from typing import Optional

from app.schemas.task import TaskCreate
from app.schemas.execution import ExecutionResult
from app.schemas.execution_plan import ExecutionPlan
from app.schemas.execution_strategy import ExecutionStrategy
from app.schemas.agent_execution_context import AgentExecutionContext

from app.services.agent_service import AgentService
from app.services.execution.single_agent_executor import SingleAgentExecutor
from app.services.execution.multi_agent_executor import MultiAgentExecutor
from app.services.rag.rag_service import RAGService


class ExecutionService:
    """
    Dispatches execution plans and optionally integrates RAG retrieval.
    """

    def __init__(
        self,
        agent_service: AgentService,
        rag_service: Optional[RAGService] = None,
    ) -> None:
        self._agent_service = agent_service
        self._rag_service = rag_service

        self._single_executor = SingleAgentExecutor(agent_service)
        self._multi_executor = MultiAgentExecutor(agent_service)

    # ==================================================
    # Public API
    # ==================================================

    def execute_plan(
        self,
        plan: ExecutionPlan,
        task_in: TaskCreate,
        context: AgentExecutionContext,
    ) -> ExecutionResult:
        """
        Execute plan based on strategy.

        If RAGService is provided, retrieved documents
        are stored in context.metadata["retrieved_docs"].
        """

        # ---------------- RAG Integration ----------------
        if self._rag_service and task_in.input:
            query = task_in.input.get("query")
            if query:
                retrieved_docs = self._rag_service.retrieve(
                    query=query,
                    top_k=5,
                )
                context.metadata["retrieved_docs"] = retrieved_docs

        # ---------------- Strategy Dispatch ----------------
        if plan.strategy == ExecutionStrategy.SINGLE_AGENT:
            return self._single_executor.execute(
                agent=plan.steps[0],
                task_in=task_in,
                context=context,
            )

        if plan.strategy == ExecutionStrategy.MULTI_AGENT:
            return self._multi_executor.execute(
                agents=plan.steps,
                task_in=task_in,
                context=context,
            )

        raise ValueError(f"Unsupported execution strategy: {plan.strategy}")