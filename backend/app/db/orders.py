import logging
from supabase import Client, create_client
from typing import Dict, Any, List

from app.core.config import settings

logger = logging.getLogger(__name__)


class OrdersConnection:
    def __init__(self):
        self.supabase: Client = create_client(
            settings.SUPABASE_URL, settings.SUPABASE_KEY
        )

    async def create_order(self, order_data: Dict[str, Any]):
        """Create a new order"""
        try:
            response = (
                self.supabase.table("orders")
                .insert(order_data)
                .execute()
            )

            if not response.data:
                return None

            return response.data[0]

        except Exception as e:
            logger.error(f"Error creating order: {str(e)}")
            return None

    async def get_order_by_id(self, order_id: str):
        """Get an order by ID (order items should be fetched separately)"""
        try:
            order_response = (
                self.supabase.table("orders")
                .select("*")
                .eq("id", str(order_id))
                .single()
                .execute()
            )
            if not order_response.data:
                return None
            order_data = order_response.data
            # Note: order items should be fetched using db/order_items.py
            return order_data
        except Exception as e:
            logger.error(f"Error fetching order: {str(e)}")
            return None

    async def get_order_with_items_by_id(self, order_id: str):
        """Get an order by ID, including order items and their menu items (inner join)"""
        try:
            order_response = (
                self.supabase.table("orders")
                .select("*, order_items(*, menu_items(*))")
                .eq("id", str(order_id))
                .single()
                .execute()
            )
            if not order_response.data:
                return None
            order_data = order_response.data
            return order_data
        except Exception as e:
            logger.error(f"Error fetching order with items: {str(e)}")
            return None

    async def get_order_with_business(self, order_id: str):
        """Get an order with business information for ownership verification"""
        try:
            response = (
                self.supabase.table("orders")
                .select("*")
                .eq("id", str(order_id))
                .single()
                .execute()
            )

            if not response.data:
                return None

            return response.data

        except Exception as e:
            logger.error(f"Error fetching order with business: {str(e)}")
            return None

    async def get_orders_by_business(
        self,
        business_id: str,
        page: int = 1,
        page_size: int = 20,
        status_filter: str = None
    ):
        """Get orders for a specific business with pagination"""
        try:
            query = (
                self.supabase.table("orders")
                .select("*", count="exact")
                .eq("business_id", str(business_id))
            )
            
            if status_filter:
                query = query.eq("status", status_filter)
            
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
            logger.error(f"Error fetching orders by business: {str(e)}")
            return None

    async def get_orders_by_customer(
        self,
        customer_id: str,
        page: int = 1,
        page_size: int = 20,
        status_filter: str = None
    ):
        """Get orders for a specific customer with pagination"""
        try:
            query = (
                self.supabase.table("orders")
                .select("*", count="exact")
                .eq("customer_id", str(customer_id))
            )
            
            if status_filter:
                query = query.eq("status", status_filter)
            
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
            logger.error(f"Error fetching orders by customer: {str(e)}")
            return None

    async def update_order(self, order_id: str, update_data: Dict[str, Any]):
        """Update an order"""
        try:
            response = (
                self.supabase.table("orders")
                .update(update_data)
                .eq("id", str(order_id))
                .execute()
            )

            if not response.data:
                return None

            return response.data[0]

        except Exception as e:
            logger.error(f"Error updating order: {str(e)}")
            return None

    async def delete_order(self, order_id: str):
        """Delete an order (order items should be deleted separately)"""
        try:
            # Note: order items should be deleted using db/order_items.py before deleting the order
            response = (
                self.supabase.table("orders")
                .delete()
                .eq("id", str(order_id))
                .execute()
            )
            if not response.data:
                return None
            return response.data[0]
        except Exception as e:
            logger.error(f"Error deleting order: {str(e)}")
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

    async def verify_order_ownership(self, order_id: str, user_id: str):
        """Verify that a user owns the business that contains this order"""
        try:
            order = await self.get_order_with_business(order_id)
            if not order:
                return False

            return order["businesses"]["owner_id"] == str(user_id)

        except Exception as e:
            logger.error(f"Error verifying order ownership: {str(e)}")
            return False

    async def verify_customer_order_access(self, order_id: str, user_id: str):
        """Verify that a user is the customer who placed this order"""
        try:
            response = (
                self.supabase.table("orders")
                .select("customer_id")
                .eq("id", str(order_id))
                .single()
                .execute()
            )

            if not response.data:
                return False

            return response.data["customer_id"] == str(user_id)

        except Exception as e:
            logger.error(f"Error verifying customer order access: {str(e)}")
            return False 