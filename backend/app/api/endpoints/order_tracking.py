from fastapi import APIRouter, HTTPException, Depends, status, Query, WebSocket, WebSocketDisconnect
from fastapi.responses import JSONResponse
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
    Order, OrderStatus, OrderType, OrderStatusUpdate,
    AgentSession, AgentInteraction
)
from app.agents.ordering_agents import (
    ordering_assistant_agent,
    translation_agent
)

logger = logging.getLogger(__name__)
router = APIRouter()

# In-memory storage for demo purposes (replace with actual database)
orders_db: Dict[str, Order] = {}
tracking_subscriptions: Dict[str, List[WebSocket]] = {}  # order_id -> list of websockets

class OrderTracker:
    """Real-time order tracking system"""
    
    def __init__(self):
        self.active_connections: Dict[str, List[WebSocket]] = {}
    
    async def connect(self, websocket: WebSocket, order_id: str):
        """Connect a WebSocket to track an order"""
        await websocket.accept()
        if order_id not in self.active_connections:
            self.active_connections[order_id] = []
        self.active_connections[order_id].append(websocket)
    
    def disconnect(self, websocket: WebSocket, order_id: str):
        """Disconnect a WebSocket from tracking"""
        if order_id in self.active_connections:
            self.active_connections[order_id].remove(websocket)
            if not self.active_connections[order_id]:
                del self.active_connections[order_id]
    
    async def send_update(self, order_id: str, update: Dict[str, Any]):
        """Send update to all clients tracking this order"""
        if order_id in self.active_connections:
            for websocket in self.active_connections[order_id][:]:  # Copy to avoid modification during iteration
                try:
                    await websocket.send_json(update)
                except:
                    # Remove dead connections
                    self.active_connections[order_id].remove(websocket)

# Global order tracker instance
order_tracker = OrderTracker()

@router.get("/orders/{order_id}/status")
async def get_order_status(
    order_id: str,
    current_user: UserResponse = Depends(get_current_user)
):
    """
    Get current status of an order with AI-powered insights.
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
        
        # Generate AI status update
        agent_response = ordering_assistant_agent(
            f"Give me a detailed status update for order {order_id}",
            None,
            f"Order status: {order.status.value}, created: {order.created_at}, items: {len(order.items)}"
        )
        
        # Calculate progress
        progress = get_order_progress(order.status)
        
        # Get estimated times
        estimated_completion = get_estimated_completion(order)
        
        return {
            "order_id": order_id,
            "status": order.status.value,
            "progress_percentage": progress,
            "estimated_ready_time": order.estimated_ready_time,
            "estimated_completion_time": estimated_completion,
            "order_type": order.order_type.value,
            "items_count": len(order.items),
            "total_amount": order.total_amount,
            "agent_update": agent_response,
            "last_updated": order.updated_at,
            "timeline": generate_order_timeline(order)
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error getting order status: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to get order status"
        )

@router.get("/orders/{order_id}/tracking")
async def get_detailed_tracking(
    order_id: str,
    current_user: UserResponse = Depends(get_current_user),
    include_predictions: bool = Query(False, description="Include AI predictions")
):
    """
    Get detailed tracking information with AI predictions.
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
        
        # Generate tracking details
        tracking_info = {
            "order_id": order_id,
            "current_status": order.status.value,
            "progress_percentage": get_order_progress(order.status),
            "timeline": generate_order_timeline(order),
            "estimated_times": {
                "ready_time": order.estimated_ready_time,
                "completion_time": get_estimated_completion(order)
            },
            "location_info": get_location_info(order),
            "items_status": get_items_status(order),
            "delivery_info": order.delivery_info if order.order_type == OrderType.DELIVERY else None
        }
        
        # Add AI predictions if requested
        if include_predictions:
            prediction_context = f"""
            Order: {order_id}
            Status: {order.status.value}
            Type: {order.order_type.value}
            Items: {len(order.items)}
            Created: {order.created_at}
            """
            
            predictions = ordering_assistant_agent(
                "Provide predictions for this order's completion and potential issues",
                None,
                prediction_context
            )
            
            tracking_info["ai_predictions"] = predictions
        
        return tracking_info
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error getting detailed tracking: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to get detailed tracking"
        )

