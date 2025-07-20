from pydantic import BaseModel, Field, validator
from typing import List, Optional, Dict, Any, Union
from datetime import datetime
from enum import Enum
import uuid

class OrderStatus(str, Enum):
    PENDING = "pending"
    CONFIRMED = "confirmed"
    PREPARING = "preparing"
    READY = "ready"
    DELIVERED = "delivered"
    CANCELLED = "cancelled"

class OrderType(str, Enum):
    DINE_IN = "dine_in"
    TAKEOUT = "takeout"
    DELIVERY = "delivery"

class PaymentStatus(str, Enum):
    PENDING = "pending"
    PAID = "paid"
    FAILED = "failed"
    REFUNDED = "refunded"

class DietaryRestriction(str, Enum):
    VEGETARIAN = "vegetarian"
    VEGAN = "vegan"
    GLUTEN_FREE = "gluten_free"
    DAIRY_FREE = "dairy_free"
    NUT_FREE = "nut_free"
    HALAL = "halal"
    KOSHER = "kosher"
    KETO = "keto"
    LOW_CARB = "low_carb"

class OrderItemModification(BaseModel):
    type: str = Field(..., description="Type of modification (add, remove, substitute)")
    description: str = Field(..., description="Description of the modification")
    price_adjustment: float = Field(0.0, description="Price adjustment for the modification")

class OrderItem(BaseModel):
    id: str = Field(default_factory=lambda: str(uuid.uuid4()), description="Unique order item ID")
    menu_item_id: str = Field(..., description="ID of the menu item")
    name: str = Field(..., description="Name of the menu item")
    quantity: int = Field(..., ge=1, description="Quantity ordered")
    unit_price: float = Field(..., ge=0, description="Unit price of the item")
    total_price: float = Field(..., ge=0, description="Total price for this item")
    size: Optional[str] = Field(None, description="Size specification if applicable")
    modifications: List[OrderItemModification] = Field(default_factory=list, description="Item modifications")
    special_instructions: Optional[str] = Field(None, description="Special preparation instructions")
    allergen_notes: Optional[str] = Field(None, description="Allergen-related notes")

class CustomerInfo(BaseModel):
    user_id: str = Field(..., description="User ID from authentication")
    name: str = Field(..., description="Customer name")
    phone: Optional[str] = Field(None, description="Customer phone number")
    email: Optional[str] = Field(None, description="Customer email")
    preferred_language: Optional[str] = Field("english", description="Customer's preferred language")
    dietary_restrictions: List[DietaryRestriction] = Field(default_factory=list, description="Dietary restrictions")

class DeliveryInfo(BaseModel):
    address: str = Field(..., description="Delivery address")
    city: str = Field(..., description="City")
    postal_code: str = Field(..., description="Postal code")
    delivery_notes: Optional[str] = Field(None, description="Delivery instructions")
    estimated_delivery_time: Optional[datetime] = Field(None, description="Estimated delivery time")

class Order(BaseModel):
    id: str = Field(default_factory=lambda: str(uuid.uuid4()), description="Unique order ID")
    business_id: str = Field(..., description="Business ID")
    customer_info: CustomerInfo = Field(..., description="Customer information")
    order_type: OrderType = Field(..., description="Type of order")
    status: OrderStatus = Field(OrderStatus.PENDING, description="Order status")
    payment_status: PaymentStatus = Field(PaymentStatus.PENDING, description="Payment status")
    items: List[OrderItem] = Field(..., description="List of ordered items")
    subtotal: float = Field(..., ge=0, description="Subtotal before taxes and fees")
    tax_amount: float = Field(0.0, ge=0, description="Tax amount")
    delivery_fee: float = Field(0.0, ge=0, description="Delivery fee if applicable")
    total_amount: float = Field(..., ge=0, description="Total order amount")
    currency: str = Field("USD", description="Currency code")
    delivery_info: Optional[DeliveryInfo] = Field(None, description="Delivery information")
    special_instructions: Optional[str] = Field(None, description="Order-level special instructions")
    estimated_ready_time: Optional[datetime] = Field(None, description="Estimated ready time")
    created_at: datetime = Field(default_factory=datetime.utcnow, description="Order creation timestamp")
    updated_at: datetime = Field(default_factory=datetime.utcnow, description="Last update timestamp")
    agent_session_id: Optional[str] = Field(None, description="AI agent session ID")

class OrderCreate(BaseModel):
    business_id: str = Field(..., description="Business ID")
    customer_info: CustomerInfo = Field(..., description="Customer information")
    order_type: OrderType = Field(..., description="Type of order")
    items: List[OrderItem] = Field(..., description="List of ordered items")
    delivery_info: Optional[DeliveryInfo] = Field(None, description="Delivery information")
    special_instructions: Optional[str] = Field(None, description="Order-level special instructions")
    agent_session_id: Optional[str] = Field(None, description="AI agent session ID")

