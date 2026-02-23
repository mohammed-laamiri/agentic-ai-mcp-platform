"""
Agent service.

Responsible for:
- Executing agent logic
- Declaring tool calls
- Interacting with LLMs (later)

Currently a deterministic stub.
"""

from datetime import datetime, timezone
from uuid import uuid4

from app.schemas.agent import AgentRead
from app.schemas.task import TaskCreate
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

    def execute(
        self,
        agent: AgentRead,
        task: TaskCreate,
        context: AgentExecutionContext | None = None,
    ) -> dict:
        """
        Execute a task using an agent.

        IMPORTANT:
        - Returns dict (execution payload)
        - Tool calls are DECLARED, not executed
        """

        # --------------------------------------------------
        # Retrieve RAG context (if available)
        # --------------------------------------------------

        rag_context = []

        if self._rag_service:
            rag_context = self._rag_service.retrieve(
                query=task.description,
                top_k=3,
            )

        context_text = "\n".join(rag_context) if rag_context else "No RAG context."

        # --------------------------------------------------
        # Build response
        # --------------------------------------------------

        output = (
            f"[STUB RESPONSE]\n"
            f"[AGENT RESPONSE]\n"
            f"Agent: {agent.name}\n\n"
            f"Task:\n{task.description}\n\n"
            f"Retrieved Context:\n{context_text}"
        )

        return {
            "execution_id": str(uuid4()),
            "agent_id": agent.id,
            "agent_name": agent.name,
            "input": task.description,
            "output": output,
            "timestamp": datetime.now(timezone.utc).isoformat(),
        }

    # ==================================================
    # Tool Execution Hook (NOT USED YET)
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