"""
Tool registration bootstrap.
"""

from app.services.tool_registry import ToolRegistry, ToolMetadata
from app.services.tools.echo_tool import echo_tool


def register_tools(tool_registry: ToolRegistry) -> None:
    """
    Register all system tools.
    """

    tool_registry.register_tool(
        metadata=ToolMetadata(
            tool_id="echo_tool",
            name="Echo Tool",
            version="1.0",
            description="Returns the same text",
            input_schema={
                "type": "object",
                "properties": {
                    "text": {"type": "string"},
                },
                "required": ["text"],
            },
        ),
        callable_fn=echo_tool,
    )