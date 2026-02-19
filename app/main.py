# app/main.py

"""
Application entry point for the Agentic AI MCP Platform.
"""

from contextlib import asynccontextmanager
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.core.config import get_settings
from app.core.db import init_db

# Routers
from app.api.routers import health_router, task_router
from app.api.routers.agent_router import router as agent_router
from app.api.routers.tool_router import router as tool_router


# ==================================================
# Lifespan
# ==================================================
@asynccontextmanager
async def lifespan(app: FastAPI):
    """
    Application startup and shutdown lifecycle.
    """
    # Initialize database here
    init_db()
    yield
    # Place for shutdown tasks if needed


# ==================================================
# App Factory
# ==================================================
def create_app() -> FastAPI:
    settings = get_settings()

    app = FastAPI(
        title=settings.app_name,
        version=getattr(settings, "version", "0.1.0"),
        description="Agentic AI MCP Platform API",
        lifespan=lifespan,
    )

    # CORS middleware
    app.add_middleware(
        CORSMiddleware,
        allow_origins=["*"],  # Restrict in production
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )

    # API prefix
    API_PREFIX = "/api"

    # Include routers
    app.include_router(health_router, prefix=API_PREFIX, tags=["Health"])
    app.include_router(task_router, prefix=f"{API_PREFIX}/tasks", tags=["Tasks"])
    app.include_router(agent_router, prefix=f"{API_PREFIX}/agents", tags=["Agents"])
    app.include_router(tool_router, prefix=f"{API_PREFIX}/tools", tags=["Tools"])

    return app


# ==================================================
# ASGI App
# ==================================================
app = create_app()
