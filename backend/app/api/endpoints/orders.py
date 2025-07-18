from fastapi import APIRouter, HTTPException, Depends, status, Query, BackgroundTasks
from fastapi.responses import JSONResponse, StreamingResponse
from fastapi.security import HTTPBearer
import logging
from typing import List, Optional, Dict, Any
import json
from datetime import datetime, timedelta
import asyncio
import uuid

from app.core.config import settings
from app.api.dependencies.auth import get_current_user
from app.models.auth import UserResponse
from app.models.ordering import (
    Order, OrderCreate, OrderUpdate, OrderResponse, OrderListResponse,
    OrderStatus, OrderType, PaymentStatus, OrderStatusUpdate,
    CustomerPreference, OrderCart, OrderCartItem, OrderAnalytics,
    AgentSession, AgentInteraction, DietaryRestriction
)
from app.agents.ordering_agents import (
    ordering_assistant_agent,
    recommendation_agent,
    translation_agent,
    process_multilingual_order,
    order_recommendation_combo
)
from app.agents.orchestrator import orchestrator

logger = logging.getLogger(__name__)
router = APIRouter()

# In-memory storage for demo purposes (replace with actual database)
orders_db: Dict[str, Order] = {}
carts_db: Dict[str, OrderCart] = {}
preferences_db: Dict[str, CustomerPreference] = {}
agent_sessions_db: Dict[str, AgentSession] = {}

@router.post("/create", response_model=OrderResponse)
async def create_order(
    order_data: OrderCreate,
    current_user: UserResponse = Depends(get_current_user),
    background_tasks: BackgroundTasks = BackgroundTasks()
):
    """
    Create a new order with AI agent assistance.
    """
    try:
        logger.info(f"Creating order for user {current_user.id}")
        
        # Calculate totals
        subtotal = sum(item.total_price for item in order_data.items)
        tax_amount = subtotal * 0.08  # 8% tax
        delivery_fee = 5.0 if order_data.order_type == OrderType.DELIVERY else 0.0
        total_amount = subtotal + tax_amount + delivery_fee
        
        # Create order
        order = Order(
            business_id=order_data.business_id,
            customer_info=order_data.customer_info,
            order_type=order_data.order_type,
            items=order_data.items,
            subtotal=subtotal,
            tax_amount=tax_amount,
            delivery_fee=delivery_fee,
            total_amount=total_amount,
            delivery_info=order_data.delivery_info,
            special_instructions=order_data.special_instructions,
            agent_session_id=order_data.agent_session_id
        )
        
        # Store order
        orders_db[order.id] = order
        
        # Generate AI agent confirmation
        agent_response = ordering_assistant_agent(
            f"Please confirm this order: {len(order.items)} items, total ${total_amount:.2f}",
            None,
            f"Order ID: {order.id}, Customer: {order.customer_info.name}"
        )
        
        # Get recommendations for future orders
        recommendations = []
        if order.customer_info.dietary_restrictions:
            dietary_str = ", ".join([dr.value for dr in order.customer_info.dietary_restrictions])
            rec_response = recommendation_agent(
                f"Customer ordered {[item.name for item in order.items]}",
                None,
                dietary_str
            )
            recommendations.append(rec_response)
        
        # Schedule order processing
        background_tasks.add_task(process_order_async, order.id)
        
        return OrderResponse(
            order=order,
            agent_response=agent_response,
            recommendations=recommendations
        )
        
    except Exception as e:
        logger.error(f"Error creating order: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to create order"
        )

@router.get("/list", response_model=OrderListResponse)
async def list_orders(
    current_user: UserResponse = Depends(get_current_user),
    status_filter: Optional[OrderStatus] = Query(None, description="Filter by order status"),
    order_type: Optional[OrderType] = Query(None, description="Filter by order type"),
    page: int = Query(1, ge=1, description="Page number"),
    per_page: int = Query(10, ge=1, le=100, description="Items per page")
):
    """
    List orders for the current user with filtering and pagination.
    """
    try:
        # Filter user's orders
        user_orders = [
            order for order in orders_db.values()
            if order.customer_info.user_id == current_user.id
        ]
        
        # Apply filters
        if status_filter:
            user_orders = [order for order in user_orders if order.status == status_filter]
        
        if order_type:
            user_orders = [order for order in user_orders if order.order_type == order_type]
        
        # Sort by creation date (newest first)
        user_orders.sort(key=lambda x: x.created_at, reverse=True)
        
        # Pagination
        total_count = len(user_orders)
        start_idx = (page - 1) * per_page
        end_idx = start_idx + per_page
        paginated_orders = user_orders[start_idx:end_idx]
        
        return OrderListResponse(
            orders=paginated_orders,
            total_count=total_count,
            page=page,
            per_page=per_page
        )
        
    except Exception as e:
        logger.error(f"Error listing orders: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to retrieve orders"
        )

