from functools import lru_cache
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    """
    Central application configuration.

    Loaded from environment variables and .env file.
    """

    app_name: str = "Agentic AI MCP Platform"
    environment: str = "development"

    # API
    api_prefix: str = "/api"

    # Server
    host: str = "127.0.0.1"
    port: int = 8000

    # AWS / Bedrock (placeholders for later)
    aws_region: str | None = None

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=False,
    )


@lru_cache
def get_settings() -> Settings:
    """
    Cached settings instance.
    Ensures settings are loaded only once.
    """
    return Settings()
