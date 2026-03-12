# app/services/execution/execution_service.py
"""
Execution Service (Async)

Handles execution of agent plans:
- Standard execution
- Streaming execution
- Token-level events
"""
# app/services/execution/execution_service.py
from typing import AsyncGenerator, List, Optional
from app.schemas.agent import AgentRead
from app.schemas.task import TaskCreate
from app.schemas.execution import ExecutionResult
from app.schemas.execution_plan import ExecutionPlan
from app.schemas.agent_execution_context import AgentExecutionContext
from app.schemas.execution_event import ExecutionEvent, ExecutionEventType


class ExecutionService:
    """
    Handles execution of agent plans.
    Supports both standard and streaming execution.
    """

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

    async def stream_execute_plan(
        self,
        agent: AgentRead,
        task: TaskCreate,
        plan: ExecutionPlan,
        context: AgentExecutionContext,
    ) -> AsyncGenerator[ExecutionEvent, None]:
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

                accumulated_output = ""
                simulated_output = (
                    f"Executing step '{step_name}' for agent '{getattr(step, 'id', 'unknown')}'."
                )

                for token in simulated_output.split(" "):
                    token_piece = token + " "
                    accumulated_output += token_piece
                    yield ExecutionEvent(
                        type=ExecutionEventType.TOKEN_CHUNK,
                        step_id=step_id,
                        step_name=step_name,
                        token=token_piece,
                    )

                step_outputs.append(accumulated_output.strip())

                yield ExecutionEvent(
                    type=ExecutionEventType.STEP_COMPLETED,
                    step_id=step_id,
                    step_name=step_name,
                    result={"output": accumulated_output.strip()},
                )

            final_output = "\n".join(step_outputs)
            final_result = ExecutionResult(status="success", output=final_output)

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