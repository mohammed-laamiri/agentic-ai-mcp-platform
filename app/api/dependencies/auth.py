"""
Authentication dependency for API layer.

Simple API key validation (Phase 4)
- Robust against Pydantic env naming mismatches
"""

from typing import Optional
from fastapi import Header, HTTPException, status
from app.core.config import get_settings


async def require_api_key(
    x_api_key: Optional[str] = Header(default=None, alias="X-API-Key"),
) -> str:
    """
    Validates API key from request header.

    Header:
        X-API-Key: <key>
    """

    settings = get_settings()

    # SAFE: supports both env styles (api_key / API_KEY mismatch issue)
    configured_api_key = getattr(settings, "api_key", None) or getattr(settings, "API_KEY", None)

    if not configured_api_key:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Server misconfigured: missing API key in settings",
        )

    if not x_api_key:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Missing API key",
        )

    # Clean comparison (no hidden whitespace issues)
    if x_api_key.strip() != str(configured_api_key).strip():
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid API key",
        )

    return x_api_key