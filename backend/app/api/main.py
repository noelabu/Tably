from app.api.endpoints import (
    auth, 
    menu_items, 
    menu_image_analysis, 
    menu_agent, 
    ordering_agents,
    orders,
    customer_preferences,
    order_tracking
)
from fastapi import APIRouter

api_router = APIRouter()

# Include routers with prefixes
api_router.include_router(auth.router, prefix="/auth", tags=["auth"])
api_router.include_router(menu_items.router, prefix="/menu-items", tags=["menu-items"])
api_router.include_router(menu_image_analysis.router, prefix="/menu-image-analysis", tags=["menu-image-analysis"])
api_router.include_router(menu_agent.router, prefix="/menu-agent", tags=["menu-agent"])
api_router.include_router(ordering_agents.router, prefix="/ordering", tags=["ordering"])
api_router.include_router(orders.router, prefix="/orders", tags=["orders"])
api_router.include_router(customer_preferences.router, prefix="/customer", tags=["customer-preferences"])
api_router.include_router(order_tracking.router, prefix="/tracking", tags=["order-tracking"])
