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

    Includes:
    - input_schema: JSON-schema-like validation contract
    - version: semantic versioning
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

        # Metadata store: tool_id -> ToolMetadata
        self._tools: Dict[str, ToolMetadata] = {}

        # Callable binding store: tool_id -> Callable
        self._callables: Dict[str, Callable[..., Any]] = {}

    # --------------------------------------------------
    # Registration
    # --------------------------------------------------

    def register_tool(
        self,
        metadata: ToolMetadata,
        callable_fn: Optional[Callable[..., Any]] = None,
        overwrite: bool = False,
    ) -> None:
        """
        Register or update a tool.

        callable_fn is optional to support metadata-only registration.

        overwrite: if False, prevents accidental overwriting of existing versions.
        """

        existing = self._tools.get(metadata.tool_id)

        if existing and not overwrite:
            if existing.version == metadata.version:
                raise ValueError(
                    f"Tool '{metadata.tool_id}' already registered with version {metadata.version}"
                )

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