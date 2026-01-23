from fastapi import FastAPI

from app.core.config import get_settings
from app.api.routers import health


def create_app() -> FastAPI:
    settings = get_settings()

    app = FastAPI(
        title=settings.app_name,
        version="0.1.0",
    )

    app.include_router(health.router, prefix="/api")

    return app


app = create_app()
