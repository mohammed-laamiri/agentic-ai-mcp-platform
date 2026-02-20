"""
Tool API router.

Exposes endpoints for:
- Register
- Get by ID
- List all
- Execute a tool (via ToolExecutionEngine)
"""

from fastapi import APIRouter, Depends, HTTPException, status
from typing import List, Optional

from app.schemas.tool import ToolCreate, ToolRead
from app.schemas.tool_call import ToolCall
from app.schemas.tool_result import ToolResult
from app.services.tool_registry import ToolRegistry
from app.services.tool_execution_engine import ToolExecutionEngine, ToolValidationError
from app.api.deps import get_tool_registry, get_tool_execution_engine

router = APIRouter(prefix="/tools", tags=["Tools"])


# -------------------------
# CRUD Endpoints
# -------------------------

@router.post("/", response_model=ToolRead, status_code=status.HTTP_201_CREATED)
def register_tool(
    tool_in: ToolCreate,
    registry: ToolRegistry = Depends(get_tool_registry),
) -> ToolRead:
    """
    Register a new tool or update an existing one.
    """
    # Map ToolCreate → ToolMetadata
    registry.register_tool(
        metadata=tool_in  # ToolRegistry supports dataclass or pydantic model
    )
    return ToolRead(**tool_in.model_dump())


@router.get("/{tool_id}", response_model=ToolRead)
def get_tool(
    tool_id: str,
    registry: ToolRegistry = Depends(get_tool_registry),
) -> ToolRead:
    """
    Retrieve tool metadata by tool ID.
    """
    tool = registry.get_tool(tool_id)
    if tool is None:
        raise HTTPException(status_code=404, detail="Tool not found")
    return ToolRead(**tool.__dict__)


@router.get("/", response_model=List[ToolRead])
def list_tools(registry: ToolRegistry = Depends(get_tool_registry)) -> List[ToolRead]:
    """
    List all registered tools.
    """
    return [ToolRead(**t.__dict__) for t in registry.list_tools()]


# -------------------------
# Execution Endpoint
# -------------------------

@router.post("/execute", response_model=ToolResult)
def execute_tool(
    tool_call: ToolCall,
    engine: ToolExecutionEngine = Depends(get_tool_execution_engine),
) -> ToolResult:
    """
    Execute a registered tool via ToolExecutionEngine.
    """
    try:
        return engine.execute(tool_call)
    except ToolValidationError as exc:
        return ToolResult(
            tool_call_id=getattr(tool_call, "call_id", None),
            tool_id=tool_call.tool_id,
            status="error",
            output=None,
            error=str(exc),
            started_at=None,
            finished_at=None,
        )