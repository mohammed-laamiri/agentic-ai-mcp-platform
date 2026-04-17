"""
Streaming Execution Route (SSE)

Provides real-time execution streaming via Server-Sent Events.

Design principles:
- Streaming is handled strictly at the API layer
- Business logic remains inside OrchestratorService
- SSE format follows RFC standards
- Future-ready for token-level streaming
"""

import asyncio
import json
import uuid
from typing import AsyncGenerator

from fastapi import APIRouter, Depends, Request
from fastapi.responses import StreamingResponse

from app.schemas.agent import AgentRead
from app.schemas.task import TaskCreate
from app.services.orchestrator import OrchestratorService
from app.api.deps import get_orchestrator


router = APIRouter()


# ============================
# Request Schema
# ============================

class StreamExecutionRequest(TaskCreate):
    """
    Combines Agent + Task payload into a single request body.

    This avoids FastAPI multiple-body-parameter issues.
    """

    agent: AgentRead


# ============================
# Streaming Endpoint
# ============================

@router.post("/execute/stream")
async def stream_execution(
    request: Request,
    payload: StreamExecutionRequest,
    orchestrator: OrchestratorService = Depends(get_orchestrator),
):
    """
    Stream execution lifecycle events in real time using SSE.
    """

    async def event_generator() -> AsyncGenerator[str, None]:
        event_id = 0

        try:
            # 🔹 Starting event
            event_id += 1
            yield _format_sse(
                event="status",
                data={"state": "starting"},
                event_id=event_id,
            )

            # 🔹 Optional heartbeat loop (in case execution is long)
            heartbeat_task = asyncio.create_task(
                _heartbeat(request)
            )

            # Execute orchestrator
            result = await orchestrator.execute(
                agent=payload.agent,
                task_in=payload,
            )

            # Cancel heartbeat once done
            heartbeat_task.cancel()

            # Result event
            event_id += 1
            yield _format_sse(
                event="result",
                data=result.model_dump(),
                event_id=event_id,
            )

            # Completed event
            event_id += 1
            yield _format_sse(
                event="status",
                data={"state": "completed"},
                event_id=event_id,
            )

        except asyncio.CancelledError:
            # Client disconnected
            return

        except Exception as exc:
            event_id += 1
            yield _format_sse(
                event="error",
                data={"message": str(exc)},
                event_id=event_id,
            )

    return StreamingResponse(
        event_generator(),
        media_type="text/event-stream",
        headers={
            "Cache-Control": "no-cache",
            "Connection": "keep-alive",
        },
    )


# ============================
# Helpers
# ============================

def _format_sse(event: str, data: dict, event_id: int) -> str:
    """
    Format Server-Sent Event message according to SSE spec.
    """
    return (
        f"id: {event_id}\n"
        f"event: {event}\n"
        f"data: {json.dumps(data)}\n\n"
    )


async def _heartbeat(request: Request, interval: int = 15):
    """
    Periodic heartbeat to keep connection alive during long executions.
    Stops automatically if client disconnects.
    """
    try:
        while True:
            if await request.is_disconnected():
                break
            await asyncio.sleep(interval)
    except asyncio.CancelledError:
        return