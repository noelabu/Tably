from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from app.core.supabase import get_supabase_client
from app.models.auth import UserResponse
from typing import Optional
import logging

logger = logging.getLogger(__name__)

# Create HTTPBearer instance for extracting bearer tokens
security = HTTPBearer()

async def get_current_user(credentials: HTTPAuthorizationCredentials = Depends(security)) -> UserResponse:
    """
    Validate JWT token and return current user
    
    This dependency can be used to protect routes that require authentication
    """
    try:
        token = credentials.credentials
        supabase = get_supabase_client()
        
        # Get user from token
        response = supabase.auth.get_user(token)
        
        if response.user is None:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid or expired token",
                headers={"WWW-Authenticate": "Bearer"},
            )
        
        return UserResponse(
            id=response.user.id,
            email=response.user.email,
            full_name=response.user.user_metadata.get("full_name") if response.user.user_metadata else None,
            role=response.user.user_metadata.get("role", "customer") if response.user.user_metadata else "customer",
            created_at=response.user.created_at
        )
        
    except Exception as e:
        logger.error(f"Authentication error: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid authentication credentials",
            headers={"WWW-Authenticate": "Bearer"},
        )

async def get_current_user_optional(credentials: Optional[HTTPAuthorizationCredentials] = Depends(security)) -> Optional[UserResponse]:
    """
    Optional authentication dependency
    Returns user if valid token is provided, None otherwise
    """
    if not credentials:
        return None
    
    try:
        return await get_current_user(credentials)
    except HTTPException:
        return None