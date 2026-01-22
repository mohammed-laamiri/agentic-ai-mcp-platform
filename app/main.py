from fastapi import FastAPI


def create_app() -> FastAPI:
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
