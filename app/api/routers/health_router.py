from fastapi import APIRouter, Depends
from app.api.deps import get_app_settings
from app.core.config import Settings

router = APIRouter(tags=["system"])


@router.get("/health")
async def health_check(settings: Settings = Depends(get_app_settings)) -> dict:
    """
    Health check endpoint.
    """
    return {
        "status": "ok",
        "environment": settings.environment,
    }
