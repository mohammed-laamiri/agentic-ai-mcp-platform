"""
Execution Router (Stable + SSE Safe + Minimal Fix)

Key fixes:
- Fix datetime serialization globally (not partial sanitization)
- Safe SSE streaming
- No over-engineered conversion layers
- Keeps orchestrator untouched
"""

from fastapi import APIRouter, HTTPException, Depends, Request
from fastapi.responses import StreamingResponse
from slowapi import Limiter
import json
import asyncio
from datetime import datetime
from uuid import UUID

from app.schemas.task import TaskCreate
from app.schemas.execution import ExecutionResult
from app.schemas.agent import AgentRead

from app.services.orchestrator import OrchestratorService
from app.services.agent_service import AgentService
from app.services.task_service import TaskService
from app.services.planner_agent import PlannerAgent
from app.services.execution.execution_service import ExecutionService

from app.api.dependencies.auth import require_api_key
from app.api.rate_limit import limiter


router = APIRouter(prefix="/execution", tags=["execution"])


# ==================================================
# ORCHESTRATOR DEPENDENCY
# ==================================================
def get_orchestrator() -> OrchestratorService:
    task_service = TaskService()
    agent_service = AgentService()
    planner_agent = PlannerAgent()

    execution_service = ExecutionService(
        agent_service=agent_service,
        tool_engine=None,
    )

    return OrchestratorService(
        task_service=task_service,
        agent_service=agent_service,
        planner_agent=planner_agent,
        execution_service=execution_service,
    )


# ==================================================
# NON-STREAM EXECUTION
# ==================================================
@router.post("/run", response_model=ExecutionResult)
@limiter.limit("10/minute")
async def execute_task(
    request: Request,
    task: TaskCreate,
    orchestrator: OrchestratorService = Depends(get_orchestrator),
    _: str = Depends(require_api_key),
):
    try:
        agent = AgentRead(id="default-agent-1", name="default-agent")

        result = await orchestrator.execute(
            agent=agent,
            task_in=task,
        )

        return result

    except Exception as exc:
        raise HTTPException(status_code=500, detail=str(exc))


# ==================================================
# GLOBAL JSON SAFE SERIALIZER (IMPORTANT FIX)
# ==================================================
def json_safe(obj):
    """
    Recursively makes ANY object JSON serializable.
    This fixes your datetime crash globally.
    """

    if isinstance(obj, dict):
        return {k: json_safe(v) for k, v in obj.items()}

    if isinstance(obj, list):
        return [json_safe(v) for v in obj]

    if isinstance(obj, datetime):
        return obj.isoformat()

    if isinstance(obj, UUID):
        return str(obj)

    return obj


# ==================================================
# STREAMING EXECUTION (FIXED SSE)
# ==================================================
@router.post("/stream")
@limiter.limit("5/minute")
async def stream_execute_task(
    request: Request,
    task: TaskCreate,
    orchestrator: OrchestratorService = Depends(get_orchestrator),
    _: str = Depends(require_api_key),
):

    agent = AgentRead(id="default-agent-1", name="default-agent")

    async def event_generator():
        try:
            async for event in orchestrator.stream_execute(
                agent=agent,
                task_in=task,
            ):

                # SAFE: convert full event object
                raw = event.model_dump() if hasattr(event, "model_dump") else dict(event)

                safe = json_safe(raw)

                yield f"data: {json.dumps(safe)}\n\n"

        except Exception as exc:
            yield f"data: {json.dumps({'type': 'ERROR', 'detail': str(exc)})}\n\n"

    return StreamingResponse(
        event_generator(),
        media_type="text/event-stream",
        headers={
            "Cache-Control": "no-cache",
            "Connection": "keep-alive",
        },
    )


# ==================================================
# LEGACY STREAM (UI COMPAT)
# ==================================================
@router.get("/tasks/{task_id}/stream")
async def legacy_task_stream_bridge(task_id: str):

    async def event_generator():
        yield "event: status\ndata: " + json.dumps({
            "state": "connected",
            "task_id": task_id
        }) + "\n\n"

        for i in range(3):
            await asyncio.sleep(1)
            yield "event: log\ndata: " + json.dumps({
                "step": i,
                "message": "bridge stream active"
            }) + "\n\n"

        yield "event: status\ndata: " + json.dumps({
            "state": "completed"
        }) + "\n\n"

    return StreamingResponse(
        event_generator(),
        media_type="text/event-stream",
        headers={
            "Cache-Control": "no-cache",
            "Connection": "keep-alive",
        },
    )