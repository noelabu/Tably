from fastapi import APIRouter, HTTPException, Depends, status, Form
from supabase import Client
import logging
from datetime import datetime
from app.core.config import settings
from app.core.supabase import get_supabase_client
from app.models.business import ManageRequest
from app.api.dependencies.auth import get_current_user, get_supabase
from gotrue.errors import AuthApiError

# Configure logging
logging.basicConfig(level=getattr(logging, settings.LOG_LEVEL))
logger = logging.getLogger(__name__)

router = APIRouter()

#Health check endpoint
@router.get("/health")
async def health_check():
    """
    Simple health check endpoint to verify the service is running
    """
    return {
        "status": "healthy",
        "timestamp": datetime.now().isoformat(),
        "service": "business" 
    }

# Manage endpoint
@router.post("/manage")
async def manage(request: ManageRequest, user = Depends(get_current_user)):
    """
    Insert business information into the database
    """
    try:
        supabase = get_supabase_client()
        supabase.table("businesses").insert({
            "name": request.name,
            "address": request.address,
            "city": request.city,
            "state": request.state,
            "zip_code": request.zip_code,
            "phone": request.phone,
            "email": request.email,
            "cuisine_type": request.cuisine_type,
            "open_time": request.open_time,
            "close_time": request.close_time,
            "owner_id": user.id
        }).execute()
        return {"message": "Business managed successfully"}
    except Exception as e:
        logger.error(f"Error managing business: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="An error occurred while managing the business"
        )
