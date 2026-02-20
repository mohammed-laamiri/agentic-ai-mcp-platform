"""
Tool Registry.

Runtime registry responsible for:
- Tool metadata registration
- Discovery by agents and planners
- Version awareness
- Validation boundaries

IMPORTANT:
- This registry does NOT execute tools
- This registry does NOT enforce permissions (yet)

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

    SAFE to share across planner, orchestrator, and execution layers.

    New:
    - input_schema: JSON-schema-like validation contract
    """

    tool_id: str
    name: str
    version: str
    description: str

    # NEW — argument validation schema
    input_schema: Optional[Dict[str, Any]] = None


class ToolRegistry:
    """
    In-memory tool registry.

    Source of truth for:
    - Tool metadata
    - Tool callable binding
    - Tool validation schema
    """

    def __init__(self) -> None:

        # Metadata store
        self._tools: Dict[str, ToolMetadata] = {}

        # Callable binding store
        self._callables: Dict[str, Callable[..., Any]] = {}

    # --------------------------------------------------
    # Registration
    # --------------------------------------------------

    def register_tool(
        self,
        metadata: ToolMetadata,
        callable_fn: Optional[Callable[..., Any]] = None,
    ) -> None:
        """
        Register or update a tool.

        callable_fn is optional to support metadata-only registration.
        """

        self._tools[metadata.tool_id] = metadata

        if callable_fn:
            self._callables[metadata.tool_id] = callable_fn

    # --------------------------------------------------
    # Retrieval
    # --------------------------------------------------

    def get_tool(self, tool_id: str) -> Optional[ToolMetadata]:
        return self._tools.get(tool_id)

    def get_callable(self, tool_id: str) -> Optional[Callable[..., Any]]:
        return self._callables.get(tool_id)

    def get_input_schema(self, tool_id: str) -> Optional[Dict[str, Any]]:
        tool = self._tools.get(tool_id)
        return tool.input_schema if tool else None

    def list_tools(self) -> List[ToolMetadata]:
        return list(self._tools.values())

    def has_tool(self, tool_id: str) -> bool:
        return tool_id in self._tools

    # --------------------------------------------------
    # Removal
    # --------------------------------------------------

    def remove_tool(self, tool_id: str) -> None:

        self._tools.pop(tool_id, None)
        self._callables.pop(tool_id, None)