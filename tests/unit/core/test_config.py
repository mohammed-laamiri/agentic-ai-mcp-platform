"""
Unit tests for application settings.
"""

from app.core.config import get_settings


def test_settings_include_safe_defaults(monkeypatch):
    """Settings should expose deploy-relevant defaults."""
    monkeypatch.delenv("DATABASE_URL", raising=False)
    monkeypatch.delenv("API_KEY", raising=False)
    get_settings.cache_clear()

    try:
        settings = get_settings()
        assert settings.database_url == "sqlite:///./app.db"
        assert settings.api_key == "dev-secret-key"
    finally:
        get_settings.cache_clear()


def test_settings_read_env_overrides(monkeypatch):
    """Settings should load DATABASE_URL and API_KEY from env."""
    monkeypatch.setenv("DATABASE_URL", "sqlite:///./override.db")
    monkeypatch.setenv("API_KEY", "override-key")
    get_settings.cache_clear()

    try:
        settings = get_settings()
        assert settings.database_url == "sqlite:///./override.db"
        assert settings.api_key == "override-key"
    finally:
        get_settings.cache_clear()
