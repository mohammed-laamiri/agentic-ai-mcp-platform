from functools import lru_cache
from pydantic import model_validator
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

    # Infrastructure
    database_url: str = "sqlite:///./app.db"
    api_key: str = "dev-secret-key"

    # AWS / Bedrock (placeholders for later)
    aws_region: str | None = None

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=False,
    )

    @model_validator(mode="after")
    def validate_production_secrets(self) -> "Settings":
        if self.environment == "production" and self.api_key == "dev-secret-key":
            raise ValueError("API_KEY must be set to a secure value in production")
        # Heroku injects postgres:// but SQLAlchemy 2.x requires postgresql://
        if self.database_url.startswith("postgres://"):
            self.database_url = self.database_url.replace("postgres://", "postgresql://", 1)
        return self


@lru_cache
def get_settings() -> Settings:
    """
    Cached settings instance.
    Ensures settings are loaded only once.
    """
    return Settings()
