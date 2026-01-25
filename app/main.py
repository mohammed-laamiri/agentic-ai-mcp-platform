"""
Application entry point.

This module is responsible for:
- Creating the FastAPI application instance
- Loading configuration
- Registering routers and middleware

IMPORTANT:
- No business logic lives here
- No service instantiation happens here
- This file should stay thin and declarative
"""

from fastapi import FastAPI

# Centralized application settings (Pydantic Settings)
from app.core.config import get_settings

# API routers
from app.api.routers import health_router, task_router
from app.api.routers.agent_router import router as agent_router


def create_app() -> FastAPI:
    """
    Application factory.

    Why we use an app factory:
    - Allows easier testing
    - Enables different configs per environment
    - Prevents side effects at import time
    """
    settings = get_settings()

    app = FastAPI(
        title=settings.app_name,
        version="0.1.0",
        description="Agentic AI MCP Platform API",
    )

    # -------------------------
    # Router Registration
    # -------------------------

    # Health check endpoints
    # Used by:
    # - Load balancers
    # - Monitoring systems
    # - CI/CD smoke tests
    app.include_router(
        health_router,
        prefix="/api",
        tags=["Health"],
    )

    # Task execution endpoints
    # This is the first real business-facing API
    app.include_router(
        task_router,
        prefix="/api",
        tags=["Tasks"],
    )

    # Agent execution endpoint
    app.include_router(
        agent_router,
        prefix="/api",
        tags=["Agent"],
    )


    return app


# ASGI application instance
# This is what Uvicorn / Gunicorn will load
app = create_app()
