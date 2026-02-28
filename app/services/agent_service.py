"""
Agent service.

Responsible for:
- Executing agent logic
- Declaring tool calls
- Interacting with LLMs (later)
- Executing tools via ToolExecutor
- Returning standardized ExecutionResult objects
"""

from datetime import datetime, timezone
from uuid import uuid4
from typing import Optional, List

from app.schemas.agent import AgentRead
from app.schemas.task import TaskCreate
from app.schemas.execution import ExecutionResult
from app.schemas.agent_execution_context import AgentExecutionContext
from app.schemas.tool_call import ToolCall
from app.schemas.tool_result import ToolResult

from app.services.rag.rag_service import RAGService
from app.services.tool_executor import ToolExecutor
from app.services.tool_registry import ToolRegistry


class AgentService:
    """
    Executes tasks using a given agent.

    Architectural role:
    - Stable execution boundary
    - Tool-aware agent runtime
    - Produces standardized ExecutionResult
    """

    def __init__(self, rag_service: Optional[RAGService] = None) -> None:
        """
        Initialize AgentService with optional RAG and tool system.
        """
        self._rag_service = rag_service

        # Tool system
        self._tool_registry = ToolRegistry()
        self._tool_executor = ToolExecutor(tool_registry=self._tool_registry)

    # ==================================================
    # Main execution entrypoint
    # ==================================================

    def execute(
        self,
        agent: AgentRead,
        task: TaskCreate,
        context: Optional[AgentExecutionContext] = None,
    ) -> ExecutionResult:
        """
        Execute a task using an agent.

        Always returns ExecutionResult (NEVER dict).
        Safe for SINGLE_AGENT and MULTI_AGENT pipelines.
        """

        started_at = datetime.now(timezone.utc)

        try:
            # --------------------------------------------------
            # Ensure context exists
            # --------------------------------------------------
            if context is None:
                context = AgentExecutionContext()

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
                except Exception as rag_error:
                    context.metadata["rag_error"] = str(rag_error)

            context_text = (
                "\n".join(rag_context)
                if rag_context
                else "No RAG context available."
            )

            # --------------------------------------------------
            # Stub agent reasoning (LLM integration later)
            # --------------------------------------------------
            output = (
                f"[AGENT EXECUTION]\n"
                f"Agent ID: {agent.id}\n"
                f"Agent Name: {agent.name}\n\n"
                f"Task:\n{task.description}\n\n"
                f"Retrieved Context:\n{context_text}"
            )

            finished_at = datetime.now(timezone.utc)

            # --------------------------------------------------
            # Update execution context safely
            # --------------------------------------------------
            context.last_agent_id = agent.id
            context.last_execution_time = finished_at

            if "execution_trace" not in context.metadata:
                context.metadata["execution_trace"] = []

            context.metadata["execution_trace"].append(
                {
                    "agent_id": agent.id,
                    "timestamp": finished_at.isoformat(),
                    "status": "success",
                }
            )

            # --------------------------------------------------
            # Return STANDARDIZED ExecutionResult
            # --------------------------------------------------
            return ExecutionResult(
                tool_call_id=None,
                tool_id=None,
                status="success",
                output=output,
                error=None,
                tool_calls=[],
                started_at=started_at,
                finished_at=finished_at,
            )

        except Exception as exc:

            finished_at = datetime.now(timezone.utc)

            # Update context safely on failure
            if context:
                context.metadata["last_error"] = str(exc)

            return ExecutionResult(
                tool_call_id=None,
                tool_id=None,
                status="error",
                output=None,
                error=f"Agent execution failed: {str(exc)}",
                tool_calls=[],
                started_at=started_at,
                finished_at=finished_at,
            )

    # ==================================================
    # Tool execution via ToolExecutor
    # ==================================================

    def execute_tool(
        self,
        tool_call: ToolCall,
        context: Optional[AgentExecutionContext] = None,
    ) -> ToolResult:
        """
        Execute tool safely via ToolExecutor.
        """
        result = self._tool_executor.execute(tool_call=tool_call)

        # Optional context update
        if context:
            if "tool_execution_trace" not in context.metadata:
                context.metadata["tool_execution_trace"] = []

            context.metadata["tool_execution_trace"].append(
                {
                    "tool_id": tool_call.tool_id,
                    "status": result.status,
                    "timestamp": result.finished_at.isoformat()
                    if result.finished_at else None,
                }
            )

        return result