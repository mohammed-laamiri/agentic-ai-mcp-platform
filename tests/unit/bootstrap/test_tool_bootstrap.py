"""
Unit tests for Tool Bootstrap.

Tests tool registration during bootstrap.
"""

import pytest


def test_bootstrap_imports():
    """Bootstrap module should be importable."""
    from app.bootstrap import tool_bootstrap

    # Module should be importable
    assert tool_bootstrap is not None


def test_bootstrap_creates_registry():
    """Bootstrap should create a tool registry."""
    from app.bootstrap.tool_bootstrap import tool_registry

    assert tool_registry is not None


def test_bootstrap_registers_echo_tool():
    """Bootstrap should register the echo tool."""
    from app.bootstrap.tool_bootstrap import tool_registry

    # Echo tool should be registered
    tool = tool_registry.get_tool("echo_tool")
    assert tool is not None
    assert tool.name == "Echo Tool"
