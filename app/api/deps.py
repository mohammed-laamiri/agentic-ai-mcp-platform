#centralizes shared dependencies (settings, db, agent context later)

from app.core.config import get_settings
from app.core.config import Settings


def get_app_settings() -> Settings:
    """
    Dependency to inject application settings.
    """
    return get_settings()
