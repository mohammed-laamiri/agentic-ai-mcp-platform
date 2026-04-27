from typing import AsyncGenerator, List, Optional
from uuid import uuid4

from app.schemas.agent import AgentRead
from app.schemas.task import TaskCreate
from app.schemas.execution import ExecutionResult
from app.schemas.execution_plan import ExecutionPlan
from app.schemas.agent_execution_context import AgentExecutionContext
from app.schemas.execution_event import ExecutionEvent, ExecutionEventType


class ExecutionService:
    """
    SAFE Execution Service (STREAMING FIXED)

    Rules:
    - Only emit ExecutionEvent
    - Only primitives in SSE payload
    - Never leak Python objects / ORM / datetime
    """

    def __init__(self, agent_service=None, tool_engine=None):
        self.agent_service = agent_service
        self.tool_engine = tool_engine

    # ==========================================================
    # MAIN EXECUTION (non-stream)
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
                final_result = ExecutionResult(**event.result)

            if event.type == ExecutionEventType.EXECUTION_FAILED:
                raise RuntimeError(event.error)

        if final_result is None:
            raise RuntimeError("Execution did not produce a final result")

        return final_result

    # ==========================================================
    # STREAM EXECUTION (FIXED + SAFE)
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
            # START
            yield ExecutionEvent(
                type=ExecutionEventType.EXECUTION_STARTED,
                execution_id=execution_id,
            )

            step_outputs: List[str] = []

            for idx, step in enumerate(plan.steps):

                step_id = getattr(step, "id", idx)
                step_name = getattr(step, "name", f"step-{idx}")

                # STEP START
                yield ExecutionEvent(
                    type=ExecutionEventType.STEP_STARTED,
                    step_id=step_id,
                    step_name=str(step_name),
                )

                # simulate execution (safe placeholder)
                step_output = f"Executed step '{step_name}'"

                # TOKEN STREAM
                for token in step_output.split(" "):
                    yield ExecutionEvent(
                        type=ExecutionEventType.TOKEN_CHUNK,
                        step_id=step_id,
                        step_name=str(step_name),
                        token=f"{token} ",
                    )

                step_outputs.append(step_output)

                # STEP COMPLETE
                yield ExecutionEvent(
                    type=ExecutionEventType.STEP_COMPLETED,
                    step_id=step_id,
                    step_name=str(step_name),
                    result={"output": step_output},
                )

            final_output = "\n".join(step_outputs)

            # FINAL RESULT
            yield ExecutionEvent(
                type=ExecutionEventType.EXECUTION_COMPLETED,
                result={
                    "execution_id": execution_id,
                    "status": "success",
                    "output": final_output,
                },
            )

        except Exception as exc:
            yield ExecutionEvent(
                type=ExecutionEventType.EXECUTION_FAILED,
                error=str(exc),
            )
            raise