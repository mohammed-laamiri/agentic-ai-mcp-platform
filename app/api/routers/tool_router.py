"""
Tool API router.

Exposes endpoints for managing tools in the registry:
- Register
- Get by ID
- List all
"""

from fastapi import APIRouter, Depends, HTTPException, status
from typing import List

from app.schemas.tool import ToolCreate, ToolRead
from app.services.tool_registry import ToolRegistry
from app.api.deps import get_tool_registry

router = APIRouter(prefix="/tools", tags=["Tools"])


@router.post("/", response_model=ToolRead, status_code=status.HTTP_201_CREATED)
def register_tool(
    tool_in: ToolCreate,
    registry: ToolRegistry = Depends(get_tool_registry),
) -> ToolRead:
    """
    Register a new tool or update an existing one.
    """
    metadata = registry.register_tool(
        metadata=tool_in  # will adjust mapping in registry if needed
    )

    # Return read-only representation
    return ToolRead(
        tool_id=tool_in.tool_id,
        name=tool_in.name,
        version=tool_in.version,
        description=tool_in.description,
    )


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
def list_tools(registry: ToolRegistry = Depends(get_tool_registry)) -> List[ToolRead]:
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
