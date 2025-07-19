from fastapi import APIRouter, HTTPException, Depends, status, Query
import logging
from typing import List
from app.core.config import settings
from app.api.dependencies.auth import get_current_user
from app.models.auth import UserResponse
from app.models.orders import (
    OrderCreate, 
    OrderUpdate, 
    OrderResponse, 
    OrdersListResponse,
    OrderDeleteResponse,
    OrderStatus,
    OrderWithBusinessResponse,
    OrderListBusinessResponse,
    OrderWithItemsResponse,
    OrderItemWithMenuName,
)
from app.models.order_items import OrderItemCreate
from app.db.orders import OrdersConnection
from app.db.order_items import OrderItemsConnection
from app.db.stock_level import StockLevelConnection
from datetime import datetime
from app.db.business import BusinessConnection
from app.models.business import BusinessResponse
from pydantic import BaseModel

# Configure logging
logging.basicConfig(level=getattr(logging, settings.LOG_LEVEL))
logger = logging.getLogger(__name__)

router = APIRouter()

def get_orders_db() -> OrdersConnection:
    """Dependency to get OrdersConnection instance"""
    return OrdersConnection()

def get_order_items_db() -> OrderItemsConnection:
    """Dependency to get OrderItemsConnection instance"""
    return OrderItemsConnection()

def get_stock_level_db() -> StockLevelConnection:
    """Dependency to get StockLevelConnection instance"""
    return StockLevelConnection()

# Response model for a list of OrderResponse
class OrdersSimpleListResponse(BaseModel):
    items: List[OrderResponse]
    total: int
    page: int
    page_size: int

# CREATE - Add new order
@router.post("/", response_model=OrderResponse, status_code=status.HTTP_201_CREATED)
async def create_order(
    order: OrderCreate,
    current_user: UserResponse = Depends(get_current_user),
    orders_db: OrdersConnection = Depends(get_orders_db),
    order_items_db: OrderItemsConnection = Depends(get_order_items_db),
    stock_level_db: StockLevelConnection = Depends(get_stock_level_db)
):
    """Create a new order"""
    try:
        logger.info(f"Creating order for business {order.business_id}")
        logger.debug(f"Order data: {order.model_dump()}")
        
        # Create order data
        order_data = {
            "business_id": order.business_id,
            "customer_id": current_user.id,  # Use current user as customer
            "total_amount": float(order.total_amount),
            "status": "pending"
        }
        
        # Create the order
        result = await orders_db.create_order(order_data)
        
        if not result:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Failed to create order"
            )
        
        # Create order items
        order_items_data = []
        for item in order.order_items:
            order_items_data.append({
                "order_id": result["id"],
                "menu_item_id": item.menu_item_id,
                "quantity": item.quantity,
                "price_at_order": float(item.price_at_order)
            })
        
        await order_items_db.create_order_items(order_items_data)
        
        # Update stock level
        for item in order.order_items:
            stock_level = await stock_level_db.get_stock_level_by_menu_item_id(item.menu_item_id)
            if stock_level:
                stock_level["quantity_available"] -= item.quantity
                await stock_level_db.update_stock_level(stock_level)
            else:
                raise HTTPException(
                    status_code=status.HTTP_404_NOT_FOUND,
                    detail="Stock level not found"
                )

        # Get the complete order with items
        complete_order = await orders_db.get_order_by_id(result["id"])
        
        if not complete_order:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Failed to retrieve created order"
            )
        
        # Convert any datetime fields in complete_order to ISO strings for serialization
        if "created_at" in complete_order and isinstance(complete_order["created_at"], (datetime,)):
            complete_order["created_at"] = complete_order["created_at"].isoformat()
        # Also convert in items
        if "items" in complete_order:
            for item in complete_order["items"]:
                if "created_at" in item and isinstance(item["created_at"], (datetime,)):
                    item["created_at"] = item["created_at"].isoformat()
                    
        return OrderResponse(**complete_order)
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error creating order: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="An error occurred while creating the order"
        )

# READ - Get orders for a business (business owner view)
@router.get("/business/{business_id}", response_model=OrdersSimpleListResponse)
async def get_orders_by_business(
    business_id: str,
    page: int = Query(1, ge=1, description="Page number"),
    page_size: int = Query(20, ge=1, le=100, description="Items per page"),
    status_filter: str = Query(None, description="Filter by order status"),
    current_user: UserResponse = Depends(get_current_user),
    orders_db: OrdersConnection = Depends(get_orders_db)
):
    """Get all orders for a specific business with pagination (business owner view)"""
    try:
        # Verify user owns the business
        if not await orders_db.verify_business_ownership(business_id, current_user.id):
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="You don't have permission to access this business"
            )
        # Get orders with pagination
        result = await orders_db.get_orders_by_business(
            business_id=business_id,
            page=page,
            page_size=page_size,
            status_filter=status_filter
        )
        if not result:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="No orders found"
            )
        items = [OrderResponse(**item) for item in result["items"]]

        return OrdersSimpleListResponse(
            items=items,
            total=result["total"],
            page=result["page"],
            page_size=result["page_size"]
        )
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error getting orders: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="An error occurred while retrieving orders"
        )

