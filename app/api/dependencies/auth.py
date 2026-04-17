"""
Authentication dependency for API layer.

This module is intentionally isolated at the API boundary.
It must NOT be imported inside domain or service layers.

Phase 4 scope:
- Simple API key validation
- Replaceable later with JWT or OAuth
"""

from typing import Optional

from fastapi import Header, HTTPException, status

from app.core.config import get_settings


# Temporary development default.
# Production should override this through environment variables.
DEV_API_KEY = "dev-secret-key"


async def require_api_key(
    x_api_key: Optional[str] = Header(default=None),
) -> str:
    """
    FastAPI dependency that validates the X-API-Key header.

    - Executed before route handler
    - Raises 401 if invalid
    - Returns the validated key otherwise

    This keeps authentication logic outside business logic.
    """

    configured_api_key = get_settings().api_key

    # Reject if header is missing or incorrect
    if x_api_key != configured_api_key:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid or missing API key",
        )

    # Return key for potential future use
    return x_api_key
