from fastapi import APIRouter, HTTPException, Depends, status, Query
import logging
from typing import List
from app.core.config import settings
from app.api.dependencies.auth import get_current_user
from app.models.auth import UserResponse
from app.models.menu_items import (
    MenuItemCreate, 
    MenuItemUpdate, 
    MenuItemResponse, 
    MenuItemsListResponse,
    MenuItemDeleteResponse
)
from app.db.menu_items import MenuItemsConnection
from app.db.stock_level import StockLevelConnection

# Configure logging
logging.basicConfig(level=getattr(logging, settings.LOG_LEVEL))
logger = logging.getLogger(__name__)

router = APIRouter()

def get_menu_items_db() -> MenuItemsConnection:
    """Dependency to get MenuItemsConnection instance"""
    return MenuItemsConnection()

def get_stock_level_db() -> StockLevelConnection:
    """Dependency to get StockLevelConnection instance"""
    return StockLevelConnection()

# CREATE - Add new menu item
@router.post("/", response_model=MenuItemResponse, status_code=status.HTTP_201_CREATED)
async def create_menu_item(
    menu_item: MenuItemCreate,
    current_user: UserResponse = Depends(get_current_user),
    menu_items_db: MenuItemsConnection = Depends(get_menu_items_db),
    stock_level_db: StockLevelConnection = Depends(get_stock_level_db)
):
    """Create a new menu item for a business"""
    try:
        logger.info(f"Creating menu item for business {menu_item.business_id}")
        logger.debug(f"Menu item data: {menu_item.model_dump()}")
        # Verify user owns the business
        if not await menu_items_db.verify_business_ownership(menu_item.business_id, current_user.id):
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="You don't have permission to access this business"
            )
        
        # Create menu item
        menu_item_data = {
            "business_id": menu_item.business_id,
            "name": menu_item.name,
            "description": menu_item.description,
            "price": float(menu_item.price),
            "image_url": menu_item.image_url,
            "available": menu_item.available,
            "category": menu_item.category
        }
        
        result = await menu_items_db.create_menu_item(menu_item_data)

        stock_level_data = {
          "menu_item_id": result["id"],
          "quantity_available": menu_item.stock_level.quantity_available,
          "total_quantity": menu_item.stock_level.total_quantity
        }

        await stock_level_db.create_stock_level(stock_level_data)
        
        if not result:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Failed to create menu item"
            )
        
        return MenuItemResponse(**result)
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error creating menu item: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="An error occurred while creating the menu item"
        )

# READ - Get menu items for a business
@router.get("/business/{business_id}", response_model=MenuItemsListResponse)
async def get_menu_items_by_business(
    business_id: str,
    page: int = Query(1, ge=1, description="Page number"),
    page_size: int = Query(20, ge=1, le=100, description="Items per page"),
    available_only: bool = Query(False, description="Show only available items"),
    current_user: UserResponse = Depends(get_current_user),
    menu_items_db: MenuItemsConnection = Depends(get_menu_items_db)
):
    """Get all menu items for a specific business with pagination"""
    try:
        # Verify user owns the business
        if not await menu_items_db.verify_business_ownership(business_id, current_user.id):
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="You don't have permission to access this business"
            )
        
        # Get menu items with pagination
        result = await menu_items_db.get_menu_items_by_business(
            business_id=business_id,
            page=page,
            page_size=page_size,
            available_only=available_only
        )
        
        if not result:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="No menu items found"
            )
        
        items = [MenuItemResponse(**item) for item in result["items"]]
        
        return MenuItemsListResponse(
            items=items,
            total=result["total"],
            page=result["page"],
            page_size=result["page_size"]
        )
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error getting menu items: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="An error occurred while retrieving menu items"
        )

# READ - Get menu items for order form
@router.get("/order-form/{business_id}/", response_model=MenuItemsListResponse)
async def get_menu_items_for_order_form(
    business_id: str,
    current_user: UserResponse = Depends(get_current_user),
    menu_items_db: MenuItemsConnection = Depends(get_menu_items_db)
):
    """Get all menu items for a specific business with pagination"""
    try:
        # Get menu items with pagination
        result = await menu_items_db.get_menu_items_by_business(
            business_id=business_id,
            page=1,
            page_size=1000,
            available_only=True
        )
        
        items = [MenuItemResponse(**item) for item in result["items"]]
        
        return MenuItemsListResponse(
            items=items,
            total=result["total"],
            page=result["page"],
            page_size=result["page_size"]
        )
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error getting menu items for order form: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="An error occurred while retrieving menu items for order form"
        )

