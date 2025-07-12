from app.api.endpoints import auth
from app.api.endpoints import business
from fastapi import APIRouter

api_router = APIRouter()

# Import and include routers from endpoints
from app.api.endpoints import auth

# Include the linecoach router with a prefix
api_router.include_router(auth.router, prefix="/auth", tags=["auth"])
api_router.include_router(business.router, prefix="/business", tags=["business"])
