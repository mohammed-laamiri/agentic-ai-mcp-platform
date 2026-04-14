"""
Unit tests for authentication dependency.
"""

import pytest
from fastapi import HTTPException

from app.api.dependencies.auth import require_api_key, DEV_API_KEY
from app.core.config import get_settings


async def test_require_api_key_valid():
    """Valid API key should return the key."""
    result = await require_api_key(x_api_key=DEV_API_KEY)
    assert result == DEV_API_KEY


async def test_require_api_key_invalid():
    """Invalid API key should raise 401."""
    with pytest.raises(HTTPException) as exc_info:
        await require_api_key(x_api_key="wrong-key")

    assert exc_info.value.status_code == 401
    assert "Invalid or missing API key" in exc_info.value.detail


async def test_require_api_key_missing():
    """Missing API key should raise 401."""
    with pytest.raises(HTTPException) as exc_info:
        await require_api_key(x_api_key=None)

    assert exc_info.value.status_code == 401
    assert "Invalid or missing API key" in exc_info.value.detail


async def test_require_api_key_empty():
    """Empty API key should raise 401."""
    with pytest.raises(HTTPException) as exc_info:
        await require_api_key(x_api_key="")

    assert exc_info.value.status_code == 401


async def test_require_api_key_uses_env_override(monkeypatch):
    """Configured API key should come from environment settings."""
    monkeypatch.setenv("API_KEY", "prod-key")
    get_settings.cache_clear()

    try:
        result = await require_api_key(x_api_key="prod-key")
        assert result == "prod-key"
    finally:
        get_settings.cache_clear()