@router.get("/{order_id}", response_model=OrderResponse)
async def get_order(
    order_id: str,
    current_user: UserResponse = Depends(get_current_user)
):
    """
    Get a specific order by ID.
    """
    try:
        if order_id not in orders_db:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Order not found"
            )
        
        order = orders_db[order_id]
        
        # Check if user owns this order
        if order.customer_info.user_id != current_user.id:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Access denied"
            )
        
        # Generate current status message
        agent_response = ordering_assistant_agent(
            f"What's the status of order {order_id}?",
            None,
            f"Order status: {order.status.value}, estimated ready: {order.estimated_ready_time}"
        )
        
        return OrderResponse(
            order=order,
            agent_response=agent_response
        )
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error retrieving order: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to retrieve order"
        )

@router.put("/{order_id}", response_model=OrderResponse)
async def update_order(
    order_id: str,
    order_update: OrderUpdate,
    current_user: UserResponse = Depends(get_current_user)
):
    """
    Update an existing order.
    """
    try:
        if order_id not in orders_db:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Order not found"
            )
        
        order = orders_db[order_id]
        
        # Check if user owns this order
        if order.customer_info.user_id != current_user.id:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Access denied"
            )
        
        # Check if order can be modified
        if order.status not in [OrderStatus.PENDING, OrderStatus.CONFIRMED]:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Order cannot be modified in current status"
            )
        
        # Update fields
        if order_update.status:
            order.status = order_update.status
        if order_update.payment_status:
            order.payment_status = order_update.payment_status
        if order_update.items:
            order.items = order_update.items
            # Recalculate totals
            order.subtotal = sum(item.total_price for item in order.items)
            order.tax_amount = order.subtotal * 0.08
            order.total_amount = order.subtotal + order.tax_amount + order.delivery_fee
        if order_update.special_instructions:
            order.special_instructions = order_update.special_instructions
        if order_update.estimated_ready_time:
            order.estimated_ready_time = order_update.estimated_ready_time
        
        order.updated_at = datetime.utcnow()
        
        # Generate update confirmation
        agent_response = ordering_assistant_agent(
            f"Order {order_id} has been updated",
            None,
            f"Updated order total: ${order.total_amount:.2f}"
        )
        
        return OrderResponse(
            order=order,
            agent_response=agent_response
        )
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error updating order: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to update order"
        )

@router.delete("/{order_id}")
async def cancel_order(
    order_id: str,
    current_user: UserResponse = Depends(get_current_user)
):
    """
    Cancel an order.
    """
    try:
        if order_id not in orders_db:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Order not found"
            )
        
        order = orders_db[order_id]
        
        # Check if user owns this order
        if order.customer_info.user_id != current_user.id:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Access denied"
            )
        
        # Check if order can be cancelled
        if order.status not in [OrderStatus.PENDING, OrderStatus.CONFIRMED]:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Order cannot be cancelled in current status"
            )
        
        # Cancel order
        order.status = OrderStatus.CANCELLED
        order.updated_at = datetime.utcnow()
        
        # Generate cancellation confirmation
        agent_response = ordering_assistant_agent(
            f"Order {order_id} has been cancelled",
            None,
            f"Cancelled order total: ${order.total_amount:.2f}"
        )
        
        return {"message": "Order cancelled successfully", "agent_response": agent_response}
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error cancelling order: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to cancel order"
        )

@router.post("/{order_id}/chat")
async def chat_about_order(
    order_id: str,
    message: str,
    current_user: UserResponse = Depends(get_current_user)
):
    """
    Chat with AI about a specific order.
    """
    try:
        if order_id not in orders_db:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Order not found"
            )
        
        order = orders_db[order_id]
        
        # Check if user owns this order
        if order.customer_info.user_id != current_user.id:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Access denied"
            )
        
        # Create order context
        order_context = f"""
Order ID: {order.id}
Status: {order.status.value}
Items: {[item.name for item in order.items]}
Total: ${order.total_amount:.2f}
Type: {order.order_type.value}
"""
        
        # Process message with ordering assistant
        response = ordering_assistant_agent(
            message,
            None,
            order_context
        )
        
        return {
            "response": response,
            "order_id": order_id,
            "timestamp": datetime.utcnow().isoformat()
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error in order chat: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to process chat message"
        )

