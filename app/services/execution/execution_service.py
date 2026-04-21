from typing import AsyncGenerator, List, Optional, Any, Dict
from uuid import uuid4

from app.schemas.agent import AgentRead
from app.schemas.task import TaskCreate
from app.schemas.execution import ExecutionResult
from app.schemas.execution_plan import ExecutionPlan
from app.schemas.execution_strategy import ExecutionStrategy
from app.schemas.agent_execution_context import AgentExecutionContext
from app.schemas.execution_event import ExecutionEvent, ExecutionEventType


class ExecutionService:
    """
    Handles execution of agent plans.
    SAFE VERSION: supports tool execution without breaking anything.
    """

    # ==========================================================
    # MAIN EXECUTION (ASYNC)
    # ==========================================================
    async def execute_plan(
        self,
        agent: AgentRead,
        task_in: TaskCreate,
        plan: ExecutionPlan,
        context: AgentExecutionContext,
    ) -> ExecutionResult:

        final_result: Optional[ExecutionResult] = None

        async for event in self.stream_execute_plan(agent, task_in, plan, context):
            if event.type == ExecutionEventType.EXECUTION_COMPLETED:
                if event.result is None:
                    raise RuntimeError("Execution completed event missing result")
                final_result = ExecutionResult(**event.result)

            if event.type == ExecutionEventType.EXECUTION_FAILED:
                raise RuntimeError(event.error)

        if final_result is None:
            raise RuntimeError("Execution did not produce a final result")

        return final_result

    # ==========================================================
    # STREAM EXECUTION
    # ==========================================================
    async def stream_execute_plan(
        self,
        agent: AgentRead,
        task: TaskCreate,
        plan: ExecutionPlan,
        context: AgentExecutionContext,
    ) -> AsyncGenerator[ExecutionEvent, None]:

        execution_id = str(uuid4())

        try:
            yield ExecutionEvent(type=ExecutionEventType.EXECUTION_STARTED)

            step_outputs: List[str] = []

            for idx, step in enumerate(plan.steps):
                step_id = getattr(step, "id", idx)
                step_name = getattr(step, "name", f"step-{idx}")

                yield ExecutionEvent(
                    type=ExecutionEventType.STEP_STARTED,
                    step_id=step_id,
                    step_name=step_name,
                )

                # ==================================================
                # SAFE TOOL EXTRACTION (FIXED)
                # ==================================================
                tools = self._extract_tools(step)

                # ==================================================
                # TOOL EXECUTION
                # ==================================================
                if tools:
                    tool_outputs = []

                    for tool in tools:
                        tool_id, args = self._normalize_tool(tool)

                        if tool_id == "echo":
                            message = args.get("message", "")
                            output = f"[Echo Tool]: {message}"
                        else:
                            output = f"[Unknown tool: {tool_id}]"

                        tool_outputs.append(output)

                        for token in output.split(" "):
                            yield ExecutionEvent(
                                type=ExecutionEventType.TOKEN_CHUNK,
                                step_id=step_id,
                                step_name=step_name,
                                token=token + " ",
                            )

                    final_step_output = " ".join(tool_outputs)

                else:
                    # fallback (original behavior)
                    final_step_output = (
                        f"Executing step '{step_name}' for agent '{step_id}'."
                    )

                    for token in final_step_output.split(" "):
                        yield ExecutionEvent(
                            type=ExecutionEventType.TOKEN_CHUNK,
                            step_id=step_id,
                            step_name=step_name,
                            token=token + " ",
                        )

                step_outputs.append(final_step_output.strip())

                yield ExecutionEvent(
                    type=ExecutionEventType.STEP_COMPLETED,
                    step_id=step_id,
                    step_name=step_name,
                    result={"output": final_step_output.strip()},
                )

            final_output = "\n".join(step_outputs)

            final_result = ExecutionResult(
                execution_id=execution_id,
                status="success",
                output=final_output,
            )

            yield ExecutionEvent(
                type=ExecutionEventType.EXECUTION_COMPLETED,
                result=final_result.model_dump(),
            )

        except Exception as exc:
            yield ExecutionEvent(
                type=ExecutionEventType.EXECUTION_FAILED,
                error=str(exc),
            )
            raise

    # ==========================================================
    # TOOL EXTRACTION (ROBUST)
    # ==========================================================
    def _extract_tools(self, step) -> List[Any]:
        """
        Safely extract tools from step regardless of Pydantic/dict state.
        """
        tools = []

        try:
            # Case 1: normal object with metadata
            metadata = getattr(step, "metadata", None)
            if isinstance(metadata, dict):
                tools = metadata.get("assigned_tools") or []

            # Case 2: Pydantic model fallback
            elif hasattr(step, "model_dump"):
                step_dict = step.model_dump() or {}
                tools = step_dict.get("metadata", {}).get("assigned_tools") or []

        except Exception:
            tools = []

        return tools

    # ==========================================================
    # TOOL NORMALIZATION (SAFE)
    # ==========================================================
    def _normalize_tool(self, tool: Any) -> tuple[str, Dict]:
        """
        Returns (tool_id, args) safely for both dict and object tools.
        """

        if isinstance(tool, dict):
            return tool.get("tool_id"), tool.get("arguments", {}) or {}

        tool_id = getattr(tool, "tool_id", None)
        args = getattr(tool, "arguments", None) or {}

        return tool_id, args

    # ==========================================================
    # SYNC VERSION
    # ==========================================================
    def execute_plan_sync(
        self,
        agent: AgentRead,
        task_in: TaskCreate,
        plan: ExecutionPlan,
        context: AgentExecutionContext,
    ) -> ExecutionResult:

        execution_id = str(uuid4())
        step_outputs: List[str] = []

        for idx, step in enumerate(plan.steps):

            tools = self._extract_tools(step)

            if tools:
                for tool in tools:
                    tool_id, args = self._normalize_tool(tool)

                    if tool_id == "echo":
                        message = args.get("message", "")
                        step_outputs.append(f"[Echo Tool]: {message}")
                    else:
                        step_outputs.append(f"[Unknown tool: {tool_id}]")
            else:
                step_outputs.append(
                    f"Executing step '{step.name}' for agent '{step.id}'"
                )

        return ExecutionResult(
            execution_id=execution_id,
            status="success",
            output="\n".join(step_outputs),
        )