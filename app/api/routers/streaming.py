"""
Streaming Execution Route (SSE - GET based)

This is the browser-compatible version using EventSource.

Key fixes:
- Uses GET instead of POST (required for EventSource)
- Uses task_id from query params
- Uses orchestrator.stream_execute (real streaming)
- SSE compliant
"""

import json
from typing import AsyncGenerator, Optional

from fastapi import APIRouter, Depends, Query
from fastapi.responses import StreamingResponse

from app.schemas.agent import AgentRead
from app.schemas.task import TaskCreate
from app.schemas.execution_event import ExecutionEvent
from app.services.orchestrator import OrchestratorService
from app.api.deps import get_orchestrator


router = APIRouter()


# ==========================================================
# MAIN STREAM ENDPOINT (BROWSER SAFE)
# ==========================================================

@router.get("/execute/stream")
async def stream_execution(
    task_id: str = Query(...),
    orchestrator: OrchestratorService = Depends(get_orchestrator),
):
    """
    SSE endpoint for browser EventSource.

    NOTE:
    - Must be GET (EventSource requirement)
    - task_id is passed via query param
    """

    async def event_generator() -> AsyncGenerator[str, None]:
        event_id = 0

        try:
            # 1. connection event
            event_id += 1
            yield _format_sse(
                event="connection",
                data={"status": "connected", "task_id": task_id},
                event_id=event_id,
            )

            # 2. minimal task payload (adapter layer)
            task_in = TaskCreate(
                name=f"task-{task_id}",
                description="stream execution",
            )

            # 3. stream from orchestrator
            async for event in orchestrator.stream_execute(
                agent=_default_agent(),
                task_in=task_in,
            ):
                event_id += 1

                yield _format_sse(
                    event=event.type.value,
                    data=_event_to_dict(event),
                    event_id=event_id,
                )

        except Exception as exc:
            yield _format_sse(
                event="error",
                data={"message": str(exc)},
                event_id=999,
            )

    return StreamingResponse(
        event_generator(),
        media_type="text/event-stream",
        headers={
            "Cache-Control": "no-cache",
            "Connection": "keep-alive",
        },
    )


# ==========================================================
# HELPERS
# ==========================================================

def _event_to_dict(event: ExecutionEvent) -> dict:
    return {
        "type": event.type.value,
        "step_id": event.step_id,
        "step_name": event.step_name,
        "strategy": event.strategy,
        "token": event.token,
        "steps": event.steps,
        "result": event.result,
        "error": event.error,
        "metadata": event.metadata,
    }


def _format_sse(event: str, data: dict, event_id: int) -> str:
    return (
        f"id: {event_id}\n"
        f"event: {event}\n"
        f"data: {json.dumps(data)}\n\n"
    )


def _default_agent() -> AgentRead:
    """
    Temporary fallback agent until frontend passes real agent.
    """
    return AgentRead(
        id="default-agent",
        name="default-agent",
    )