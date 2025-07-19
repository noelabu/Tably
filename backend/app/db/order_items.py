import logging
from supabase import Client, create_client
from typing import Dict, Any, List
from app.core.config import settings

logger = logging.getLogger(__name__)

class OrderItemsConnection:
    def __init__(self):
        self.supabase: Client = create_client(
            settings.SUPABASE_URL, settings.SUPABASE_KEY
        )

    async def create_order_items(self, order_items_data: List[Dict[str, Any]]):
        """Create order items for an order"""
        try:
            response = (
                self.supabase.table("order_items")
                .insert(order_items_data)
                .execute()
            )
            if not response.data:
                return None
            return response.data
        except Exception as e:
            logger.error(f"Error creating order items: {str(e)}")
            return None

    async def get_order_items_by_order_id(self, order_id: str):
        """Get order items for a specific order"""
        try:
            response = (
                self.supabase.table("order_items")
                .select("*, menu_items(name, price)")
                .eq("order_id", str(order_id))
                .execute()
            )
            return response.data if response.data else []
        except Exception as e:
            logger.error(f"Error fetching order items: {str(e)}")
            return []

    async def delete_order_items_by_order_id(self, order_id: str):
        """Delete all order items for a specific order"""
        try:
            await self.supabase.table("order_items").delete().eq("order_id", str(order_id)).execute()
            return True
        except Exception as e:
            logger.error(f"Error deleting order items: {str(e)}")
            return False
