import logging
from typing import Dict, Any, Optional, List
import json
from app.db.menu_items import MenuItemsConnection
from app.core.supabase import get_supabase_client

logger = logging.getLogger(__name__)

class MenuContextService:
    """Service to provide menu context for AI agents"""
    
    def __init__(self):
        self.menu_db = MenuItemsConnection()
        self.supabase = get_supabase_client()
    
    async def get_business_menu_context(self, business_id: str) -> str:
        """
        Fetch and format menu data for a specific business to be used by AI agents.
        Returns a formatted string containing the menu information.
        """
        try:
            # Get all available menu items for the business
            menu_data = await self.menu_db.get_menu_items_by_business(
                business_id=business_id,
                page=1,
                page_size=1000,  # Get all items
                available_only=True  # Only get available items
            )
            
            if not menu_data or not menu_data.get("items"):
                return "No menu items available at this time."
            
            # Format menu items for AI consumption
            menu_context = self._format_menu_for_ai(menu_data["items"])
            
            # Get business information
            business_info = await self._get_business_info(business_id)
            
            # Combine business info and menu
            full_context = f"""
RESTAURANT INFORMATION:
{business_info}

CURRENT MENU:
{menu_context}

Note: Only recommend items from this menu. Prices and availability are current.
"""
            return full_context
            
        except Exception as e:
            logger.error(f"Error fetching menu context: {str(e)}")
            return "Unable to fetch menu information at this time."
    
    def _format_menu_for_ai(self, menu_items: List[Dict[str, Any]]) -> str:
        """Format menu items into a structured string for AI processing"""
        
        # Group items by category
        categories = {}
        for item in menu_items:
            category = item.get("category") or "Other"
            if category not in categories:
                categories[category] = []
            categories[category].append(item)
        
        # Format the menu
        formatted_menu = []
        for category, items in categories.items():
            formatted_menu.append(f"\n{category.upper()}:")
            formatted_menu.append("-" * 40)
            
            for item in items:
                name = item.get('name', 'Unknown Item')
                price = item.get('price', 0)
                description = item.get('description') or 'No description available'
                
                item_text = f"""
{name} - ${price:.2f}
{description}
"""
                dietary_info = item.get('dietary_info')
                if dietary_info:
                    item_text += f"Dietary Info: {dietary_info}\n"
                
                allergens = item.get('allergens')
                if allergens:
                    item_text += f"Allergens: {allergens}\n"
                
                prep_time = item.get('preparation_time')
                if prep_time:
                    item_text += f"Prep Time: {prep_time} minutes\n"
                
                formatted_menu.append(item_text)
        
        return "\n".join(formatted_menu)
    
    async def _get_business_info(self, business_id: str) -> str:
        """Get business information"""
        try:
            response = (
                self.supabase.table("businesses")
                .select("name, description, cuisine_type, operating_hours")
                .eq("id", business_id)
                .single()
                .execute()
            )
            
            if not response.data:
                return "Restaurant information not available."
            
            business = response.data
            name = business.get('name') or 'Unknown'
            cuisine = business.get('cuisine_type') or 'Various'
            description = business.get('description') or 'No description available'
            hours = business.get('operating_hours') or 'Hours not specified'
            
            return f"""
Name: {name}
Cuisine: {cuisine}
Description: {description}
Hours: {hours}
"""
        except Exception as e:
            logger.error(f"Error fetching business info: {str(e)}")
            return "Restaurant information not available."
    
    async def get_menu_item_details(self, business_id: str, item_name: str) -> Optional[Dict[str, Any]]:
        """Get detailed information about a specific menu item"""
        try:
            items = await self.menu_db.search_menu_items(
                business_id=business_id,
                search_term=item_name,
                available_only=True,
                limit=1
            )
            
            if items:
                return items[0]
            return None
            
        except Exception as e:
            logger.error(f"Error fetching menu item details: {str(e)}")
            return None

# Singleton instance
menu_context_service = MenuContextService()