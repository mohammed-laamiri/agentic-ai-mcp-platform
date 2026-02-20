"""
Tool Registry.

Runtime registry responsible for:
- Tool metadata registration
- Discovery by agents and planners
- Version awareness
- Validation boundaries
- Execution binding

IMPORTANT:
- This registry does NOT execute tools
- This registry does NOT enforce permissions (yet)
- This registry is a runtime dependency, not a domain model

Future replacements:
- DynamoDB / Postgres
- MCP-compatible tool index
"""

from dataclasses import dataclass
from typing import Dict, Optional, List, Callable, Any


@dataclass(frozen=True)
class ToolMetadata:
    """
    Immutable tool metadata contract.

    SAFE to expose to planners.
    """

    tool_id: str
    name: str
    version: str
    description: str


@dataclass
class RegisteredTool:
    """
    Internal runtime representation of a tool.

    Contains:
    - Metadata (safe)
    - Execution binding (private to runtime)
    - Optional argument schema
    """

    metadata: ToolMetadata
    callable: Callable[..., Any]
    input_schema: Optional[dict] = None


class ToolRegistry:
    """
    In-memory tool registry.

    Architectural role:
    - Source of truth for tool metadata
    - Provides execution bindings
    - Enables validation and execution layers
    """

    def __init__(self) -> None:
        self._tools: Dict[str, RegisteredTool] = {}

    # --------------------------------------------------
    # Registration
    # --------------------------------------------------

    def register_tool(
        self,
        metadata: ToolMetadata,
        tool_callable: Callable[..., Any],
        input_schema: Optional[dict] = None,
    ) -> None:
        """
        Register or update a tool definition.

        Behavior:
        - If tool_id exists → replaced
        - If tool_id is new → inserted
        """

        self._tools[metadata.tool_id] = RegisteredTool(
            metadata=metadata,
            callable=tool_callable,
            input_schema=input_schema,
        )

    # --------------------------------------------------
    # Retrieval (Metadata)
    # --------------------------------------------------

    def get_tool(self, tool_id: str) -> Optional[ToolMetadata]:
        """
        Retrieve tool metadata by tool ID.

        Returns:
        - ToolMetadata if found
        - None if tool does not exist
        """

        tool = self._tools.get(tool_id)
        return tool.metadata if tool else None

    def list_tools(self) -> List[ToolMetadata]:
        """
        List all registered tools.

        Order is NOT guaranteed.
        """

        return [tool.metadata for tool in self._tools.values()]

    def has_tool(self, tool_id: str) -> bool:
        """
        Check whether a tool exists in the registry.
        """

        return tool_id in self._tools

    # --------------------------------------------------
    # Execution Binding
    # --------------------------------------------------

    def get_callable(self, tool_id: str) -> Optional[Callable[..., Any]]:
        """
        Retrieve execution callable for a tool.
        """

        tool = self._tools.get(tool_id)
        return tool.callable if tool else None

    def get_input_schema(self, tool_id: str) -> Optional[dict]:
        """
        Retrieve input schema for validation (optional).
        """

        tool = self._tools.get(tool_id)
        return tool.input_schema if tool else None

    # --------------------------------------------------
    # Removal
    # --------------------------------------------------

    def remove_tool(self, tool_id: str) -> None:
        """
        Remove a tool from the registry.

        Silent if tool does not exist.
        """

        self._tools.pop(tool_id, None)