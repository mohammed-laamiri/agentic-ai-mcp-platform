"""
Agent service.

Responsible for:
- Executing agent logic
- Declaring tool calls
- Interacting with LLMs (later)
- Recording execution trace

Currently a deterministic stub.
"""

from datetime import datetime, timezone
from uuid import uuid4
from typing import Dict, Any

from app.schemas.agent import AgentRead
from app.schemas.task import TaskCreate
from app.schemas.agent_execution_context import AgentExecutionContext
from app.schemas.tool_call import ToolCall
from app.schemas.tool_result import ToolResult


class AgentService:
    """
    Executes tasks using a given agent.

    Architectural role:
    - Stable execution boundary
    - Future tool-aware agent runtime
    - Emits execution trace events
    """

    # ==================================================
    # Main Execution Entry Point
    # ==================================================

    def execute(
        self,
        agent: AgentRead,
        task: TaskCreate,
        context: AgentExecutionContext | None = None,
    ) -> Dict[str, Any]:
        """
        Execute a task using an agent.

        Returns:
            dict execution payload

        Tool calls are DECLARED, not executed.
        """

        execution_id = str(uuid4())

        # --------------------------------------------------
        # Trace: agent started
        # --------------------------------------------------

        if context is not None:
            context.add_trace(
                event_type="agent_started",
                payload={
                    "execution_id": execution_id,
                    "agent_id": agent.id,
                    "agent_name": agent.name,
                    "input": task.description,
                },
            )

        # --------------------------------------------------
        # Stub execution logic
        # --------------------------------------------------

        output = f"[STUB RESPONSE] Agent '{agent.name}' processed task."

        result: Dict[str, Any] = {
            "execution_id": execution_id,
            "agent_id": agent.id,
            "agent_name": agent.name,
            "input": task.description,
            "output": output,
            "timestamp": datetime.now(timezone.utc).isoformat(),
            # Future:
            # "tool_calls": []
        }

        # --------------------------------------------------
        # Trace: agent finished
        # --------------------------------------------------

        if context is not None:
            context.add_trace(
                event_type="agent_finished",
                payload={
                    "execution_id": execution_id,
                    "agent_id": agent.id,
                    "agent_name": agent.name,
                    "output": output,
                },
            )

        return result

    # ==================================================
    # Tool Execution Hook (NOT USED YET)
    # ==================================================

    def execute_tool(
        self,
        tool_call: ToolCall,
        context: AgentExecutionContext | None = None,
    ) -> ToolResult:
        """
        Stub tool execution.

        Future: delegated to ToolExecutor
        """

        timestamp = datetime.now(timezone.utc).isoformat()

        # Trace: tool started
        if context is not None:
            context.add_trace(
                event_type="tool_started",
                payload={
                    "tool_id": tool_call.tool_id,
                    "arguments": tool_call.arguments,
                },
            )

        result = ToolResult(
            tool_id=tool_call.tool_id,
            success=True,
            output=f"[STUB] Tool '{tool_call.tool_id}' executed.",
            error=None,
            metadata={
                "stub": True,
                "timestamp": timestamp,
            },
        )

        # Trace: tool finished
        if context is not None:
            context.add_trace(
                event_type="tool_finished",
                payload={
                    "tool_id": tool_call.tool_id,
                    "success": True,
                },
            )

        return result