@router.websocket("/orders/{order_id}/track-live")
async def track_order_live(
    websocket: WebSocket,
    order_id: str,
    # current_user: UserResponse = Depends(get_current_user)  # WebSocket auth is complex
):
    """
    Real-time order tracking via WebSocket.
    """
    try:
        # For demo purposes, we'll skip auth in WebSocket
        # In production, implement proper WebSocket authentication
        
        if order_id not in orders_db:
            await websocket.close(code=4004, reason="Order not found")
            return
        
        await order_tracker.connect(websocket, order_id)
        
        # Send initial status
        order = orders_db[order_id]
        initial_update = {
            "type": "status_update",
            "order_id": order_id,
            "status": order.status.value,
            "progress": get_order_progress(order.status),
            "timestamp": datetime.utcnow().isoformat(),
            "message": f"Connected to order {order_id} tracking"
        }
        await websocket.send_json(initial_update)
        
        # Keep connection alive and send periodic updates
        while True:
            try:
                # Wait for any message from client (heartbeat)
                data = await asyncio.wait_for(websocket.receive_text(), timeout=30.0)
                
                # Send current status as response to heartbeat
                current_order = orders_db.get(order_id)
                if current_order:
                    update = {
                        "type": "heartbeat_response",
                        "order_id": order_id,
                        "status": current_order.status.value,
                        "progress": get_order_progress(current_order.status),
                        "timestamp": datetime.utcnow().isoformat()
                    }
                    await websocket.send_json(update)
                
            except asyncio.TimeoutError:
                # Send periodic update even without heartbeat
                current_order = orders_db.get(order_id)
                if current_order:
                    update = {
                        "type": "periodic_update",
                        "order_id": order_id,
                        "status": current_order.status.value,
                        "progress": get_order_progress(current_order.status),
                        "timestamp": datetime.utcnow().isoformat()
                    }
                    await websocket.send_json(update)
                
    except WebSocketDisconnect:
        order_tracker.disconnect(websocket, order_id)
        logger.info(f"Client disconnected from order {order_id} tracking")
    except Exception as e:
        logger.error(f"Error in live tracking: {e}")
        await websocket.close(code=4000, reason="Internal error")
        order_tracker.disconnect(websocket, order_id)

@router.post("/orders/{order_id}/update-status")
async def update_order_status(
    order_id: str,
    status_update: OrderStatusUpdate,
    current_user: UserResponse = Depends(get_current_user)
):
    """
    Update order status (typically used by restaurant staff).
    """
    try:
        if order_id not in orders_db:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Order not found"
            )
        
        order = orders_db[order_id]
        
        # Update order status
        old_status = order.status
        order.status = status_update.status
        order.updated_at = datetime.utcnow()
        
        if status_update.estimated_ready_time:
            order.estimated_ready_time = status_update.estimated_ready_time
        
        # Generate AI status update message
        agent_message = ordering_assistant_agent(
            f"Order {order_id} status updated from {old_status.value} to {status_update.status.value}",
            None,
            status_update.message or "Status updated by staff"
        )
        
        # Send real-time update to connected clients
        update_message = {
            "type": "status_changed",
            "order_id": order_id,
            "old_status": old_status.value,
            "new_status": status_update.status.value,
            "message": status_update.message or agent_message,
            "estimated_ready_time": order.estimated_ready_time,
            "timestamp": datetime.utcnow().isoformat()
        }
        
        await order_tracker.send_update(order_id, update_message)
        
        return {
            "order_id": order_id,
            "old_status": old_status.value,
            "new_status": status_update.status.value,
            "message": status_update.message,
            "agent_response": agent_message,
            "timestamp": datetime.utcnow().isoformat()
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error updating order status: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to update order status"
        )

