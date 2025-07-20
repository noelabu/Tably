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
        Returns a JSON string containing the menu information.
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
                return json.dumps({
                    "error": "No menu items available at this time.",
                    "business_id": business_id
                })
            
            # Format menu items for AI consumption
            formatted_menu = self._format_menu_for_ai(menu_data["items"])
            
            # Get business information
            business_info = await self._get_business_info(business_id)
            
            # Create list of available items for the note
            available_items_list = []
            for item in menu_data["items"]:
                available_items_list.append(f"{item['name']} (₱{item['price']})")
            available_items_text = ", ".join(available_items_list)
            
            # Create structured response
            context = {
                "business_id": business_id,
                "business_info": business_info,
                "menu_items": formatted_menu,
                "total_items": len(menu_data["items"]),
                "note": f"CRITICAL: You are ONLY allowed to mention, recommend, or suggest items that are explicitly listed in this menu. NEVER suggest items that are not in this menu. Use exact item names and prices as shown. If a customer asks for something not listed, politely inform them it's not available and suggest alternatives from this menu only. NEVER mention generic food items like 'pizza', 'burger', 'coffee', 'dessert', 'salad', 'pasta' unless they are specifically listed in this menu. If you don't have access to menu data, say 'I'm sorry, but I don't have access to the current menu. Please ask a staff member for assistance.' AVAILABLE ITEMS ONLY: You must ONLY mention these exact items: {available_items_text}.",
                "explicit_menu_items": available_items_text,
                "menu_restrictions": f"ABSOLUTE RESTRICTION: You are FORBIDDEN from mentioning any items not in this list: {available_items_text}. Use ONLY these exact item names and prices."
            }
            
            return json.dumps(context, indent=2)
            
        except Exception as e:
            logger.error(f"Error fetching menu context: {str(e)}")
            return json.dumps({
                "error": "Unable to fetch menu information at this time.",
                "business_id": business_id,
                "details": str(e)
            })
    
    def _format_menu_for_ai(self, menu_items: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Format menu items into structured data for AI processing"""
        
        # Group items by category
        categories = {}
        for item in menu_items:
            category = item.get("category") or "Other"
            if category not in categories:
                categories[category] = []
            
            # Clean and structure the item data
            formatted_item = {
                "id": item.get("id"),
                "name": item.get('name', 'Unknown Item'),
                "price": float(item.get('price', 0)),
                "description": item.get('description') or 'No description available',
                "available": item.get('available', True)
            }
            
            # Add optional fields if they exist
            if item.get('dietary_info'):
                formatted_item["dietary_info"] = item.get('dietary_info')
            
            if item.get('allergens'):
                formatted_item["allergens"] = item.get('allergens')
            
            if item.get('preparation_time'):
                formatted_item["preparation_time"] = item.get('preparation_time')
            
            if item.get('calories'):
                formatted_item["calories"] = item.get('calories')
            
            if item.get('spice_level'):
                formatted_item["spice_level"] = item.get('spice_level')
            
            categories[category].append(formatted_item)
        
        return categories
    
    async def _get_business_info(self, business_id: str) -> Dict[str, Any]:
        """Get business information"""
        try:
            response = (
                self.supabase.table("businesses")
                .select("name, description, cuisine_type")
                .eq("id", business_id)
                .single()
                .execute()
            )
            
            if not response.data:
                return {
                    "error": "Restaurant information not available.",
                    "name": "Unknown",
                    "cuisine_type": "Various",
                    "description": "No description available"
                }
            
            business = response.data
            return {
                "name": business.get('name') or 'Unknown',
                "cuisine_type": business.get('cuisine_type') or 'Various',
                "description": business.get('description') or 'No description available'
            }
            
        except Exception as e:
            logger.error(f"Error fetching business info: {str(e)}")
            return {
                "error": "Restaurant information not available.",
                "name": "Unknown",
                "cuisine_type": "Various",
                "description": "No description available"
            }
    
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