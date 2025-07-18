from pydantic import BaseModel, Field
from typing import Optional, List, Dict, Any
from decimal import Decimal
from datetime import datetime
from enum import Enum
from app.models.order_items import OrderItemBase

class OrderStatus(str, Enum):
    PENDING = "pending"
    CONFIRMED = "confirmed"
    PREPARING = "preparing"
    READY = "ready"
    COMPLETED = "completed"
    CANCELLED = "cancelled"

class OrderBase(BaseModel):
    business_id: str = Field(..., description="ID of the business this order belongs to")
    total_amount: Decimal = Field(..., gt=0, description="Total amount of the order")
    status: OrderStatus = Field(..., description="Status of the order")

class OrderCreate(OrderBase):
    order_items: List[OrderItemBase] = Field(..., description="List of items in the order")


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
        

class OrderUpdate(BaseModel):
    status: Optional[OrderStatus] = Field(None, description="New status of the order")
    special_instructions: Optional[str] = Field(None, max_length=1000, description="Special instructions for the entire order")
    pickup_time: Optional[datetime] = Field(None, description="Requested pickup time")

class OrderResponse(BaseModel):
    id: str
    customer_id: str
    business_id: str
    total_amount: Decimal
    status: OrderStatus
    created_at: datetime
    
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