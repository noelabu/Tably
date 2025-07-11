from pydantic import BaseModel, EmailStr, field_validator
from typing import Optional, Dict, Any

class LoginRequest(BaseModel):
    email: EmailStr
    password: str

class SignupRequest(BaseModel):
    email: EmailStr
    password: str
    full_name: Optional[str] = None
    role: Optional[str] = None  # Optional, defaults to "customer" if not provided
    
    @field_validator('role')
    @classmethod
    def validate_role(cls, v):
        if v is not None and v not in ["customer", "business-owner"]:
            raise ValueError("Role must be 'customer' or 'business-owner'")
        return v

class TokenResponse(BaseModel):
    access_token: str
    token_type: str = "bearer"
    refresh_token: Optional[str] = None
    expires_in: Optional[int] = None
    user: Optional[Dict[str, Any]] = None

class UserResponse(BaseModel):
    id: str
    email: str
    full_name: Optional[str] = None
    role: str = "customer"
    created_at: Optional[str] = None
    
class RefreshTokenRequest(BaseModel):
    refresh_token: str