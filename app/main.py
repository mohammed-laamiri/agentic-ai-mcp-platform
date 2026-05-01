"""
Application entry point.

Responsible for:
- Creating the FastAPI application instance
- Loading configuration
- Registering routers and middleware
"""

from fastapi import FastAPI
from fastapi.responses import JSONResponse
from fastapi.middleware.cors import CORSMiddleware

# Centralized settings
from app.core.config import get_settings

# Logging
from app.core.logging import configure_logging
from app.api.middleware.correlation import CorrelationIdMiddleware

# Rate limiting
from slowapi.errors import RateLimitExceeded
from slowapi.middleware import SlowAPIMiddleware
from app.api.rate_limit import limiter

# Routers
from app.api.routers import health_router, task_router
from app.api.routers.agent_router import router as agent_router
from app.api.routers.tool_router import router as tool_router
from app.api.routers.rag_router import router as rag_router
from app.api.routers.demo_router import router as demo_router
from app.api.routers.execution_router import router as execution_router
from app.api.routers.streaming import router as streaming_router

# Runtime init (important side effects)
from app.runtime.runtime import tool_registry, tool_execution_engine


configure_logging()


def create_app() -> FastAPI:
    settings = get_settings()

    app = FastAPI(
        title=settings.app_name,
        version="0.1.0",
        description="Agentic AI MCP Platform API",
    )

    # ------------------------------
    # ✅ CORS (CRITICAL FIX FOR DJANGO FRONTEND)
    # ------------------------------
    app.add_middleware(
        CORSMiddleware,
        allow_origins=[
            "http://127.0.0.1:8001",
            "http://localhost:8001",
        ],
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )

    # ------------------------------
    # Middleware
    # ------------------------------
    app.add_middleware(CorrelationIdMiddleware)

    app.state.limiter = limiter
    app.add_middleware(SlowAPIMiddleware)

    @app.exception_handler(RateLimitExceeded)
    async def rate_limit_handler(request, exc):
        return JSONResponse(
            status_code=429,
            content={"detail": "Rate limit exceeded. Try again later."},
        )

    # ------------------------------
    # Root
    # ------------------------------
    @app.get("/")
    def root():
        return {
            "message": "Agentic AI MCP Platform API is running",
            "docs": "/docs",
            "health": "/api/health",
        }

    # ------------------------------
    # ROUTES (CLEAN & CONSISTENT)
    # ------------------------------
    app.include_router(health_router, prefix="/api", tags=["Health"])
    app.include_router(task_router, prefix="/api/tasks", tags=["Tasks"])
    app.include_router(agent_router, prefix="/api", tags=["Agents"])
    app.include_router(rag_router, prefix="/api", tags=["RAG"])
    app.include_router(tool_router, prefix="/api", tags=["Tools"])
    app.include_router(demo_router, prefix="/api", tags=["Demo"])

    # Execution routes
    app.include_router(execution_router, prefix="/api", tags=["Execution"])

    # Streaming routes
    app.include_router(streaming_router, prefix="/api", tags=["Streaming"])

    return app


app = create_app()