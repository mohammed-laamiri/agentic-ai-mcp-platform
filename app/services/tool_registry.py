"""
Tool Registry (MCP Upgrade).

Responsibilities:
- Tool metadata registration & versioning
- Executor binding (MCP-compliant)
- Discovery by planners and executors
- Validation boundaries
- Optional future enhancements: permissions, rate limits, cost tracking
"""

from dataclasses import dataclass
from typing import Dict, Optional, Callable, List, Any


@dataclass(frozen=True)
class ToolMetadata:
    """
    Immutable tool metadata contract.

    Safe to share across:
    - PlannerAgent
    - Orchestrator
    - Execution runtimes

    Future extensions:
    - Input/output schema
    - Cost estimation
    - Rate limits
    - Permissions
    - Tool owner
    - Tool category
    """
    tool_id: str
    name: str
    version: str
    description: str


class ToolRegistry:
    """
    In-memory tool registry with MCP binding.

    Architectural role:
    - Source of truth for tool metadata
    - Registers executor functions for tools
    - Supports planners and execution engines
    """

    def __init__(self) -> None:
        self._tools: Dict[str, ToolMetadata] = {}
        self._executors: Dict[str, Callable[..., Any]] = {}

    # --------------------------------------------------
    # Metadata Registration
    # --------------------------------------------------

    def register_tool(self, metadata: ToolMetadata, executor: Optional[Callable[..., Any]] = None) -> None:
        """
        Register a tool metadata and optionally bind an executor.

        Behavior:
        - If tool_id exists → replaced
        - If tool_id is new → inserted
        """
        self._tools[metadata.tool_id] = metadata
        if executor:
            self._executors[metadata.tool_id] = executor

    # --------------------------------------------------
    # Executor Binding
    # --------------------------------------------------

    def bind_executor(self, tool_id: str, executor: Callable[..., Any]) -> None:
        """
        Bind or update an executor for a registered tool.
        """
        if tool_id not in self._tools:
            raise ValueError(f"Cannot bind executor: Tool '{tool_id}' not registered")
        self._executors[tool_id] = executor

    def get_executor(self, tool_id: str) -> Optional[Callable[..., Any]]:
        """
        Retrieve the executor callable for a given tool ID.
        """
        return self._executors.get(tool_id)

    # --------------------------------------------------
    # Retrieval
    # --------------------------------------------------

    def get_tool(self, tool_id: str) -> Optional[ToolMetadata]:
        return self._tools.get(tool_id)

    def list_tools(self) -> List[ToolMetadata]:
        return list(self._tools.values())

    def has_tool(self, tool_id: str) -> bool:
        return tool_id in self._tools

    # --------------------------------------------------
    # Removal
    # --------------------------------------------------

    def remove_tool(self, tool_id: str) -> None:
        self._tools.pop(tool_id, None)
        self._executors.pop(tool_id, None)
