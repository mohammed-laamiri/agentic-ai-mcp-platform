"""
Unit tests for Echo Tool.

Tests the echo tool functionality.
"""

from app.services.tools.echo_tool import echo_tool


def test_echo_tool_returns_message():
    """echo_tool should return the input message."""
    result = echo_tool("Hello World")

    assert result["echo"] == "Hello World"


def test_echo_tool_returns_length():
    """echo_tool should return the message length."""
    result = echo_tool("Hello")

    assert result["length"] == 5


def test_echo_tool_empty_message():
    """echo_tool should handle empty messages."""
    result = echo_tool("")

    assert result["echo"] == ""
    assert result["length"] == 0


def test_echo_tool_unicode():
    """echo_tool should handle unicode characters."""
    result = echo_tool("Hello 世界")

    assert result["echo"] == "Hello 世界"
    assert result["length"] == 8
