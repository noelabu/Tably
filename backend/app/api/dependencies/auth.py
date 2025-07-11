from fastapi import Depends, HTTPException
from fastapi.security import OAuth2PasswordBearer
from supabase import create_client, Client
from app.core.config import settings
from app.models.auth import UserResponse
from typing import Optional
import logging

logger = logging.getLogger(__name__)
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/api/v1/auth/login")

supabase_client = create_client(settings.SUPABASE_URL, settings.SUPABASE_KEY)


def get_supabase():
    """Dependency that returns the shared Supabase client."""
    return supabase_client


async def get_current_supabase_client(token: str = Depends(oauth2_scheme)):
    try:
        supabase = create_client(settings.SUPABASE_URL, settings.SUPABASE_KEY)
        user_response = supabase.auth.get_user(token)
        if not user_response:
            logger.error("Invalid or expired token")
            raise HTTPException(
                status_code=401, detail="Unauthorized Access: Invalid token"
            )
        return supabase

    except Exception as e:
        logger.error("Token validation failed: %s", str(e))
        raise HTTPException(
            status_code=401, detail=f"Token validation failed: {str(e)}"
        )


async def get_current_user(
    token: str = Depends(oauth2_scheme), supabase: Client = Depends(get_supabase)
) -> UserResponse:
    """
    Validate JWT token and return current user
    
    This dependency can be used to protect routes that require authentication
    """
    try:
        user_response = supabase.auth.get_user(token)
        if not user_response or not user_response.user:
            logger.error("Invalid or expired token")
            raise HTTPException(
                status_code=401, detail="Unauthorized Access: Invalid token"
            )
        
        return UserResponse(
            id=user_response.user.id,
            email=user_response.user.email,
            full_name=user_response.user.user_metadata.get("full_name") if user_response.user.user_metadata else None,
            role=user_response.user.user_metadata.get("role", "customer") if user_response.user.user_metadata else "customer",
            created_at=user_response.user.created_at.isoformat() if user_response.user.created_at else None
        )

    except HTTPException:
        raise
    except Exception as e:
        logger.error("Token validation failed: %s", str(e))
        raise HTTPException(
            status_code=401, detail=f"Token validation failed: {str(e)}"
        )


async def get_current_user_optional(
    token: Optional[str] = Depends(oauth2_scheme), supabase: Client = Depends(get_supabase)
) -> Optional[UserResponse]:
    """
    Optional authentication dependency
    Returns user if valid token is provided, None otherwise
    """
    if not token:
        return None
    
    try:
        return await get_current_user(token, supabase)
    except HTTPException:
        return None