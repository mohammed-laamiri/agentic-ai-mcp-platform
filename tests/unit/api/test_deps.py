"""
Unit tests for API dependencies.

Tests dependency injection functions.
"""

import pytest

from app.api.deps import (
    get_app_settings,
    get_agent_service,
    get_planner_agent,
    get_tool_registry,
    get_memory_writer,
)
from app.core.config import Settings
from app.services.agent_service import AgentService
from app.services.planner_agent import PlannerAgent
from app.services.tool_registry import ToolRegistry
from app.services.memory_writer import MemoryWriter


def test_get_app_settings():
    """get_app_settings should return Settings instance."""
    settings = get_app_settings()
    assert isinstance(settings, Settings)


def test_get_app_settings_cached():
    """get_app_settings should return same instance on multiple calls."""
    settings1 = get_app_settings()
    settings2 = get_app_settings()
    assert settings1 is settings2


def test_get_agent_service():
    """get_agent_service should return AgentService instance."""
    service = get_agent_service()
    assert isinstance(service, AgentService)


def test_get_agent_service_cached():
    """get_agent_service should return same instance on multiple calls."""
    service1 = get_agent_service()
    service2 = get_agent_service()
    assert service1 is service2


def test_get_planner_agent():
    """get_planner_agent should return PlannerAgent instance."""
    planner = get_planner_agent()
    assert isinstance(planner, PlannerAgent)


def test_get_planner_agent_cached():
    """get_planner_agent should return same instance on multiple calls."""
    planner1 = get_planner_agent()
    planner2 = get_planner_agent()
    assert planner1 is planner2


def test_get_tool_registry():
    """get_tool_registry should return ToolRegistry instance."""
    registry = get_tool_registry()
    assert isinstance(registry, ToolRegistry)


def test_get_tool_registry_cached():
    """get_tool_registry should return same instance on multiple calls."""
    registry1 = get_tool_registry()
    registry2 = get_tool_registry()
    assert registry1 is registry2


def test_get_memory_writer():
    """get_memory_writer should return MemoryWriter instance."""
    writer = get_memory_writer()
    assert isinstance(writer, MemoryWriter)


def test_get_memory_writer_cached():
    """get_memory_writer should return same instance on multiple calls."""
    writer1 = get_memory_writer()
    writer2 = get_memory_writer()
    assert writer1 is writer2
