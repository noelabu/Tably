from fastapi import APIRouter
from app.api.endpoints import auth, business, menu_items, orders, menu_image_analysis

api_router = APIRouter()

# Include routers with prefixes
api_router.include_router(auth.router, prefix="/auth", tags=["auth"])
api_router.include_router(business.router, prefix="/business", tags=["business"])
api_router.include_router(menu_items.router, prefix="/menu-items", tags=["menu-items"])
api_router.include_router(menu_image_analysis.router, prefix="/menu-image-analysis", tags=["menu-image-analysis"])
