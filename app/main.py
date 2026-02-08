# app/main.py

"""
Application entry point.

- Creates FastAPI instance
- Loads settings
- Registers routers & middleware
"""

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.core.config import get_settings
from app.api.routers import health_router, task_router
from app.api.routers.agent_router import router as agent_router
from app.api.routers.tool_router import router as tool_router


def create_app() -> FastAPI:
    """
    Application factory.

    Benefits:
    - Easier testing
    - Different configs per environment
    - No side effects at import
    """
    settings = get_settings()

    app = FastAPI(
        title=settings.app_name,
        version=settings.version if hasattr(settings, "version") else "0.1.0",
        description="Agentic AI MCP Platform API",
    )

    # ----------------------------
    # CORS middleware
    # ----------------------------
    app.add_middleware(
        CORSMiddleware,
        allow_origins=["*"],  # restrict in production
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )

    # ----------------------------
    # Router Registration
    # ----------------------------
    app.include_router(health_router, prefix="/api", tags=["Health"])
    app.include_router(task_router, prefix="/api", tags=["Tasks"])
    app.include_router(agent_router, prefix="/api", tags=["Agent"])
    app.include_router(tool_router, prefix="/api", tags=["Tools"])

    return app


# ASGI app instance
app = create_app()
