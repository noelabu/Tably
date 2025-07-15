from pydantic import BaseModel, Field, EmailStr
from typing import Optional, List
from datetime import datetime

class BusinessBase(BaseModel):
    name: str = Field(..., min_length=1, max_length=200, description="Name of the business")
    address: str = Field(..., max_length=300, description="Address of the business")
    city: str = Field(..., max_length=100, description="City where the business is located")
    state: str = Field(..., max_length=100, description="State where the business is located")
    zip_code: str = Field(..., max_length=20, description="ZIP code of the business")
    phone: str = Field(..., max_length=20, description="Phone number of the business")
    email: EmailStr = Field(..., description="Contact email of the business")
    cuisine_type: str = Field(..., max_length=100, description="Type of cuisine served")
    open_time: str = Field(..., max_length=10, description="Opening time (e.g., 09:00)")
    close_time: str = Field(..., max_length=10, description="Closing time (e.g., 21:00)")
    image_url: Optional[str] = Field(None, description="URL to the business image/logo")
    description: Optional[str] = Field(None, max_length=1000, description="Description of the business")

class BusinessCreate(BusinessBase):
    pass

class BusinessUpdate(BaseModel):
    name: Optional[str] = Field(None, min_length=1, max_length=200, description="Name of the business")
    address: Optional[str] = Field(None, max_length=300, description="Address of the business")
    city: Optional[str] = Field(None, max_length=100, description="City where the business is located")
    state: Optional[str] = Field(None, max_length=100, description="State where the business is located")
    zip_code: Optional[str] = Field(None, max_length=20, description="ZIP code of the business")
    phone: Optional[str] = Field(None, max_length=20, description="Phone number of the business")
    email: Optional[EmailStr] = Field(None, description="Contact email of the business")
    cuisine_type: Optional[str] = Field(None, max_length=100, description="Type of cuisine served")
    open_time: Optional[str] = Field(None, max_length=10, description="Opening time (e.g., 09:00)")
    close_time: Optional[str] = Field(None, max_length=10, description="Closing time (e.g., 21:00)")
    image_url: Optional[str] = Field(None, description="URL to the business image/logo")
    description: Optional[str] = Field(None, max_length=1000, description="Description of the business")

class BusinessResponse(BusinessBase):
    id: str
    owner_id: str
    created_at: datetime

    class Config:
        from_attributes = True

class BusinessesListResponse(BaseModel):
    items: List[BusinessResponse]
    total: int
    page: int
    page_size: int

class BusinessDeleteResponse(BaseModel):
    message: str
    deleted_id: str