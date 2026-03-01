"""
Async Execution Service

Responsible for executing validated execution plans.

Supports:
- Standard execution (execute_plan)
- Streaming execution (stream_execute_plan)
- Token-level LLM streaming (TOKEN_CHUNK events)

No HTTP concerns.
Pure domain logic.
"""

from typing import AsyncGenerator, Optional, List

from app.schemas.agent import AgentRead
from app.schemas.task import TaskCreate
from app.schemas.execution import ExecutionResult
from app.schemas.execution_plan import ExecutionPlan
from app.schemas.agent_execution_context import AgentExecutionContext
from app.schemas.execution_event import (
    ExecutionEvent,
    ExecutionEventType,
)


class ExecutionService:
    """
    Handles execution of agent plans.

    This layer is responsible for:
    - Iterating through execution steps
    - Streaming structured domain events
    - Aggregating final execution result
    - Emitting token-level LLM output
    """

    # ==========================================================
    # Standard Execution (Backward Compatible)
    # ==========================================================

    async def execute_plan(
        self,
        agent: AgentRead,
        task: TaskCreate,
        plan: ExecutionPlan,
        context: AgentExecutionContext,
    ) -> ExecutionResult:
        """
        Execute a plan and return a final ExecutionResult.

        Internally consumes streaming execution but returns
        only the final result for backward compatibility.
        """

        final_result: Optional[ExecutionResult] = None

        async for event in self.stream_execute_plan(
            agent=agent,
            task=task,
            plan=plan,
            context=context,
        ):
            if event.type == ExecutionEventType.EXECUTION_COMPLETED:
                final_result = ExecutionResult(**event.data)

            if event.type == ExecutionEventType.EXECUTION_FAILED:
                raise RuntimeError(event.error)

        if final_result is None:
            raise RuntimeError("Execution did not produce a final result")

        return final_result

    # ==========================================================
    # Streaming Execution (Primary Engine)
    # ==========================================================

    async def stream_execute_plan(
        self,
        agent: AgentRead,
        task: TaskCreate,
        plan: ExecutionPlan,
        context: AgentExecutionContext,
    ) -> AsyncGenerator[ExecutionEvent, None]:
        """
        Stream execution lifecycle events.

        Emits strongly-typed ExecutionEvent objects.
        """

        try:
            # 🔹 Execution lifecycle started
            yield ExecutionEvent(
                type=ExecutionEventType.EXECUTION_STARTED,
            )

            step_outputs: List[str] = []

            # --------------------------------------------------
            # Iterate through execution steps
            # --------------------------------------------------
            for step in plan.steps:

                yield ExecutionEvent(
                    type=ExecutionEventType.STEP_STARTED,
                    step_id=step.id,
                    step_name=step.name,
                )

                accumulated_output = ""

                # --------------------------------------------------
                # 🔥 Simulated LLM Streaming
                # Replace this block with real LLM integration:
                #
                # async for token in self._llm.stream_generate(...):
                #     yield TOKEN_CHUNK
                # --------------------------------------------------

                simulated_output = (
                    f"Executing step '{step.name}' "
                    f"for agent '{step.agent_id}'."
                )

                for token in simulated_output.split(" "):
                    token_piece = token + " "
                    accumulated_output += token_piece

                    yield ExecutionEvent(
                        type=ExecutionEventType.TOKEN_CHUNK,
                        step_id=step.id,
                        step_name=step.name,
                        token=token_piece,
                    )

                step_outputs.append(accumulated_output.strip())

                yield ExecutionEvent(
                    type=ExecutionEventType.STEP_COMPLETED,
                    step_id=step.id,
                    step_name=step.name,
                    data={
                        "output": accumulated_output.strip()
                    },
                )

            # --------------------------------------------------
            # Aggregate final result
            # --------------------------------------------------
            final_output = "\n".join(step_outputs)

            final_result = ExecutionResult(
                success=True,
                output=final_output,
            )

            yield ExecutionEvent(
                type=ExecutionEventType.EXECUTION_COMPLETED,
                data=final_result.model_dump(),
            )

        except Exception as exc:

            yield ExecutionEvent(
                type=ExecutionEventType.EXECUTION_FAILED,
                error=str(exc),
            )

            raise