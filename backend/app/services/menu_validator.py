import logging
import json
from typing import Dict, List, Optional, Tuple
from app.db.menu_items import MenuItemsConnection

logger = logging.getLogger(__name__)

class MenuValidator:
    """Service to validate that AI responses only contain actual menu items"""
    
    def __init__(self):
        self.menu_db = MenuItemsConnection()
        self._menu_cache = {}
    
    def get_business_menu_items(self, business_id: str) -> List[Dict]:
        """Get menu items for a business (synchronous wrapper)"""
        try:
            import asyncio
            
            # Check if we're already in an event loop
            try:
                loop = asyncio.get_running_loop()
                # We're in an event loop, can't use run_until_complete
                logger.warning("Cannot get menu items - already in event loop")
                # Return empty list instead of failing completely
                return []
            except RuntimeError:
                # No event loop running, we can create one
                loop = asyncio.new_event_loop()
                asyncio.set_event_loop(loop)
                
                try:
                    # Get menu items
                    menu_data = loop.run_until_complete(
                        self.menu_db.get_menu_items_by_business(
                            business_id=business_id,
                            page=1,
                            page_size=1000,
                            available_only=True
                        )
                    )
                    
                    if menu_data and menu_data.get("items"):
                        return menu_data["items"]
                    return []
                finally:
                    loop.close()
            
        except Exception as e:
            logger.error(f"Error getting menu items for business {business_id}: {e}")
            return []
    
    async def get_business_menu_items_async(self, business_id: str) -> List[Dict]:
        """Get menu items for a business (async version)"""
        try:
            menu_data = await self.menu_db.get_menu_items_by_business(
                business_id=business_id,
                page=1,
                page_size=1000,
                available_only=True
            )
            
            if menu_data and menu_data.get("items"):
                return menu_data["items"]
            return []
            
        except Exception as e:
            logger.error(f"Error getting menu items for business {business_id}: {e}")
            return []
    
    async def validate_response_async(self, response: str, business_id: str) -> Tuple[bool, str, List[str]]:
        """
        Validate that a response only contains actual menu items.
        
        Returns:
            (is_valid, corrected_response, available_items)
        """
        try:
            # Get menu items from database for the actual business
            # Try async first, fallback to sync
            try:
                import asyncio
                loop = asyncio.get_running_loop()
                # We're in an event loop, use async version
                menu_items = await self.get_business_menu_items_async(business_id)
            except RuntimeError:
                # No event loop, use sync version
                menu_items = self.get_business_menu_items(business_id)
            
            if not menu_items:
                # If we can't get menu items, just allow the response to pass through
                # This prevents blocking responses when menu access fails
                logger.warning(f"No menu items found for business {business_id}, allowing response to pass through")
                return True, response, []
            
            # Extract available item names
            available_items = [item["name"].lower() for item in menu_items]
            available_items_with_prices = [f"{item['name']} (₱{item['price']})" for item in menu_items]
            
            # Common generic items that shouldn't be mentioned unless in menu
            generic_items = [
                "classic", "grilled", "veggie", "bacon", "mushroom", "swiss", 
                "beef", "chicken", "cheese", "burger", "sandwich", "deluxe",
                "supreme", "premium", "signature", "special", "original",
                # Coffee-specific generic terms
                "espresso shot", "cappuccino", "latte", "americano", "mocha",
                "flat white", "cold brew", "affogato", "cortado", "macchiato"
            ]
            
            response_lower = response.lower()
            non_menu_items = []
            
            # Check for generic items not in menu
            for generic in generic_items:
                if generic in response_lower:
                    # Check if this generic term is actually in the menu
                    if not any(generic in item for item in available_items):
                        # Check if the response is explaining that the item is NOT available
                        # This prevents false positives when AI correctly says something isn't available
                        negative_indicators = [
                            "doesn't", "don't", "not available", "not on", "not in", 
                            "doesn't have", "don't have", "not currently", "not feature",
                            "doesn't currently", "don't currently", "not offer", "doesn't offer"
                        ]
                        
                        # If the response contains negative indicators, it's likely explaining that something is NOT available
                        has_negative_indicator = any(indicator in response_lower for indicator in negative_indicators)
                        
                        # Only flag as non-menu item if it's not explaining unavailability
                        if not has_negative_indicator:
                            non_menu_items.append(generic)
            
            # If non-menu items found, create corrected response
            if non_menu_items:
                logger.warning(f"Response contains non-menu items: {non_menu_items}")
                
                # Check if the response is about adding items to cart or order confirmation
                cart_indicators = [
                    "added", "add", "cart", "order", "confirm", "placed", "added to your cart",
                    "added to your order", "added to cart", "added to order", "i've added"
                ]
                
                has_cart_indicator = any(indicator in response_lower for indicator in cart_indicators)
                
                # If the response is about adding items to cart and contains valid menu items, allow it
                if has_cart_indicator:
                    # Check if the response contains actual menu items
                    has_menu_items = any(item["name"].lower() in response_lower for item in menu_items)
                    if has_menu_items:
                        logger.info("Response contains cart operations with valid menu items - allowing")
                        return True, response, available_items_with_prices
                
                # Create corrected response with actual menu items
                corrected_response = "I'm sorry, but I can only recommend items that are actually available on our menu. "
                
                if available_items_with_prices:
                    # Group by category
                    categories = {}
                    for item in menu_items:
                        category = item.get("category", "Other")
                        if category not in categories:
                            categories[category] = []
                        categories[category].append(f"{item['name']} (₱{item['price']})")
                    
                    corrected_response += "Here are our available items:\n"
                    for category, items in categories.items():
                        corrected_response += f"\n{category}:\n"
                        for item in items:
                            corrected_response += f"- {item}\n"
                else:
                    corrected_response += "Please ask a staff member for our current menu."
                
                return False, corrected_response, available_items_with_prices
            
            return True, response, available_items_with_prices
            
        except Exception as e:
            logger.error(f"Error validating menu response: {e}")
            return False, "I'm sorry, but I encountered an error. Please ask a staff member for assistance.", []
    
    def validate_response(self, response: str, business_id: str) -> Tuple[bool, str, List[str]]:
        """Synchronous wrapper for validate_response_async"""
        try:
            import asyncio
            loop = asyncio.get_running_loop()
            # We're in an event loop, can't use run_until_complete
            logger.warning("Cannot validate response - already in event loop")
            # Instead of failing, try to get menu items directly
            try:
                menu_items = self.get_business_menu_items(business_id)
                if not menu_items:
                    # If we can't get menu items, just allow the response to pass through
                    return True, response, []
                
                # Extract available item names
                available_items = [item["name"].lower() for item in menu_items]
                available_items_with_prices = [f"{item['name']} (₱{item['price']})" for item in menu_items]
                
                # Simple validation without complex logic
                response_lower = response.lower()
                
                # Check if response contains any menu items
                has_menu_items = any(item["name"].lower() in response_lower for item in menu_items)
                
                if has_menu_items:
                    return True, response, available_items_with_prices
                else:
                    # If no menu items found, just allow the response to pass through
                    return True, response, available_items_with_prices
                    
            except Exception as e:
                logger.error(f"Error in sync validation: {e}")
                return True, response, []  # Allow response to pass through
                
        except RuntimeError:
            # No event loop running, we can create one
            loop = asyncio.new_event_loop()
            asyncio.set_event_loop(loop)
            
            try:
                return loop.run_until_complete(self.validate_response_async(response, business_id))
            finally:
                loop.close()
    
    def get_menu_summary(self, business_id: str) -> str:
        """Get a formatted summary of available menu items"""
        try:
            menu_items = self.get_business_menu_items(business_id)
            
            if not menu_items:
                return "No menu items available."
            
            # Group by category
            categories = {}
            for item in menu_items:
                category = item.get("category", "Other")
                if category not in categories:
                    categories[category] = []
                categories[category].append(f"{item['name']} (₱{item['price']})")
            
            summary = "Available Menu Items:\n"
            for category, items in categories.items():
                summary += f"\n{category}:\n"
                for item in items:
                    summary += f"- {item}\n"
            
            return summary
            
        except Exception as e:
            logger.error(f"Error getting menu summary: {e}")
            return "Menu information unavailable."

# Singleton instance
menu_validator = MenuValidator() 