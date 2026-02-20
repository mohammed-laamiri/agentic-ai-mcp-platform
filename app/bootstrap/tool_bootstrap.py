"""
Tool Bootstrap

Responsible for registering all runtime tools.

This runs during app startup.
"""

from app.services.tool_registry import ToolRegistry, ToolMetadata
from app.services.tools.echo_tool import echo_tool


def register_tools(registry: ToolRegistry) -> None:
    """
    Register all available tools.
    """

    registry.register_tool(
        metadata=ToolMetadata(
            tool_id="echo",
            name="Echo Tool",
            version="1.0.0",
            description="Echoes a message and returns its length.",
            input_schema={
                "type": "object",
                "properties": {
                    "message": {
                        "type": "string"
                    }
                },
                "required": ["message"],
            },
        ),
        callable_fn=echo_tool,
    )