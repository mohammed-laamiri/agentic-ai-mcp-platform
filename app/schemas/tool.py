"""
Tool schema.

Defines the structured representation of a tool for:
- registration
- discovery
- execution metadata
"""

from pydantic import BaseModel, Field


class ToolCreate(BaseModel):
    """
    Input payload for creating/registering a tool.
    """

    tool_id: str = Field(..., description="Unique tool identifier")
    name: str = Field(..., description="Human-readable tool name")
    version: str = Field(..., description="Semantic version of the tool")
    description: str = Field(..., description="Brief description of the tool")


class ToolRead(BaseModel):
    """
    Read-only representation of a registered tool.
    """

    tool_id: str = Field(..., description="Unique tool identifier")
    name: str = Field(..., description="Human-readable tool name")
    version: str = Field(..., description="Semantic version of the tool")
    description: str = Field(..., description="Brief description of the tool")
