from fastapi import APIRouter, HTTPException, Depends, status, Request
import logging
from datetime import datetime
from app.core.config import settings
from app.core.supabase import get_supabase_client
from app.models.auth import LoginRequest, SignupRequest, TokenResponse, UserResponse, RefreshTokenRequest
from gotrue.errors import AuthApiError

# Configure logging
logging.basicConfig(level=getattr(logging, settings.LOG_LEVEL))
logger = logging.getLogger(__name__)

router = APIRouter()

# Health check endpoint
@router.get("/health")
async def health_check():
    """
    Simple health check endpoint to verify the service is running
    """
    return {
        "status": "healthy",
        "timestamp": datetime.now().isoformat(),
        "service": "auth"
    }

# Signup endpoint
@router.post("/signup", response_model=TokenResponse)
async def signup(request: SignupRequest):
    """
    Create a new user account with Supabase (no email verification required)
    """
    try:
        supabase = get_supabase_client()
        
        # Validate role if provided
        if request.role is not None and request.role not in ["customer", "business-owner"]:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Invalid role. Must be 'customer' or 'business-owner'"
            )
        
        # Use default role if not provided
        user_role = request.role if request.role is not None else "customer"
        
        # Create user with Supabase Auth
        response = supabase.auth.sign_up({
            "email": request.email,
            "password": request.password,
            "options": {
                "data": {
                    "full_name": request.full_name,
                    "role": user_role
                },
                "email_redirect_to": None  # Disable email redirect
            }
        })
        
        if response.user is None:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Failed to create user account"
            )
        
        # If no session is returned (email confirmation required), 
        # automatically sign in the user
        if response.session is None:
            # Sign in the user immediately after signup
            login_response = supabase.auth.sign_in_with_password({
                "email": request.email,
                "password": request.password
            })
            
            if login_response.session is None:
                # Return a response indicating signup was successful but login is needed
                return TokenResponse(
                    access_token="",
                    refresh_token="",
                    expires_in=None,
                    user={
                        "id": response.user.id,
                        "email": response.user.email,
                        "full_name": response.user.user_metadata.get("full_name") if response.user.user_metadata else None
                    }
                )
            
            # Use the login session
            response = login_response
        
        # Return token response
        return TokenResponse(
            access_token=response.session.access_token,
            refresh_token=response.session.refresh_token,
            expires_in=response.session.expires_in,
            user={
                "id": response.user.id,
                "email": response.user.email,
                "full_name": response.user.user_metadata.get("full_name") if response.user.user_metadata else None,
                "role": response.user.user_metadata.get("role", "customer") if response.user.user_metadata else "customer"
            }
        )
        
    except AuthApiError as e:
        logger.error(f"Supabase auth error: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )
    except Exception as e:
        logger.error(f"Signup error: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="An error occurred during signup"
        )

# Login endpoint
@router.post("/login", response_model=TokenResponse)
async def login(request: LoginRequest):
    """
    Authenticate user with email and password
    """
    try:
        supabase = get_supabase_client()
        
        # Sign in with Supabase Auth
        response = supabase.auth.sign_in_with_password({
            "email": request.email,
            "password": request.password
        })
        
        if response.session is None:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid email or password"
            )
        
        # Return token response
        return TokenResponse(
            access_token=response.session.access_token,
            refresh_token=response.session.refresh_token,
            expires_in=response.session.expires_in,
            user={
                "id": response.user.id,
                "email": response.user.email,
                "full_name": response.user.user_metadata.get("full_name") if response.user.user_metadata else None,
                "role": response.user.user_metadata.get("role", "customer") if response.user.user_metadata else "customer"
            }
        )
        
    except AuthApiError as e:
        logger.error(f"Supabase auth error: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid email or password"
        )
    except Exception as e:
        logger.error(f"Login error: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="An error occurred during login"
        )

# Logout endpoint
@router.post("/logout")
async def logout(request: Request):
    """
    Logout the current user
    """
    try:
        authorization = request.headers.get("Authorization")
        if not authorization or not authorization.startswith("Bearer "):
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Missing or invalid authorization header"
            )
        
        supabase = get_supabase_client()
        
        # Sign out with Supabase
        supabase.auth.sign_out()
        
        return {"message": "Successfully logged out"}
        
    except Exception as e:
        logger.error(f"Logout error: {str(e)}")
        # Even if logout fails on server, we return success
        # Client should clear tokens regardless
        return {"message": "Successfully logged out"}

# Refresh token endpoint
@router.post("/refresh", response_model=TokenResponse)
async def refresh_token(request: RefreshTokenRequest):
    """
    Refresh access token using refresh token
    """
    try:
        supabase = get_supabase_client()
        
        # Refresh session
        response = supabase.auth.refresh_session(request.refresh_token)
        
        if response.session is None:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid refresh token"
            )
        
        # Return new token response
        return TokenResponse(
            access_token=response.session.access_token,
            refresh_token=response.session.refresh_token,
            expires_in=response.session.expires_in,
            user={
                "id": response.user.id,
                "email": response.user.email,
                "full_name": response.user.user_metadata.get("full_name") if response.user.user_metadata else None,
                "role": response.user.user_metadata.get("role", "customer") if response.user.user_metadata else "customer"
            }
        )
        
    except AuthApiError as e:
        logger.error(f"Supabase auth error: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid refresh token"
        )
    except Exception as e:
        logger.error(f"Refresh token error: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="An error occurred while refreshing token"
        )

# Get current user endpoint
@router.get("/me", response_model=UserResponse)
async def get_current_user_endpoint(request: Request):
    """
    Get current authenticated user information
    """
    try:
        authorization = request.headers.get("Authorization")
        if not authorization or not authorization.startswith("Bearer "):
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Missing or invalid authorization header"
            )
        
        # Extract token
        access_token = authorization.split(" ")[1]
        
        supabase = get_supabase_client()
        
        # Get user from token
        response = supabase.auth.get_user(access_token)
        
        if response.user is None:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid or expired token"
            )
        
        return UserResponse(
            id=response.user.id,
            email=response.user.email,
            full_name=response.user.user_metadata.get("full_name") if response.user.user_metadata else None,
            role=response.user.user_metadata.get("role", "customer") if response.user.user_metadata else "customer",
            created_at=response.user.created_at
        )
        
    except AuthApiError as e:
        logger.error(f"Supabase auth error: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid or expired token"
        )
    except Exception as e:
        logger.error(f"Get current user error: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="An error occurred while fetching user information"
        )