@router.get("/orders/{order_id}/delivery-tracking")
async def get_delivery_tracking(
    order_id: str,
    current_user: UserResponse = Depends(get_current_user)
):
    """
    Get delivery tracking information for delivery orders.
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
        
        if order.order_type != OrderType.DELIVERY:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Order is not a delivery order"
            )
        
        # Generate delivery tracking info
        delivery_info = {
            "order_id": order_id,
            "delivery_status": get_delivery_status(order.status),
            "delivery_address": order.delivery_info.address if order.delivery_info else None,
            "estimated_delivery_time": order.delivery_info.estimated_delivery_time if order.delivery_info else None,
            "delivery_instructions": order.delivery_info.delivery_notes if order.delivery_info else None,
            "driver_info": get_driver_info(order),  # Mock data
            "location_updates": get_location_updates(order),  # Mock data
            "contact_info": {
                "restaurant_phone": "+1-555-0123",
                "support_phone": "+1-555-0100"
            }
        }
        
        # Generate AI delivery update
        agent_response = ordering_assistant_agent(
            f"Provide delivery tracking update for order {order_id}",
            None,
            f"Delivery status: {delivery_info['delivery_status']}, address: {delivery_info['delivery_address']}"
        )
        
        delivery_info["agent_update"] = agent_response
        
        return delivery_info
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error getting delivery tracking: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to get delivery tracking"
        )

@router.get("/orders/{order_id}/notifications")
async def get_order_notifications(
    order_id: str,
    current_user: UserResponse = Depends(get_current_user)
):
    """
    Get notification history for an order.
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
        
        # Generate notification history (mock data)
        notifications = [
            {
                "id": str(uuid.uuid4()),
                "type": "order_confirmed",
                "message": "Your order has been confirmed",
                "timestamp": order.created_at + timedelta(minutes=2),
                "read": True
            },
            {
                "id": str(uuid.uuid4()),
                "type": "preparation_started",
                "message": "Your order is being prepared",
                "timestamp": order.created_at + timedelta(minutes=5),
                "read": True
            }
        ]
        
        if order.status in [OrderStatus.READY, OrderStatus.DELIVERED]:
            notifications.append({
                "id": str(uuid.uuid4()),
                "type": "order_ready",
                "message": "Your order is ready for pickup/delivery",
                "timestamp": order.updated_at,
                "read": False
            })
        
        return {
            "order_id": order_id,
            "notifications": notifications,
            "unread_count": len([n for n in notifications if not n["read"]])
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error getting order notifications: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to get order notifications"
        )