@router.get("/{order_id}/track")
async def track_order(
    order_id: str,
    current_user: UserResponse = Depends(get_current_user)
):
    """
    Track order status with AI-powered updates.
    """
    try:
        if order_id not in orders_db:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Order not found"
            )
        
        order = orders_db[order_id]
        
        # Check if user owns this order
        if order.customer_info.user_id != current_user.id:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Access denied"
            )
        
        # Generate tracking information
        tracking_info = {
            "order_id": order_id,
            "status": order.status.value,
            "estimated_ready_time": order.estimated_ready_time,
            "progress": get_order_progress(order.status),
            "timeline": get_order_timeline(order),
            "next_update": get_next_update_time(order)
        }
        
        # Generate AI tracking message
        agent_response = ordering_assistant_agent(
            f"Give me a tracking update for order {order_id}",
            None,
            f"Current status: {order.status.value}, Progress: {tracking_info['progress']}%"
        )
        
        return {
            "tracking_info": tracking_info,
            "agent_message": agent_response,
            "timestamp": datetime.utcnow().isoformat()
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error tracking order: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to track order"
        )

@router.post("/cart/add")
async def add_to_cart(
    item: OrderCartItem,
    current_user: UserResponse = Depends(get_current_user),
    session_id: str = Query(..., description="Cart session ID")
):
    """
    Add item to shopping cart with AI assistance.
    """
    try:
        # Get or create cart
        if session_id not in carts_db:
            carts_db[session_id] = OrderCart(
                session_id=session_id,
                user_id=current_user.id,
                business_id="default",  # Would come from request context
                items=[]
            )
        
        cart = carts_db[session_id]
        
        # Check if item already exists in cart
        existing_item = None
        for cart_item in cart.items:
            if (cart_item.menu_item_id == item.menu_item_id and 
                cart_item.size == item.size and
                cart_item.modifications == item.modifications):
                existing_item = cart_item
                break
        
        if existing_item:
            existing_item.quantity += item.quantity
        else:
            cart.items.append(item)
        
        cart.updated_at = datetime.utcnow()
        
        # Generate AI response
        agent_response = ordering_assistant_agent(
            f"I added {item.name} to my cart",
            None,
            f"Cart now has {len(cart.items)} different items"
        )
        
        return {
            "cart": cart,
            "agent_response": agent_response,
            "message": f"Added {item.name} to cart"
        }
        
    except Exception as e:
        logger.error(f"Error adding to cart: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to add item to cart"
        )

@router.get("/cart/{session_id}")
async def get_cart(
    session_id: str,
    current_user: UserResponse = Depends(get_current_user)
):
    """
    Get shopping cart contents.
    """
    try:
        if session_id not in carts_db:
            return {"cart": None, "message": "Cart not found"}
        
        cart = carts_db[session_id]
        
        # Check if user owns this cart
        if cart.user_id != current_user.id:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Access denied"
            )
        
        # Calculate totals
        subtotal = sum(item.unit_price * item.quantity for item in cart.items)
        
        return {
            "cart": cart,
            "subtotal": subtotal,
            "item_count": len(cart.items),
            "total_quantity": sum(item.quantity for item in cart.items)
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error retrieving cart: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to retrieve cart"
        )

