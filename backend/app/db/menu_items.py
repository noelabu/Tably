import logging
from supabase import Client, create_client
from typing import Dict, Any

from app.core.config import settings

logger = logging.getLogger(__name__)


class MenuItemsConnection:
    def __init__(self):
        self.supabase: Client = create_client(
            settings.SUPABASE_URL, settings.SUPABASE_KEY
        )

    async def create_menu_item(self, menu_item_data: Dict[str, Any]):
        """Create a new menu item"""
        try:
            response = (
                self.supabase.table("menu_items")
                .insert(menu_item_data)
                .execute()
            )

            if not response.data:
                return None

            return response.data[0]

        except Exception as e:
            logger.error(f"Error creating menu item: {str(e)}")
            return None

    async def get_menu_item_by_id(self, menu_item_id: str):
        """Get a menu item by ID"""
        try:
            response = (
                self.supabase.table("menu_items")
                .select("*")
                .eq("id", str(menu_item_id))
                .single()
                .execute()
            )

            if not response.data:
                return None

            return response.data

        except Exception as e:
            logger.error(f"Error fetching menu item: {str(e)}")
            return None

    async def get_menu_item_with_business(self, menu_item_id: str):
        """Get a menu item with business information for ownership verification"""
        try:
            response = (
                self.supabase.table("menu_items")
                .select("*, businesses(owner_id)")
                .eq("id", str(menu_item_id))
                .single()
                .execute()
            )

            if not response.data:
                return None

            return response.data

        except Exception as e:
            logger.error(f"Error fetching menu item with business: {str(e)}")
            return None

    async def get_menu_items_by_business(
        self,
        business_id: str,
        page: int = 1,
        page_size: int = 20,
        available_only: bool = False
    ):
        """Get menu items for a specific business with pagination"""
        try:
            query = (
                self.supabase.table("menu_items")
                .select("*", count="exact")
                .eq("business_id", str(business_id))
            )
            
            if available_only:
                query = query.eq("available", True)
            
            # Apply pagination
            offset = (page - 1) * page_size
            query = query.range(offset, offset + page_size - 1).order("created_at", desc=True)
            
            response = query.execute()
            
            return {
                "items": response.data,
                "total": response.count or 0,
                "page": page,
                "page_size": page_size
            }

        except Exception as e:
            logger.error(f"Error fetching menu items by business: {str(e)}")
            return None

    async def update_menu_item(self, menu_item_id: str, update_data: Dict[str, Any]):
        """Update a menu item"""
        try:
            response = (
                self.supabase.table("menu_items")
                .update(update_data)
                .eq("id", str(menu_item_id))
                .execute()
            )

            if not response.data:
                return None

            return response.data[0]

        except Exception as e:
            logger.error(f"Error updating menu item: {str(e)}")
            return None

    async def delete_menu_item(self, menu_item_id: str):
        """Delete a menu item"""
        try:
            response = (
                self.supabase.table("menu_items")
                .delete()
                .eq("id", str(menu_item_id))
                .execute()
            )

            if not response.data:
                return None

            return response.data[0]

        except Exception as e:
            logger.error(f"Error deleting menu item: {str(e)}")
            return None

    async def verify_business_ownership(self, business_id: str, user_id: str):
        """Verify that a user owns a specific business"""
        try:
            response = (
                self.supabase.table("businesses")
                .select("owner_id")
                .eq("id", str(business_id))
                .execute()
            )

            if not response.data:
                return False

            return response.data[0]["owner_id"] == str(user_id)

        except Exception as e:
            logger.error(f"Error verifying business ownership: {str(e)}")
            return False

    async def verify_menu_item_ownership(self, menu_item_id: str, user_id: str):
        """Verify that a user owns the business that contains this menu item"""
        try:
            menu_item = await self.get_menu_item_with_business(menu_item_id)
            if not menu_item:
                return False

            return menu_item["businesses"]["owner_id"] == str(user_id)

        except Exception as e:
            logger.error(f"Error verifying menu item ownership: {str(e)}")
            return False

    async def search_menu_items(
        self,
        business_id: str,
        search_term: str,
        available_only: bool = False,
        limit: int = 20
    ):
        """Search menu items by name or description"""
        try:
            query = (
                self.supabase.table("menu_items")
                .select("*")
                .eq("business_id", str(business_id))
            )
            
            if available_only:
                query = query.eq("available", True)
            
            # Supabase text search (using ilike for case-insensitive search)
            query = (
                query.or_(f"name.ilike.%{search_term}%,description.ilike.%{search_term}%")
                .limit(limit)
                .order("created_at", desc=True)
            )
            
            response = query.execute()
            
            if not response.data:
                return []

            return response.data

        except Exception as e:
            logger.error(f"Error searching menu items: {str(e)}")
            return []