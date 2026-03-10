"""
Unit tests for ToolRegistry.

These tests validate:
- Tool registration
- Retrieval
- Listing
- Executor binding
- Removal

No mocks are used.
"""

import pytest

from app.services.tool_registry import ToolRegistry, ToolMetadata
from app.schemas.tool import ToolCreate


def test_register_and_get_tool():
    registry = ToolRegistry()

    tool = ToolCreate(
        tool_id="search",
        name="Search Tool",
        version="1.0",
        description="Performs web searches",
    )

    registry.register_tool(tool)

    stored = registry.get_tool("search")

    assert stored is not None
    assert stored.tool_id == "search"
    assert stored.name == "Search Tool"
    assert stored.version == "1.0"


def test_register_tool_overwrites_existing():
    registry = ToolRegistry()

    tool_v1 = ToolCreate(
        tool_id="search",
        name="Search Tool",
        version="1.0",
        description="Initial version",
    )

    tool_v2 = ToolCreate(
        tool_id="search",
        name="Search Tool",
        version="2.0",
        description="Updated version",
    )

    registry.register_tool(tool_v1)
    registry.register_tool(tool_v2)

    stored = registry.get_tool("search")

    assert stored.version == "2.0"
    assert stored.description == "Updated version"


def test_list_tools():
    registry = ToolRegistry()

    tool1 = ToolCreate(
        tool_id="search",
        name="Search Tool",
        version="1.0",
        description="Search",
    )

    tool2 = ToolCreate(
        tool_id="calculator",
        name="Calculator Tool",
        version="1.0",
        description="Math operations",
    )

    registry.register_tool(tool1)
    registry.register_tool(tool2)

    tools = registry.list_tools()

    assert len(tools) == 2
    tool_ids = {t.tool_id for t in tools}
    assert tool_ids == {"search", "calculator"}


def test_bind_executor():
    """bind_executor attaches an executor to a registered tool."""
    registry = ToolRegistry()
    meta = ToolMetadata(tool_id="x", name="X", version="1.0", description="X")
    registry.register_tool(meta)
    registry.bind_executor("x", lambda a, b: a + b)
    fn = registry.get_executor("x")
    assert fn is not None
    assert fn(1, 2) == 3


def test_bind_executor_raises_when_tool_not_registered():
    """bind_executor raises ValueError when tool_id is not registered."""
    registry = ToolRegistry()
    with pytest.raises(ValueError, match="not registered"):
        registry.bind_executor("missing", lambda: None)


def test_get_executor_returns_none_when_not_bound():
    """get_executor returns None when no executor was bound."""
    registry = ToolRegistry()
    meta = ToolMetadata(tool_id="y", name="Y", version="1.0", description="Y")
    registry.register_tool(meta)
    assert registry.get_executor("y") is None


def test_has_tool():
    """has_tool returns True for registered tool, False otherwise."""
    registry = ToolRegistry()
    registry.register_tool(
        ToolCreate(tool_id="z", name="Z", version="1.0", description="Z")
    )
    assert registry.has_tool("z") is True
    assert registry.has_tool("missing") is False


def test_remove_tool():
    """remove_tool removes metadata and executor."""
    registry = ToolRegistry()
    meta = ToolMetadata(tool_id="r", name="R", version="1.0", description="R")
    registry.register_tool(meta)
    registry.bind_executor("r", lambda: None)
    registry.remove_tool("r")
    assert registry.has_tool("r") is False
    assert registry.get_executor("r") is None
