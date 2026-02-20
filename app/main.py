"""
Application entry point.

Responsible for:
- Creating the FastAPI application instance
- Loading configuration
- Registering routers and middleware
"""

from fastapi import FastAPI

# Centralized application settings
from app.core.config import get_settings

# Routers
from app.api.routers import health_router, task_router
from app.api.routers.agent_router import router as agent_router
from app.api.routers.tool_router import router as tool_router

# -------------------------
# Tool runtime singletons
# -------------------------
from app.services.tool_registry import ToolRegistry, ToolMetadata
from app.services.tool_execution_engine import ToolExecutionEngine

tool_registry = ToolRegistry()
tool_execution_engine = ToolExecutionEngine(tool_registry)

# Register first real tool
tool_registry.register_tool(
    ToolMetadata(
        tool_id="echo",
        name="Echo Tool",
        version="1.0.0",
        description="Returns input arguments as output",
    )
)


def create_app() -> FastAPI:
    """
    Application factory.
    """
    settings = get_settings()
    app = FastAPI(
        title=settings.app_name,
        version="0.1.0",
        description="Agentic AI MCP Platform API",
    )

    # Router registration
    app.include_router(health_router, prefix="/api", tags=["Health"])
    app.include_router(task_router, prefix="/api", tags=["Tasks"])
    app.include_router(agent_router, prefix="/api", tags=["Agent"])
    app.include_router(tool_router, prefix="/api", tags=["Tools"])

    return app


# ASGI app
app = create_app()