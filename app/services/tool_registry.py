"""
Tool Registry.

This is a skeleton implementation that defines the contract for:
- tool registration
- metadata storage
- permission checks
- versioning

This is intentionally minimal for now.
The goal is to establish a stable API for future tool execution and
MCP compatibility.
"""

from dataclasses import dataclass
from typing import Dict, Optional, List


@dataclass(frozen=True)
class ToolMetadata:
    """
    Tool metadata contract.

    Future extensions:
    - JSON schema
    - cost estimation
    - rate limits
    - required permissions
    - tool owner
    - tool type (llm, api, db, etc.)
    """
    tool_id: str
    name: str
    version: str
    description: str


class ToolRegistry:
    """
    In-memory tool registry.

    This registry is intentionally simple and will later be replaced by
    a persistent store (DynamoDB, Postgres, etc.)
    """

    def __init__(self) -> None:
        self._tools: Dict[str, ToolMetadata] = {}

    def register_tool(self, metadata: ToolMetadata) -> None:
        """
        Register a tool.

        If a tool already exists with the same ID, it will be replaced.
        """
        self._tools[metadata.tool_id] = metadata

    def get_tool(self, tool_id: str) -> Optional[ToolMetadata]:
        """
        Retrieve tool metadata by ID.
        """
        return self._tools.get(tool_id)

    def list_tools(self) -> List[ToolMetadata]:
        """
        List all registered tools.
        """
        return list(self._tools.values())

    def remove_tool(self, tool_id: str) -> None:
        """
        Remove a tool from the registry.
        """
        self._tools.pop(tool_id, None)
