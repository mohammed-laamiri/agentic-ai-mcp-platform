# app/api/routers/demo_router.py
from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from typing import Any, Dict

from app.runtime.runtime import tool_execution_engine

router = APIRouter()

# -----------------------------
# Request & Response Schemas
# -----------------------------
class DemoRequest(BaseModel):
    message: str

class DemoResponse(BaseModel):
    tool_call_id: str | None
    tool_id: str
    status: str
    output: Any
    error: str | None
    started_at: str
    finished_at: str


# -----------------------------
# Demo endpoint
# -----------------------------
@router.post("/demo/full", response_model=DemoResponse)
def full_demo(payload: DemoRequest):
    """
    Full demo of tool execution pipeline using echo tool.
    """

    # Construct a ToolCall dynamically
    from app.schemas.tool_call import ToolCall

    tool_call = ToolCall(
        tool_id="echo",
        arguments={"message": payload.message},
    )

    # Execute using singleton engine
    try:
        result = tool_execution_engine.execute(tool_call)

        # Convert datetime to ISO strings for JSON serialization
        response_data = DemoResponse(
            tool_call_id=result.tool_call_id,
            tool_id=result.tool_id,
            status=result.status,
            output=result.output,
            error=result.error,
            started_at=result.started_at.isoformat(),
            finished_at=result.finished_at.isoformat(),
        )

        return response_data

    except Exception as exc:
        raise HTTPException(status_code=500, detail=f"Demo pipeline failed: {str(exc)}")