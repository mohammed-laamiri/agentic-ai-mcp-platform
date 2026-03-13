"""
Unit tests for register_tools.

Tests tool registration function.
"""

from app.services.tool_registry import ToolRegistry
from app.services.tools.register_tools import register_tools


def test_register_tools_registers_echo_tool():
    """register_tools should register the echo tool."""
    registry = ToolRegistry()

    register_tools(registry)

    tool = registry.get_tool("echo_tool")
    assert tool is not None
    assert tool.name == "Echo Tool"


def test_register_tools_binds_executor():
    """register_tools should bind executor for echo tool."""
    registry = ToolRegistry()

    register_tools(registry)

    executor = registry.get_executor("echo_tool")
    assert executor is not None

    # Test the executor works
    result = executor(message="hello")
    assert result["echo"] == "hello"
