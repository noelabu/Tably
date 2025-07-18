from pydantic import BaseModel, Field
from typing import Optional
from decimal import Decimal

class OrderItemBase(BaseModel):
    menu_item_id: str = Field(..., description="ID of the menu item")
    quantity: int = Field(..., gt=0, le=100, description="Quantity of the menu item")
    price_at_order: Decimal = Field(..., description="Price of the menu item at the time of order")

class OrderItemCreate(OrderItemBase):
    pass

class OrderItemResponse(OrderItemBase):
    id: str
    order_id: str

    class Config:
        from_attributes = True
