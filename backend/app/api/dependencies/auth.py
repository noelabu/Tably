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
    token: str = Depends(oauth2_scheme)
) -> UserResponse:
    """
    Validate JWT token and return current user
    
    This dependency can be used to protect routes that require authentication
    """
    try:
        # Create a Supabase client with the user's token for auth operations
        user_supabase = create_client(settings.SUPABASE_URL, settings.SUPABASE_ANON_KEY)
        
        # Set the authorization header directly
        user_supabase.auth.set_session(token, token)
        
        user_response = user_supabase.auth.get_user(token)
        if not user_response or not user_response.user:
            logger.error("Invalid or expired token")
            raise HTTPException(
                status_code=401, detail="Unauthorized Access: Invalid token"
            )
        
        # Use service key client for database operations
        service_supabase = create_client(settings.SUPABASE_URL, settings.SUPABASE_KEY)
        user_data_response = service_supabase.table("users").select("*").eq("id", user_response.user.id).execute()
        
        if not user_data_response.data:
            logger.error("User not found in public.users table")
            raise HTTPException(
                status_code=404, detail="User not found"
            )
        
        user_data = user_data_response.data[0]
        
        return UserResponse(
            id=user_response.user.id,
            email=user_response.user.email,
            full_name=user_data.get("full_name") or user_response.user.user_metadata.get("full_name") if user_response.user.user_metadata else None,
            role=user_data.get("role", "customer"),  # Get role from public.users table
            created_at=user_data.get("created_at") or (user_response.user.created_at.isoformat() if user_response.user.created_at else None)
        )

    except HTTPException:
        raise
    except Exception as e:
        logger.error("Token validation failed: %s", str(e))
        raise HTTPException(
            status_code=401, detail=f"Token validation failed: {str(e)}"
        )


async def get_current_user_optional(
    token: Optional[str] = Depends(oauth2_scheme)
) -> Optional[UserResponse]:
    """
    Optional authentication dependency
    Returns user if valid token is provided, None otherwise
    """
    if not token:
        return None
    
    try:
        return await get_current_user(token)
    except HTTPException:
        return None