"""
Middleware to inject correlation ID per request.

- Ensures all logs can access correlation_id via contextvar
- Response includes X-Correlation-ID for tracing
"""

import uuid
from fastapi import Request
from starlette.middleware.base import BaseHTTPMiddleware

from app.core.logging import correlation_id_ctx


class CorrelationIdMiddleware(BaseHTTPMiddleware):
    """
    Middleware to set correlation_id in ContextVar for each request.
    """

    async def dispatch(self, request: Request, call_next):
        # Extract from header or generate new UUID
        correlation_id = request.headers.get("X-Correlation-ID", str(uuid.uuid4()))

        # Store in ContextVar (used by logging filter)
        correlation_id_ctx.set(correlation_id)

        # Call downstream route handler
        response = await call_next(request)

        # Add correlation_id to response headers for tracing
        response.headers["X-Correlation-ID"] = correlation_id

        return response