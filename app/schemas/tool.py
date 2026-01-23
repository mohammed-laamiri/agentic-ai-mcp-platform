from pydantic import BaseModel, Field


class ToolBase(BaseModel):
    """
    Represents a callable tool exposed to agents.
    """

    name: str = Field(..., description="Unique tool name")
    description: str
    version: str = "v1"


class ToolRead(ToolBase):
    """
    Tool metadata exposed to agents or MCP.
    """

    enabled: bool = True
