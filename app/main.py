"""
Application entry point.

Responsible for:
- Creating the FastAPI application instance
- Loading configuration
- Registering routers and middleware

Phase 4 implemented:
- Auth layer applied at route level
- Correlation IDs & logging configured
- Rate limiting middleware registered
"""

from fastapi import FastAPI
from fastapi.responses import JSONResponse

# Centralized settings
from app.core.config import get_settings

# Logging & observability (Phase 4.2)
from app.core.logging import configure_logging
from app.api.middleware.correlation import CorrelationIdMiddleware

# Rate limiting (Phase 4.3)
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

# Runtime singletons (tool registry, execution engine)
from app.runtime import runtime  # noqa: F401


def create_app() -> FastAPI:
    """
    Application factory.

    - Registers routers
    - Configures logging & correlation ID middleware
    - Registers rate limiting middleware and exception handler
    """
    settings = get_settings()

    app = FastAPI(
        title=settings.app_name,
        version="0.1.0",
        description="Agentic AI MCP Platform API",
    )

    # ------------------------------
    # Phase 4.2 — Logging
    # ------------------------------
    configure_logging()

    # ------------------------------
    # Phase 4.2 — Correlation ID middleware
    # ------------------------------
    app.add_middleware(CorrelationIdMiddleware)

    # ------------------------------
    # Phase 4.3 — Rate limiting
    # ------------------------------
    app.state.limiter = limiter
    app.add_middleware(SlowAPIMiddleware)

    @app.exception_handler(RateLimitExceeded)
    async def rate_limit_exceeded_handler(request, exc):
        """
        Returns 429 when rate limit is exceeded.
        """
        return JSONResponse(
            status_code=429,
            content={"detail": "Rate limit exceeded. Try again later."},
        )

    # ------------------------------
    # Router registration
    # ------------------------------
    app.include_router(health_router, prefix="/api", tags=["Health"])
    app.include_router(task_router, prefix="/api/tasks", tags=["Tasks"])
    app.include_router(agent_router, prefix="/api", tags=["Agent"])
    app.include_router(rag_router, prefix="/api", tags=["RAG"])
    app.include_router(tool_router, prefix="/api", tags=["Tools"])
    app.include_router(demo_router, prefix="/api", tags=["Demo"])
    app.include_router(execution_router)
    app.include_router(streaming_router, prefix="/api")

    return app


# ASGI app instance
app = create_app()