from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
import logging
import os
from app.api.main import api_router
from app.core.config import Settings

# Ensure environment variables are loaded from .env file
try:
    from dotenv import load_dotenv
    load_dotenv()
except ImportError:
    pass

def create_app(
    settings: Settings | None = None,
) -> FastAPI:
    """Create a new app from application settings"""

    # Configure logging
    logging.basicConfig(level=logging.INFO)

    if settings is None:
        settings = Settings()

    app = FastAPI(
        title="Tably API",
        description="Multi agent ordering system for Tably",
        version="0.1.0",
        openapi_url=f"{settings.API_V1_STR}/openapi.json",
        docs_url="/docs",
        redoc_url="/redoc",
    )

    if settings.CORS_ENABLED:
        app.add_middleware(
            CORSMiddleware,
            allow_origins=settings.CORS_ALLOWED_ORIGINS,
            allow_credentials=settings.CORS_ALLOW_CREDENTIALS,
            allow_methods=settings.CORS_ALLOWED_METHODS,
            allow_headers=settings.CORS_ALLOWED_HEADERS,
        )

    # Add a root endpoint
    @app.get("/")
    async def root():
        return {"message": "LineCoach API is running", "docs": "/docs"}

    # Include the API router
    app.include_router(api_router, prefix=settings.API_V1_STR)

    return app
