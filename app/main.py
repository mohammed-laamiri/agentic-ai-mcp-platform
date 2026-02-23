"""
Application entry point.

Responsible for:
- Creating the FastAPI application instance
- Loading configuration
- Registering routers and middleware

IMPORTANT:
- Does NOT create runtime singletons
- Runtime lives in app.runtime.runtime to prevent circular imports
"""

from fastapi import FastAPI

# Centralized application settings
from app.core.config import get_settings

# Routers
from app.api.routers import health_router, task_router
from app.api.routers.agent_router import router as agent_router
from app.api.routers.tool_router import router as tool_router
from app.api.routers.rag_router import router as rag_router
from app.api.routers.demo_router import router as demo_router

# IMPORTANT:
# This initializes runtime singletons (tool_registry, tool_execution_engine, etc.)
# without creating circular imports.
from app.runtime import runtime  # noqa: F401


def create_app() -> FastAPI:
    """
    Application factory.

    Why this pattern:
    - Prevents side effects at import time
    - Enables testing environments
    - Enables production deployment flexibility
    """

    settings = get_settings()

    app = FastAPI(
        title=settings.app_name,
        version="0.1.0",
        description="Agentic AI MCP Platform API",
    )

    # ==========================================================
    # Router registration
    # ==========================================================

    app.include_router(
        health_router,
        prefix="/api",
        tags=["Health"],
    )

    app.include_router(
        task_router,
        prefix="/api",
        tags=["Tasks"],
    )

    app.include_router(
        agent_router,
        prefix="/api",
        tags=["Agent"],
    )

    app.include_router(
        rag_router, 
        prefix="/api", 
        tags=["RAG"]
    )

    app.include_router(
        tool_router,
        prefix="/api",
        tags=["Tools"],
    )

    app.include_router(
        demo_router,
        prefix="/api",
        tags=["Demo"],
    )

    return app


# ASGI application instance (used by Uvicorn)
app = create_app()