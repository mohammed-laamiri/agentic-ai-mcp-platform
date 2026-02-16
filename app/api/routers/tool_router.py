# app/api/routers/tool_router.py

from typing import List
from fastapi import APIRouter, Depends, HTTPException, status

from app.schemas.tool import ToolCreate, ToolRead
from app.services.tool_registry import ToolRegistry
from app.api.deps import get_tool_registry

router = APIRouter(tags=["Tools"])

# ----------------------------
# Tool Endpoints
# ----------------------------

@router.post("/", response_model=ToolRead, status_code=status.HTTP_201_CREATED)
def register_tool(
    tool_in: ToolCreate,
    registry: ToolRegistry = Depends(get_tool_registry),
) -> ToolRead:
    """
    Register or update a tool in the registry.
    """
    try:
        tool = registry.register_tool(metadata=tool_in)
        return ToolRead.model_validate(tool)  # Pydantic v2 compatible
    except Exception as exc:
        raise HTTPException(status_code=500, detail=str(exc))


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
    return ToolRead.model_validate(tool)


@router.get("/", response_model=List[ToolRead])
def list_tools(
    registry: ToolRegistry = Depends(get_tool_registry),
) -> List[ToolRead]:
    """
    List all registered tools.
    """
    tools = registry.list_tools()
    return [ToolRead.model_validate(t) for t in tools]


@router.get("/health", status_code=200)
def tools_health() -> dict:
    """
    Health check endpoint for the tools router.
    """
    return {"status": "ok", "router": "tools"}
