from pydantic import BaseModel, Field
from typing import Optional, List, Dict, Any
from decimal import Decimal
from datetime import datetime
from enum import Enum

class OrderStatus(str, Enum):
    PENDING = "pending"
    CONFIRMED = "confirmed"
    PREPARING = "preparing"
    READY = "ready"
    COMPLETED = "completed"
    CANCELLED = "cancelled"

class OrderItemBase(BaseModel):
    menu_item_id: str = Field(..., description="ID of the menu item")
    quantity: int = Field(..., gt=0, le=100, description="Quantity of the menu item")
    special_instructions: Optional[str] = Field(None, max_length=500, description="Special instructions for this item")

class OrderItemCreate(OrderItemBase):
    pass

class OrderItemResponse(OrderItemBase):
    id: str
    order_id: str
    menu_item_name: str
    menu_item_price: Decimal
    total_price: Decimal
    created_at: datetime
    
    class Config:
        from_attributes = True

class OrderBase(BaseModel):
    business_id: str = Field(..., description="ID of the business this order belongs to")
    customer_id: str = Field(..., description="ID of the customer placing the order")
    items: List[OrderItemCreate] = Field(..., min_items=1, description="List of items in the order")
    total_amount: Decimal = Field(..., gt=0, description="Total amount of the order")
    special_instructions: Optional[str] = Field(None, max_length=1000, description="Special instructions for the entire order")
    pickup_time: Optional[datetime] = Field(None, description="Requested pickup time")

class OrderCreate(OrderBase):
    pass

class OrderUpdate(BaseModel):
    status: Optional[OrderStatus] = Field(None, description="New status of the order")
    special_instructions: Optional[str] = Field(None, max_length=1000, description="Special instructions for the entire order")
    pickup_time: Optional[datetime] = Field(None, description="Requested pickup time")

class OrderResponse(BaseModel):
    id: str
    business_id: str
    customer_id: str
    status: OrderStatus
    total_amount: Decimal
    special_instructions: Optional[str]
    pickup_time: Optional[datetime]
    items: List[OrderItemResponse]
    created_at: datetime
    updated_at: datetime
    
    class Config:
        from_attributes = True

class OrdersListResponse(BaseModel):
    items: List[OrderResponse]
    total: int
    page: int
    page_size: int

class OrderDeleteResponse(BaseModel):
    message: str
    deleted_id: str 