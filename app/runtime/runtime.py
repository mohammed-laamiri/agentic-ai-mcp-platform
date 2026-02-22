"""
Application runtime singletons.

This module owns long-lived runtime objects.

WHY this exists:
- Prevent circular imports
- Provide singleton services
- Central place for runtime wiring

DO NOT put FastAPI app here.
DO NOT put routers here.
"""

from app.services.tool_registry import ToolRegistry, ToolMetadata
from app.services.tool_execution_engine import ToolExecutionEngine


# ==========================================================
# Tool Registry Singleton
# ==========================================================

tool_registry = ToolRegistry()


# ==========================================================
# Tool Execution Engine Singleton
# ==========================================================

tool_execution_engine = ToolExecutionEngine(tool_registry)


# ==========================================================
# Register MVP tools
# ==========================================================

def _echo_tool(**kwargs):
    """Simple MVP tool."""
    return kwargs


tool_registry.register_tool(
    metadata=ToolMetadata(
        tool_id="echo",
        name="Echo Tool",
        version="1.0.0",
        description="Returns input arguments",
        input_schema=None,
    ),
    callable_fn=_echo_tool,
)