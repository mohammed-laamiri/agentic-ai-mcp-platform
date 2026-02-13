# app/main.py

"""
Application entry point for the Agentic AI MCP Platform.

Responsibilities:
- Create FastAPI application instance
- Load environment-specific settings
- Register routers, middleware, and dependencies
- Provide ASGI app for Uvicorn/Gunicorn
- Initialize infrastructure layers (e.g. database)
"""

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.core.config import get_settings
from app.core.db import init_db  # <-- Step 1.2: register DB initialization

from app.api.routers import health_router, task_router
from app.api.routers.agent_router import router as agent_router
from app.api.routers.tool_router import router as tool_router


def create_app() -> FastAPI:
    """
    Application factory pattern.

    Advantages:
    - Enables easy testing with isolated app instances
    - Supports multiple environments (dev, staging, prod)
    - Avoids side effects during module import
    """
    settings = get_settings()

    app = FastAPI(
        title=settings.app_name,
        version=getattr(settings, "version", "0.1.0"),
        description="Agentic AI MCP Platform API",
    )

    # ==================================================
    # Application Lifecycle Events
    # ==================================================
    @app.on_event("startup")
    def on_startup() -> None:
        """
        Runs once when the application starts.

        Infrastructure initialization happens here.

        Today:
        - Create database tables

        Tomorrow:
        - Warm up vector stores
        - Load models
        - Register agents
        - Validate tool registry
        """
        init_db()

    # ==================================================
    # Middleware
    # ==================================================
    app.add_middleware(
        CORSMiddleware,
        allow_origins=["*"],  # TODO: Restrict in production
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )

    # ==================================================
    # Router Registration
    # ==================================================
    # Health & system status
    app.include_router(health_router, prefix="/api", tags=["Health"])
    # Task execution & management
    app.include_router(task_router, prefix="/api", tags=["Tasks"])
    # Agent management and orchestration
    app.include_router(agent_router, prefix="/api", tags=["Agents"])
    # Tool registry and execution endpoints
    app.include_router(tool_router, prefix="/api", tags=["Tools"])

    return app


# ==================================================
# ASGI app instance
# ==================================================
# This is the app Uvicorn or Gunicorn will run
app = create_app()
