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
# Settings Class
# ==================================================
class Settings(BaseSettings):
    """
    Central application configuration.

    Loaded from environment variables or .env file.
    """

    # --------------------------------------------------
    # Application Info
    # --------------------------------------------------
    app_name: str = "Agentic AI MCP Platform"
    version: str = "0.1.0"
    environment: str = "development"  # development | staging | production

    # --------------------------------------------------
    # API / Server Settings
    # --------------------------------------------------
    api_prefix: str = "/api"
    host: str = "127.0.0.1"
    port: int = 8000

    # --------------------------------------------------
    # Database
    # --------------------------------------------------
    DATABASE_URL: str = "sqlite:///./mcp.db"

    # --------------------------------------------------
    # AWS / Bedrock (Future AI Layer)
    # --------------------------------------------------
    aws_region: str | None = None
    bedrock_model: str | None = None

    # --------------------------------------------------
    # Pydantic Settings Configuration
    # --------------------------------------------------
    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=False,
    )


# ==================================================
# Cached Singleton Settings
# ==================================================
@lru_cache
def get_settings() -> Settings:
    """
    Returns a cached Settings instance.

    Ensures:
    - Settings loaded once
    - Fast repeated access
    - Safe for entire app lifecycle
    """
    return Settings()
