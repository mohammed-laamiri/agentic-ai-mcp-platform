"""
Agent service.

Responsible for:
- Executing agent logic
- Declaring tool calls
- Interacting with LLMs (later)

Currently a deterministic stub compatible with ExecutionResult schema.
"""

from datetime import datetime, timezone
from uuid import uuid4

from app.schemas.agent import AgentRead
from app.schemas.task import TaskCreate
from app.schemas.execution import ExecutionResult
from app.schemas.agent_execution_context import AgentExecutionContext
from app.schemas.tool_call import ToolCall
from app.schemas.tool_result import ToolResult

from app.services.rag.rag_service import RAGService


class AgentService:
    """
    Executes tasks using a given agent.

    Architectural role:
    - Stable execution boundary
    - Future tool-aware agent runtime
    """

    def __init__(self, rag_service: RAGService | None = None) -> None:
        """
        Inject RAG service.

        Optional for backward compatibility.
        """
        self._rag_service = rag_service

    # ==================================================
    # Main execution entrypoint
    # ==================================================

    def execute(
        self,
        agent: AgentRead,
        task: TaskCreate,
        context: AgentExecutionContext | None = None,
    ) -> dict:
        """
        Execute a task using an agent.

        Returns dict compatible with ExecutionResult.
        Tool calls are DECLARED, not executed.
        """

        started_at = datetime.now(timezone.utc)

        # --------------------------------------------------
        # Retrieve RAG context (if available)
        # --------------------------------------------------

        rag_context = []

        if self._rag_service:
            rag_context = self._rag_service.retrieve(
                query=task.description or "",
                top_k=3,
            )

        context_text = "\n".join(rag_context) if rag_context else "No RAG context."

        # --------------------------------------------------
        # Build stub output
        # --------------------------------------------------

        output = (
            f"[STUB RESPONSE]\n"
            f"Agent: {agent.name}\n\n"
            f"Task:\n{task.description}\n\n"
            f"Retrieved Context:\n{context_text}"
        )

        finished_at = datetime.now(timezone.utc)

        # --------------------------------------------------
        # Return ExecutionResult-compatible payload
        # --------------------------------------------------

        return {
            "tool_call_id": None,
            "tool_id": None,
            "status": "success",
            "output": output,
            "error": None,
            "tool_calls": [],
            "started_at": started_at,
            "finished_at": finished_at,
        }

    # ==================================================
    # Tool Execution Hook (future use)
    # ==================================================

    def execute_tool(
        self,
        tool_call: ToolCall,
        context: AgentExecutionContext | None = None,
    ) -> ToolResult:
        """
        Stub for tool execution.

        Actual execution will be handled by ToolExecutor later.
        """

        return ToolResult(
            tool_id=tool_call.tool_id,
            success=True,
            output=f"[STUB] Tool '{tool_call.tool_id}' executed.",
            error=None,
            metadata={
                "stub": True,
                "timestamp": datetime.now(timezone.utc).isoformat(),
            },
        )