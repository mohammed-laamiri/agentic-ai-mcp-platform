"""
Tool API router.

Exposes endpoints for managing tools in the registry:
- Register metadata
- Get metadata
- List tools
- Execute tools (MVP critical endpoint)
"""

from fastapi import APIRouter, Depends, HTTPException, status
from typing import List, Dict, Any

from app.schemas.tool import ToolCreate, ToolRead
from app.services.tool_registry import ToolRegistry, ToolMetadata
from app.services.tool_execution_engine import ToolExecutionEngine

from app.api.deps import (
    get_tool_registry,
    get_tool_execution_engine,
)

router = APIRouter(prefix="/tools", tags=["Tools"])


# =====================================================
# Register Tool Metadata
# =====================================================

@router.post(
    "/",
    response_model=ToolRead,
    status_code=status.HTTP_201_CREATED,
)
def register_tool(
    tool_in: ToolCreate,
    registry: ToolRegistry = Depends(get_tool_registry),
) -> ToolRead:
    """
    Register or update tool metadata.

    NOTE:
    - Callable binding is handled separately
    - This endpoint registers metadata only
    """

    metadata = ToolMetadata(
        tool_id=tool_in.tool_id,
        name=tool_in.name,
        version=tool_in.version,
        description=tool_in.description,
        input_schema=getattr(tool_in, "input_schema", None),
    )

    registry.register_tool(metadata)

    return ToolRead(
        tool_id=metadata.tool_id,
        name=metadata.name,
        version=metadata.version,
        description=metadata.description,
    )


# =====================================================
# Get Tool Metadata
# =====================================================

@router.get(
    "/{tool_id}",
    response_model=ToolRead,
)
def get_tool(
    tool_id: str,
    registry: ToolRegistry = Depends(get_tool_registry),
) -> ToolRead:
    """
    Retrieve tool metadata by ID.
    """

    tool = registry.get_tool(tool_id)

    if tool is None:
        raise HTTPException(
            status_code=404,
            detail=f"Tool '{tool_id}' not found",
        )

    return ToolRead(
        tool_id=tool.tool_id,
        name=tool.name,
        version=tool.version,
        description=tool.description,
    )


# =====================================================
# List Tools
# =====================================================

@router.get(
    "/",
    response_model=List[ToolRead],
)
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


# =====================================================
# Execute Tool (MVP CRITICAL ENDPOINT)
# =====================================================

@router.post(
    "/{tool_id}/execute",
)
def execute_tool(
    tool_id: str,
    payload: Dict[str, Any],
    engine: ToolExecutionEngine = Depends(get_tool_execution_engine),
):
    """
    Execute a registered tool.

    MVP version:
    - No persistence
    - No retries
    - No timeouts
    - Direct execution only
    """

    try:

        result = engine.execute(
            tool_id=tool_id,
            arguments=payload,
        )

        return {
            "tool_id": tool_id,
            "success": True,
            "output": result,
        }

    except Exception as exc:

        raise HTTPException(
            status_code=400,
            detail=str(exc),
        )