class OrderUpdate(BaseModel):
    status: Optional[OrderStatus] = Field(None, description="Updated order status")
    payment_status: Optional[PaymentStatus] = Field(None, description="Updated payment status")
    items: Optional[List[OrderItem]] = Field(None, description="Updated list of items")
    special_instructions: Optional[str] = Field(None, description="Updated special instructions")
    estimated_ready_time: Optional[datetime] = Field(None, description="Updated estimated ready time")

class OrderResponse(BaseModel):
    order: Order = Field(..., description="Order details")
    agent_response: Optional[str] = Field(None, description="AI agent response")
    recommendations: Optional[List[str]] = Field(None, description="Additional recommendations")

class OrderListResponse(BaseModel):
    orders: List[Order] = Field(..., description="List of orders")
    total_count: int = Field(..., description="Total number of orders")
    page: int = Field(..., description="Current page number")
    per_page: int = Field(..., description="Items per page")

class OrderStatusUpdate(BaseModel):
    order_id: str = Field(..., description="Order ID")
    status: OrderStatus = Field(..., description="New status")
    message: Optional[str] = Field(None, description="Status update message")
    estimated_ready_time: Optional[datetime] = Field(None, description="Updated estimated ready time")

class CustomerPreference(BaseModel):
    user_id: str = Field(..., description="User ID")
    favorite_items: List[str] = Field(default_factory=list, description="Favorite menu item IDs")
    dietary_restrictions: List[DietaryRestriction] = Field(default_factory=list, description="Dietary restrictions")
    preferred_language: str = Field("english", description="Preferred language")
    spice_level: Optional[str] = Field(None, description="Preferred spice level")
    budget_range: Optional[str] = Field(None, description="Preferred budget range")
    preferred_order_type: Optional[OrderType] = Field(None, description="Preferred order type")
    allergen_warnings: List[str] = Field(default_factory=list, description="Allergen warnings")
    created_at: datetime = Field(default_factory=datetime.utcnow, description="Created timestamp")
    updated_at: datetime = Field(default_factory=datetime.utcnow, description="Updated timestamp")

class OrderCartItem(BaseModel):
    menu_item_id: str = Field(..., description="Menu item ID")
    name: str = Field(..., description="Item name")
    quantity: int = Field(..., ge=1, description="Quantity")
    unit_price: float = Field(..., ge=0, description="Unit price")
    size: Optional[str] = Field(None, description="Size specification")
    modifications: List[OrderItemModification] = Field(default_factory=list, description="Modifications")
    special_instructions: Optional[str] = Field(None, description="Special instructions")

class OrderCart(BaseModel):
    session_id: str = Field(..., description="Cart session ID")
    user_id: str = Field(..., description="User ID")
    business_id: str = Field(..., description="Business ID")
    items: List[OrderCartItem] = Field(default_factory=list, description="Cart items")
    order_type: Optional[OrderType] = Field(None, description="Order type")
    delivery_info: Optional[DeliveryInfo] = Field(None, description="Delivery info")
    special_instructions: Optional[str] = Field(None, description="Special instructions")
    created_at: datetime = Field(default_factory=datetime.utcnow, description="Created timestamp")
    updated_at: datetime = Field(default_factory=datetime.utcnow, description="Updated timestamp")

class OrderAnalytics(BaseModel):
    total_orders: int = Field(..., description="Total number of orders")
    total_revenue: float = Field(..., description="Total revenue")
    average_order_value: float = Field(..., description="Average order value")
    popular_items: List[Dict[str, Any]] = Field(..., description="Most popular items")
    order_trends: Dict[str, Any] = Field(..., description="Order trends data")
    customer_satisfaction: Optional[float] = Field(None, description="Customer satisfaction score")

class AgentInteraction(BaseModel):
    session_id: str = Field(..., description="Agent session ID")
    user_id: str = Field(..., description="User ID")
    message: str = Field(..., description="User message")
    agent_response: str = Field(..., description="Agent response")
    agent_type: str = Field(..., description="Type of agent used")
    language: str = Field("english", description="Language used")
    context: Optional[Dict[str, Any]] = Field(None, description="Conversation context")
    timestamp: datetime = Field(default_factory=datetime.utcnow, description="Interaction timestamp")

class AgentSession(BaseModel):
    session_id: str = Field(default_factory=lambda: str(uuid.uuid4()), description="Session ID")
    user_id: str = Field(..., description="User ID")
    business_id: str = Field(..., description="Business ID")
    language: str = Field("english", description="Session language")
    context: Dict[str, Any] = Field(default_factory=dict, description="Session context")
    interactions: List[AgentInteraction] = Field(default_factory=list, description="Session interactions")
    created_at: datetime = Field(default_factory=datetime.utcnow, description="Session created timestamp")
    updated_at: datetime = Field(default_factory=datetime.utcnow, description="Session updated timestamp")
    is_active: bool = Field(True, description="Session active status")