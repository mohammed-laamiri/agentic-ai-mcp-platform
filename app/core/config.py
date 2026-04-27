from functools import lru_cache
from pydantic_settings import BaseSettings, SettingsConfigDict
from pydantic import Field


class Settings(BaseSettings):
    """
    Central application configuration.

    SAFE DESIGN:
    - One canonical field: api_key
    - Accepts env var: API_KEY
    - Avoids casing bugs entirely
    """

    app_name: str = "Agentic AI MCP Platform"
    environment: str = "development"

    api_prefix: str = "/api"

    host: str = "127.0.0.1"
    port: int = 8000

    database_url: str = "sqlite:///./app.db"

    # ✅ SAFE + EXPLICIT MAPPING
    api_key: str = Field(default="test", alias="API_KEY")

    aws_region: str | None = None

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=False,
        extra="ignore",
    )


@lru_cache
def get_settings() -> Settings:
    """
    Cached settings instance.
    """
    return Settings()