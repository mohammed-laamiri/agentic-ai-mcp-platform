# app/api/routers/tool_router.py

from typing import List
from fastapi import APIRouter, Depends, HTTPException, status

from app.schemas.tool import ToolCreate, ToolRead
from app.services.tool_registry import ToolRegistry, ToolMetadata
from app.api.deps import get_tool_registry

router = APIRouter(tags=["Tools"])

# ----------------------------
# Tool Endpoints
# ----------------------------

@router.get("/health", status_code=200)
def tools_health() -> dict:
    """
    Health check endpoint for the tools router.
    """
    return {"status": "ok", "router": "tools"}


@router.post("/", response_model=ToolRead, status_code=status.HTTP_201_CREATED)
def register_tool(
    tool_in: ToolCreate,
    registry: ToolRegistry = Depends(get_tool_registry),
) -> ToolRead:
    """
    Register or update a tool in the registry.
    """
    try:
        # Convert Pydantic model to ToolMetadata dataclass
        metadata = ToolMetadata(
            tool_id=tool_in.tool_id,
            name=tool_in.name,
            version=tool_in.version,
            description=tool_in.description,
        )
        registry.register_tool(metadata=metadata)
        # Return the registered tool
        return ToolRead(
            tool_id=metadata.tool_id,
            name=metadata.name,
            version=metadata.version,
            description=metadata.description,
        )
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
    return ToolRead(
        tool_id=tool.tool_id,
        name=tool.name,
        version=tool.version,
        description=tool.description,
    )


@router.get("/", response_model=List[ToolRead])
def list_tools(
    registry: ToolRegistry = Depends(get_tool_registry),
) -> List[ToolRead]:
    """
    List all registered tools.
    """
    tools = registry.list_tools()
    return [
        ToolRead(
            tool_id=t.tool_id,
            name=t.name,
            version=t.version,
            description=t.description,
        )
        for t in tools
    ]
