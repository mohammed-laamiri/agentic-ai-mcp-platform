"""
Tool Bootstrap

Responsible for registering all runtime tools.

This runs during app startup.
"""

from app.services.tool_registry import ToolRegistry, ToolMetadata
from app.services.tools.echo_tool import echo_tool

tool_registry = ToolRegistry()

# Register echo tool
tool_registry.register_tool(
    metadata=ToolMetadata(
        tool_id="echo_tool",
        name="Echo Tool",
        version="1.0",
        description="Simply echoes the message back",
        input_schema={"message": "str"}
    ),
    callable_fn=echo_tool,
)