# READ - Get single menu item
@router.get("/{menu_item_id}", response_model=MenuItemResponse)
async def get_menu_item(
    menu_item_id: str,
    current_user: UserResponse = Depends(get_current_user),
    menu_items_db: MenuItemsConnection = Depends(get_menu_items_db)
):
    """Get a specific menu item by ID"""
    try:
        # Verify user owns the menu item
        if not await menu_items_db.verify_menu_item_ownership(menu_item_id, current_user.id):
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="You don't have permission to access this menu item"
            )
        
        # Get menu item
        menu_item = await menu_items_db.get_menu_item_by_id(menu_item_id)
        
        if not menu_item:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Menu item not found"
            )
        
        return MenuItemResponse(**menu_item)
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error getting menu item: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="An error occurred while retrieving the menu item"
        )

# UPDATE - Update menu item
@router.patch("/{menu_item_id}", response_model=MenuItemResponse)
async def update_menu_item(
    menu_item_id: str,
    menu_item_update: MenuItemUpdate,
    current_user: UserResponse = Depends(get_current_user),
    menu_items_db: MenuItemsConnection = Depends(get_menu_items_db)
):
    """Update a specific menu item"""
    try:
        # First verify the menu item exists and user owns it
        if not await menu_items_db.verify_menu_item_ownership(menu_item_id, current_user.id):
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="You don't have permission to access this menu item"
            )
        
        # Build update data (only include fields that are not None)
        update_data = {}
        if menu_item_update.name is not None:
            update_data["name"] = menu_item_update.name
        if menu_item_update.description is not None:
            update_data["description"] = menu_item_update.description
        if menu_item_update.price is not None:
            update_data["price"] = float(menu_item_update.price)
        if menu_item_update.image_url is not None:
            update_data["image_url"] = menu_item_update.image_url
        if menu_item_update.available is not None:
            update_data["available"] = menu_item_update.available
        if menu_item_update.category is not None:
            update_data["category"] = menu_item_update.category
        
        if not update_data:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="No fields provided for update"
            )
        
        # Update menu item
        result = await menu_items_db.update_menu_item(menu_item_id, update_data)
        
        if not result:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Failed to update menu item"
            )
        
        return MenuItemResponse(**result)
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error updating menu item: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="An error occurred while updating the menu item"
        )

# DELETE - Delete menu item
@router.delete("/{menu_item_id}", response_model=MenuItemDeleteResponse)
async def delete_menu_item(
    menu_item_id: str,
    current_user: UserResponse = Depends(get_current_user),
    menu_items_db: MenuItemsConnection = Depends(get_menu_items_db)
):
    """Delete a specific menu item"""
    try:
        # First verify the menu item exists and user owns it
        if not await menu_items_db.verify_menu_item_ownership(menu_item_id, current_user.id):
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="You don't have permission to access this menu item"
            )
        
        # Delete menu item
        result = await menu_items_db.delete_menu_item(menu_item_id)
        
        if not result:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Failed to delete menu item"
            )
        
        return MenuItemDeleteResponse(
            message="Menu item deleted successfully",
            deleted_id=menu_item_id
        )
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error deleting menu item: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="An error occurred while deleting the menu item"
        )

# SEARCH - Search menu items
@router.get("/business/{business_id}/search", response_model=List[MenuItemResponse])
async def search_menu_items(
    business_id: str,
    q: str = Query(..., min_length=1, description="Search term"),
    available_only: bool = Query(False, description="Show only available items"),
    limit: int = Query(20, ge=1, le=100, description="Maximum number of results"),
    current_user: UserResponse = Depends(get_current_user),
    menu_items_db: MenuItemsConnection = Depends(get_menu_items_db)
):
    """Search menu items by name or description"""
    try:
        # Verify user owns the business
        if not await menu_items_db.verify_business_ownership(business_id, current_user.id):
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="You don't have permission to access this business"
            )
        
        # Search menu items
        results = await menu_items_db.search_menu_items(
            business_id=business_id,
            search_term=q,
            available_only=available_only,
            limit=limit
        )
        
        return [MenuItemResponse(**item) for item in results]
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error searching menu items: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="An error occurred while searching menu items"
        )