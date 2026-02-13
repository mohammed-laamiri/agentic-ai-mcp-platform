# app/core/config.py

"""
Application configuration for Agentic AI MCP Platform.

Responsibilities:
- Centralized settings management
- Environment-specific configuration
- Supports .env file and environment variable overrides
- Provides cached singleton for performance
"""

from functools import lru_cache
from pydantic_settings import BaseSettings, SettingsConfigDict


# ==================================================
# Default database URL (SQLite local DB)
# ==================================================
database_url: str = "sqlite:///./mcp.db"


# ==================================================
# Settings class
# ==================================================
class Settings(BaseSettings):
    """
    Central application configuration.

    Loaded from environment variables or .env file.
    """

    # --------------------------------------------------
    # Application info
    # --------------------------------------------------
    app_name: str = "Agentic AI MCP Platform"
    environment: str = "development"  # dev, staging, prod

    # --------------------------------------------------
    # API / Server settings
    # --------------------------------------------------
    api_prefix: str = "/api"
    host: str = "127.0.0.1"
    port: int = 8000

    # --------------------------------------------------
    # Database
    # --------------------------------------------------
    database_url: str = database_url

    # --------------------------------------------------
    # AWS / Bedrock placeholders (future AI layer)
    # --------------------------------------------------
    aws_region: str | None = None
    bedrock_model: str | None = None

    # --------------------------------------------------
    # Pydantic Settings config
    # --------------------------------------------------
    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=False,
    )


# ==================================================
# Cached settings instance
# ==================================================
@lru_cache
def get_settings() -> Settings:
    """
    Returns a singleton Settings instance.

    Caching ensures settings are loaded only once per application lifecycle.
    """
    return Settings()
