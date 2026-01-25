from typing import Callable, Dict


class ToolRegistry:
    """
    Registry for MCP tools.

    This is intentionally minimal for now.
    Tools will be registered with metadata later.
    """

    def __init__(self) -> None:
        self._tools: Dict[str, Callable] = {}

    def register(self, name: str, tool: Callable) -> None:
        self._tools[name] = tool

    def get(self, name: str) -> Callable:
        if name not in self._tools:
            raise KeyError(f"Tool '{name}' not found")
        return self._tools[name]