@router.post("/orders/{order_id}/feedback")
async def submit_order_feedback(
    order_id: str,
    rating: int = Query(..., ge=1, le=5, description="Rating from 1 to 5"),
    comment: Optional[str] = Query(None, description="Feedback comment"),
    current_user: UserResponse = Depends(get_current_user)
):
    """
    Submit feedback for a completed order.
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
        
        # Check if order is completed
        if order.status not in [OrderStatus.DELIVERED, OrderStatus.READY]:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Can only provide feedback for completed orders"
            )
        
        # Generate AI response to feedback
        feedback_context = f"Customer rated order {order_id} with {rating} stars"
        if comment:
            feedback_context += f" and commented: {comment}"
        
        agent_response = ordering_assistant_agent(
            "Thank you for your feedback",
            None,
            feedback_context
        )
        
        # Store feedback (in real implementation, save to database)
        feedback_data = {
            "order_id": order_id,
            "user_id": current_user.id,
            "rating": rating,
            "comment": comment,
            "timestamp": datetime.utcnow(),
            "agent_response": agent_response
        }
        
        return {
            "message": "Feedback submitted successfully",
            "feedback": feedback_data,
            "agent_response": agent_response
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error submitting feedback: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to submit feedback"
        )

# Helper functions
def get_order_progress(status: OrderStatus) -> int:
    """Calculate order progress percentage."""
    progress_map = {
        OrderStatus.PENDING: 10,
        OrderStatus.CONFIRMED: 25,
        OrderStatus.PREPARING: 50,
        OrderStatus.READY: 75,
        OrderStatus.DELIVERED: 100,
        OrderStatus.CANCELLED: 0
    }
    return progress_map.get(status, 0)

def get_estimated_completion(order: Order) -> Optional[datetime]:
    """Calculate estimated completion time."""
    if order.status == OrderStatus.DELIVERED:
        return order.updated_at
    
    if order.estimated_ready_time:
        if order.order_type == OrderType.DELIVERY:
            return order.estimated_ready_time + timedelta(minutes=20)
        else:
            return order.estimated_ready_time
    
    # Default estimation based on current time
    base_time = datetime.utcnow()
    if order.status == OrderStatus.PENDING:
        return base_time + timedelta(minutes=25)
    elif order.status == OrderStatus.CONFIRMED:
        return base_time + timedelta(minutes=20)
    elif order.status == OrderStatus.PREPARING:
        return base_time + timedelta(minutes=15)
    elif order.status == OrderStatus.READY:
        return base_time + timedelta(minutes=5)
    
    return None

def generate_order_timeline(order: Order) -> List[Dict[str, Any]]:
    """Generate order timeline."""
    timeline = [
        {
            "status": "pending",
            "timestamp": order.created_at,
            "message": "Order placed",
            "completed": True
        }
    ]
    
    if order.status != OrderStatus.PENDING:
        timeline.append({
            "status": "confirmed",
            "timestamp": order.created_at + timedelta(minutes=2),
            "message": "Order confirmed",
            "completed": True
        })
    
    if order.status in [OrderStatus.PREPARING, OrderStatus.READY, OrderStatus.DELIVERED]:
        timeline.append({
            "status": "preparing",
            "timestamp": order.created_at + timedelta(minutes=5),
            "message": "Preparation started",
            "completed": True
        })
    
    if order.status in [OrderStatus.READY, OrderStatus.DELIVERED]:
        timeline.append({
            "status": "ready",
            "timestamp": order.estimated_ready_time or order.updated_at,
            "message": "Order ready",
            "completed": True
        })
    
    if order.status == OrderStatus.DELIVERED:
        timeline.append({
            "status": "delivered",
            "timestamp": order.updated_at,
            "message": "Order delivered",
            "completed": True
        })
    
    return timeline

def get_location_info(order: Order) -> Dict[str, Any]:
    """Get location information for order."""
    return {
        "restaurant_address": "123 Main St, Downtown",
        "delivery_address": order.delivery_info.address if order.delivery_info else None,
        "estimated_distance": "2.5 miles" if order.order_type == OrderType.DELIVERY else None
    }

def get_items_status(order: Order) -> List[Dict[str, Any]]:
    """Get status of individual items."""
    return [
        {
            "name": item.name,
            "quantity": item.quantity,
            "status": "preparing" if order.status == OrderStatus.PREPARING else "ready",
            "estimated_time": "5 mins" if order.status == OrderStatus.PREPARING else "ready"
        }
        for item in order.items
    ]

def get_delivery_status(order_status: OrderStatus) -> str:
    """Convert order status to delivery status."""
    status_map = {
        OrderStatus.PENDING: "order_received",
        OrderStatus.CONFIRMED: "preparing",
        OrderStatus.PREPARING: "preparing",
        OrderStatus.READY: "out_for_delivery",
        OrderStatus.DELIVERED: "delivered",
        OrderStatus.CANCELLED: "cancelled"
    }
    return status_map.get(order_status, "unknown")

def get_driver_info(order: Order) -> Optional[Dict[str, Any]]:
    """Get driver information (mock data)."""
    if order.order_type == OrderType.DELIVERY and order.status == OrderStatus.READY:
        return {
            "name": "John Doe",
            "phone": "+1-555-0199",
            "vehicle": "Honda Civic - ABC 123",
            "rating": 4.8,
            "estimated_arrival": datetime.utcnow() + timedelta(minutes=15)
        }
    return None

def get_location_updates(order: Order) -> List[Dict[str, Any]]:
    """Get location updates for delivery (mock data)."""
    if order.order_type == OrderType.DELIVERY and order.status == OrderStatus.READY:
        return [
            {
                "timestamp": datetime.utcnow() - timedelta(minutes=5),
                "location": "Picked up from restaurant",
                "latitude": 40.7128,
                "longitude": -74.0060
            },
            {
                "timestamp": datetime.utcnow() - timedelta(minutes=2),
                "location": "En route to delivery address",
                "latitude": 40.7150,
                "longitude": -74.0070
            }
        ]
    return []