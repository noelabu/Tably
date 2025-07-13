from app.api.endpoints import auth, menu_items, orders
from fastapi import APIRouter

api_router = APIRouter()

# Import and include routers from endpoints
from app.api.endpoints import auth, menu_items, orders

# Include routers with prefixes
api_router.include_router(auth.router, prefix="/auth", tags=["auth"])
api_router.include_router(menu_items.router, prefix="/menu-items", tags=["menu-items"])
api_router.include_router(orders.router, prefix="/orders", tags=["orders"])