@router.post("/cart/{session_id}/checkout")
async def checkout_cart(
    session_id: str,
    order_type: OrderType,
    current_user: UserResponse = Depends(get_current_user),
    background_tasks: BackgroundTasks = BackgroundTasks()
):
    """
    Checkout cart and create order.
    """
    try:
        if session_id not in carts_db:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Cart not found"
            )
        
        cart = carts_db[session_id]
        
        # Check if user owns this cart
        if cart.user_id != current_user.id:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Access denied"
            )
        
        if not cart.items:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Cart is empty"
            )
        
        # Convert cart items to order items
        order_items = []
        for cart_item in cart.items:
            order_item = {
                "menu_item_id": cart_item.menu_item_id,
                "name": cart_item.name,
                "quantity": cart_item.quantity,
                "unit_price": cart_item.unit_price,
                "total_price": cart_item.unit_price * cart_item.quantity,
                "size": cart_item.size,
                "modifications": cart_item.modifications,
                "special_instructions": cart_item.special_instructions
            }
            order_items.append(order_item)
        
        # Create order
        order_data = OrderCreate(
            business_id=cart.business_id,
            customer_info={
                "user_id": current_user.id,
                "name": current_user.name or "Customer",
                "email": current_user.email,
                "preferred_language": "english"
            },
            order_type=order_type,
            items=order_items,
            delivery_info=cart.delivery_info,
            special_instructions=cart.special_instructions
        )
        
        # Create the order
        order_response = await create_order(order_data, current_user, background_tasks)
        
        # Clear cart
        del carts_db[session_id]
        
        return {
            "order": order_response.order,
            "agent_response": order_response.agent_response,
            "message": "Order created successfully from cart"
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error during checkout: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to checkout cart"
        )

@router.get("/analytics/summary")
async def get_order_analytics(
    current_user: UserResponse = Depends(get_current_user),
    start_date: Optional[datetime] = Query(None, description="Start date for analytics"),
    end_date: Optional[datetime] = Query(None, description="End date for analytics")
):
    """
    Get order analytics for the current user.
    """
    try:
        # Filter user's orders
        user_orders = [
            order for order in orders_db.values()
            if order.customer_info.user_id == current_user.id
        ]
        
        # Apply date filters
        if start_date:
            user_orders = [order for order in user_orders if order.created_at >= start_date]
        if end_date:
            user_orders = [order for order in user_orders if order.created_at <= end_date]
        
        # Calculate analytics
        total_orders = len(user_orders)
        total_revenue = sum(order.total_amount for order in user_orders)
        average_order_value = total_revenue / total_orders if total_orders > 0 else 0
        
        # Popular items
        item_counts = {}
        for order in user_orders:
            for item in order.items:
                item_counts[item.name] = item_counts.get(item.name, 0) + item.quantity
        
        popular_items = [
            {"name": name, "count": count}
            for name, count in sorted(item_counts.items(), key=lambda x: x[1], reverse=True)[:5]
        ]
        
        analytics = OrderAnalytics(
            total_orders=total_orders,
            total_revenue=total_revenue,
            average_order_value=average_order_value,
            popular_items=popular_items,
            order_trends={"monthly": {}, "weekly": {}},  # Would be calculated from real data
            customer_satisfaction=4.2  # Would come from ratings
        )
        
        return analytics
        
    except Exception as e:
        logger.error(f"Error retrieving analytics: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to retrieve analytics"
        )

# Helper functions
def get_order_progress(status: OrderStatus) -> int:
    """Calculate order progress percentage based on status."""
    progress_map = {
        OrderStatus.PENDING: 10,
        OrderStatus.CONFIRMED: 25,
        OrderStatus.PREPARING: 50,
        OrderStatus.READY: 75,
        OrderStatus.DELIVERED: 100,
        OrderStatus.CANCELLED: 0
    }
    return progress_map.get(status, 0)

def get_order_timeline(order: Order) -> List[Dict[str, Any]]:
    """Generate order timeline."""
    timeline = [
        {
            "status": "pending",
            "timestamp": order.created_at,
            "message": "Order received"
        }
    ]
    
    if order.status != OrderStatus.PENDING:
        timeline.append({
            "status": "confirmed",
            "timestamp": order.updated_at,
            "message": "Order confirmed"
        })
    
    return timeline

def get_next_update_time(order: Order) -> Optional[datetime]:
    """Estimate next update time."""
    if order.status == OrderStatus.PENDING:
        return order.created_at + timedelta(minutes=5)
    elif order.status == OrderStatus.CONFIRMED:
        return order.updated_at + timedelta(minutes=15)
    elif order.status == OrderStatus.PREPARING:
        return order.estimated_ready_time
    return None

async def process_order_async(order_id: str):
    """Background task to process order."""
    try:
        await asyncio.sleep(2)  # Simulate processing time
        if order_id in orders_db:
            order = orders_db[order_id]
            order.status = OrderStatus.CONFIRMED
            order.estimated_ready_time = datetime.utcnow() + timedelta(minutes=20)
            order.updated_at = datetime.utcnow()
            logger.info(f"Order {order_id} confirmed and processing started")
    except Exception as e:
        logger.error(f"Error processing order {order_id}: {e}")