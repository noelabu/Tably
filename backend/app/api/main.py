from app.api.endpoints import auth, menu_items, menu_image_analysis, menu_agent
from fastapi import APIRouter

api_router = APIRouter()

# Include routers with prefixes
api_router.include_router(auth.router, prefix="/auth", tags=["auth"])
api_router.include_router(menu_items.router, prefix="/menu-items", tags=["menu-items"])
api_router.include_router(menu_image_analysis.router, prefix="/menu-image-analysis", tags=["menu-image-analysis"])
api_router.include_router(menu_agent.router, prefix="/menu-agent", tags=["menu-agent"])