# READ - Get orders for a customer (customer view)
@router.get("/customer", response_model=OrdersListResponse)
async def get_orders_by_customer(
    page: int = Query(1, ge=1, description="Page number"),
    page_size: int = Query(20, ge=1, le=100, description="Items per page"),
    status_filter: str = Query(None, description="Filter by order status"),
    current_user: UserResponse = Depends(get_current_user),
    orders_db: OrdersConnection = Depends(get_orders_db),
    business_db: BusinessConnection = Depends(BusinessConnection)
):
    """Get all orders for a specific customer with pagination (customer view)"""
    try:
        result = await orders_db.get_orders_by_customer(
            customer_id=current_user.id,
            page=page,
            page_size=page_size,
            status_filter=status_filter
        )

        if not result:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="No orders found"
            )

        orders_with_business = []
        for order in result["items"]:
            business = await business_db.get_business_by_id(order["business_id"])
            order["business"] = BusinessResponse(**business) if business else None
            orders_with_business.append(OrderWithBusinessResponse(**order))

        return OrdersListResponse(
            items=orders_with_business,
            total=result["total"],
            page=result["page"],
            page_size=result["page_size"]
        )
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error getting orders: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="An error occurred while retrieving orders"
        )

# READ - Get single order
@router.get("/{order_id}", response_model=OrderWithItemsResponse)
async def get_order(
    order_id: str,
    current_user: UserResponse = Depends(get_current_user),
    orders_db: OrdersConnection = Depends(get_orders_db)
):
    """Get a specific order by ID"""
    try:
        data = await orders_db.get_order_with_items_by_id(order_id)
        if not data:
            raise HTTPException(status_code=404, detail="Order not found")
        # Map order_items to requested format
        order_items = []
        for item in data.get("order_items", []):
            menu_item = item.get("menu_items")
            name = menu_item["name"] if isinstance(menu_item, dict) and "name" in menu_item else ""
            order_items.append(OrderItemWithMenuName(
                id=item["id"],
                order_id=item["order_id"],
                menu_item_id=item["menu_item_id"],
                name=name,
                quantity=item["quantity"],
                price_at_order=item["price_at_order"],
            ))
        return OrderWithItemsResponse(
            id=data["id"],
            customer_id=data["customer_id"],
            business_id=data["business_id"],
            total_amount=data["total_amount"],
            status=data["status"],
            created_at=data["created_at"],
            order_items=order_items
        )
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error retrieving order: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to retrieve order"
        )

# New endpoint: Get order with items and menu item names
@router.get("/with-items/{order_id}", response_model=OrderWithItemsResponse)
async def get_order_with_items(
    order_id: str,
    current_user: UserResponse = Depends(get_current_user),
    orders_db: OrdersConnection = Depends(get_orders_db)
):
    """Get an order by ID, including order items and their menu item names."""
    try:
        data = await orders_db.get_order_with_items_by_id(order_id)
        if not data:
            raise HTTPException(status_code=404, detail="Order not found")
        # Map order_items to requested format
        order_items = []
        for item in data.get("order_items", []):
            menu_item = item.get("menu_items")
            name = menu_item["name"] if isinstance(menu_item, dict) and "name" in menu_item else ""
            order_items.append(OrderItemWithMenuName(
                id=item["id"],
                order_id=item["order_id"],
                menu_item_id=item["menu_item_id"],
                name=name,
                quantity=item["quantity"],
                price_at_order=item["price_at_order"],
            ))
        return OrderWithItemsResponse(
            id=data["id"],
            customer_id=data["customer_id"],
            business_id=data["business_id"],
            total_amount=data["total_amount"],
            status=data["status"],
            created_at=data["created_at"],
            order_items=order_items
        )
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error retrieving order with items: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to retrieve order with items"
        )

# UPDATE - Update order (business owner can update status, customer can update pickup time)
@router.patch("/{order_id}", response_model=OrderResponse)
async def update_order(
    order_id: str,
    order_update: OrderUpdate,
    current_user: UserResponse = Depends(get_current_user),
    orders_db: OrdersConnection = Depends(get_orders_db)
):
    """Update a specific order"""
    try:
        # First verify the order exists
        order = await orders_db.get_order_by_id(order_id)
        if not order:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Order not found"
            )
        
        # Build update data based on user role
        update_data = {}
        
        if order_update.status is not None:
            update_data["status"] = order_update.status
            
        if not update_data:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="No fields provided for update"
            )
        
        # Update order
        result = await orders_db.update_order(order_id, update_data)
        
        if not result:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Failed to update order"
            )
        
        # Get updated order with items
        updated_order = await orders_db.get_order_by_id(order_id)
        
        return OrderResponse(**updated_order)
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error updating order: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="An error occurred while updating the order"
        )

# DELETE - Delete order (only business owners can delete)
@router.delete("/{order_id}", response_model=OrderDeleteResponse)
async def delete_order(
    order_id: str,
    current_user: UserResponse = Depends(get_current_user),
    orders_db: OrdersConnection = Depends(get_orders_db)
):
    """Delete a specific order (business owners only)"""
    try:
        # First verify the order exists and user owns the business
        if not await orders_db.verify_order_ownership(order_id, current_user.id):
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="You don't have permission to delete this order"
            )
        
        # Delete order
        result = await orders_db.delete_order(order_id)
        
        if not result:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Failed to delete order"
            )
        
        return OrderDeleteResponse(
            message="Order deleted successfully",
            deleted_id=order_id
        )
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error deleting order: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="An error occurred while deleting the order"
        )