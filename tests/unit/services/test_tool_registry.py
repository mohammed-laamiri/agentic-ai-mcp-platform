"""
Unit tests for ToolRegistry.

These tests validate:
- Tool registration
- Retrieval
- Listing

No mocks are used.
"""

from app.services.tool_registry import ToolRegistry
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
