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
- This registry is a runtime dependency, not a domain model

Future replacements:
- DynamoDB / Postgres
- MCP-compatible tool index
"""

from dataclasses import dataclass
from typing import Dict, Optional, List


@dataclass(frozen=True)
class ToolMetadata:
    """
    Immutable tool metadata contract.

    This object is SAFE to share across:
    - PlannerAgent
    - Orchestrator
    - Execution runtimes

    Future extensions (NOT implemented):
    - Input / output JSON schema
    - Cost estimation
    - Rate limits
    - Required permissions
    - Tool owner
    - Tool category (llm, api, db, retrieval, etc.)
    """

    tool_id: str
    name: str
    version: str
    description: str


class ToolRegistry:
    """
    In-memory tool registry.

    Architectural role:
    - Acts as the source of truth for tool metadata
    - Enables planners to reason about available tools
    - Enables executors to validate tool existence

    This registry is intentionally:
    - Stateless across restarts
    - Fast
    - Replaceable
    """

    def __init__(self) -> None:
        self._tools: Dict[str, ToolMetadata] = {}

    # --------------------------------------------------
    # Registration
    # --------------------------------------------------

    def register_tool(self, metadata: ToolMetadata) -> None:
        """
        Register or update a tool definition.

        Behavior:
        - If tool_id exists → replaced
        - If tool_id is new → inserted
        """
        self._tools[metadata.tool_id] = metadata

    # --------------------------------------------------
    # Retrieval
    # --------------------------------------------------

    def get_tool(self, tool_id: str) -> Optional[ToolMetadata]:
        """
        Retrieve tool metadata by tool ID.

        Returns:
        - ToolMetadata if found
        - None if tool does not exist
        """
        return self._tools.get(tool_id)

    def list_tools(self) -> List[ToolMetadata]:
        """
        List all registered tools.

        Order is NOT guaranteed.
        """
        return list(self._tools.values())

    def has_tool(self, tool_id: str) -> bool:
        """
        Check whether a tool exists in the registry.
        """
        return tool_id in self._tools

    # --------------------------------------------------
    # Removal
    # --------------------------------------------------

    def remove_tool(self, tool_id: str) -> None:
        """
        Remove a tool from the registry.

        Silent if tool does not exist.
        """
        self._tools.pop(tool_id, None)
