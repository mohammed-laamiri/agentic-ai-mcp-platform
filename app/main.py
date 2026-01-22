from fastapi import FastAPI
from app.core.config import get_settings


def create_app() -> FastAPI:
    settings = get_settings()

    app = FastAPI(
        title=settings.app_name,
        version="0.1.0",
    )

    """
    Application factory.

    This pattern allows:
    - Easier testing
    - Cleaner configuration
    - Future scalability (background workers, CLI, etc.)
    """
    app = FastAPI(
        title="Agentic AI MCP Platform",
        version="0.1.0",
    )

    @app.get("/health", tags=["system"])
    async def health_check() -> dict[str, str]:
        """
        Basic health check endpoint.
        Used by monitoring, CI, and load balancers.
        """
        return {"status": "ok"}

    return app


app = create_app()
