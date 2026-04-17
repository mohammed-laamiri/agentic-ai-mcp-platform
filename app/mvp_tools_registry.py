"""
MVP Tool Registration.

Registers initial MVP tools at FastAPI startup.
"""

from app.services.tool_registry import ToolRegistry, ToolMetadata
from app.mvp_tools import echo_tool, sum_tool


def register_mvp_tools(registry: ToolRegistry) -> None:
    """
    Register MVP tools in the ToolRegistry instance.
    """

    # Echo tool
    registry.register_tool(
        metadata=ToolMetadata(
            tool_id="echo_tool",
            name="Echo Tool",
            version="0.1.0",
            description="Returns input as output",
        ),
        callable_fn=echo_tool,
    )

    # Sum tool
    registry.register_tool(
        metadata=ToolMetadata(
            tool_id="sum_tool",
            name="Sum Tool",
            version="0.1.0",
            description="Adds two numbers: expects 'a' and 'b'",
        ),
        callable_fn=sum_tool,
    )