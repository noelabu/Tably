from pydantic import BaseModel, Field
from typing import Optional, List
from decimal import Decimal
from datetime import datetime
from app.models.stock_levels import StockLevelCreate

class MenuItemBase(BaseModel):
    name: str = Field(..., min_length=1, max_length=200, description="Name of the menu item")
    description: Optional[str] = Field(None, max_length=1000, description="Description of the menu item")
    price: Decimal = Field(..., gt=0, le=9999.99, description="Price of the menu item")
    image_url: Optional[str] = Field(None, description="URL to the menu item image")
    available: bool = Field(True, description="Whether the menu item is available")

class MenuItemCreate(MenuItemBase):
    business_id: str = Field(..., description="ID of the business this menu item belongs to")
    stock_level: StockLevelCreate = Field(..., description="Stock level of the menu item")

class MenuItemUpdate(BaseModel):
    name: Optional[str] = Field(None, min_length=1, max_length=200, description="Name of the menu item")
    description: Optional[str] = Field(None, max_length=1000, description="Description of the menu item")
    price: Optional[Decimal] = Field(None, gt=0, le=9999.99, description="Price of the menu item")
    image_url: Optional[str] = Field(None, description="URL to the menu item image")
    available: Optional[bool] = Field(None, description="Whether the menu item is available")

class MenuItemResponse(MenuItemBase):
    id: str
    business_id: str
    created_at: datetime
    
    class Config:
        from_attributes = True

class MenuItemsListResponse(BaseModel):
    items: List[MenuItemResponse]
    total: int
    page: int
    page_size: int
    
class MenuItemDeleteResponse(BaseModel):
    message: str
    deleted_id: str