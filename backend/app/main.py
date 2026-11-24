"""FastAPI application entry point."""

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from .api.health import router as health_router
from .api.components import router as components_router
from .api.compatibility import router as compatibility_router
from .config import Settings


def create_app(settings: Settings | None = None) -> FastAPI:
    """Create and configure the FastAPI application."""
    runtime_settings = settings or Settings.from_environment()
    application = FastAPI(title=runtime_settings.app_name)

    application.add_middleware(
        CORSMiddleware,
        allow_origins=runtime_settings.frontend_origins,
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )
    application.include_router(
        health_router,
        prefix=runtime_settings.api_v1_prefix,
    )
    application.include_router(
        components_router,
        prefix=runtime_settings.api_v1_prefix,
    )
    application.include_router(
        compatibility_router,
        prefix=runtime_settings.api_v1_prefix,
    )
    return application


app = create_app()
