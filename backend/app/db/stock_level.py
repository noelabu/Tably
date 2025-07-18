import logging
from supabase import Client, create_client
from typing import Dict, Any

from app.core.config import settings

logger = logging.getLogger(__name__)

class StockLevelConnection:
  def __init__(self):
    self.supabase: Client = create_client(
      settings.SUPABASE_URL, settings.SUPABASE_KEY
    )
  
  async def create_stock_level(self, stock_level_data: Dict[str, Any]):
    """Create a new stock level"""
    try:
      response = (
        self.supabase.table("stock_levels")
        .insert(stock_level_data)
        .execute()
      )
      
      if not response.data:
        return None
      
      return response.data[0]
    
    except Exception as e:
      logger.error(f"Error creating stock level: {str(e)}")
      return None
    
  async def get_stock_level_by_menu_item_id(self, menu_item_id: str):
    """Get a stock level by menu item ID"""
    try:
      response = (
        self.supabase.table("stock_levels")
        .select("*")
        .eq("menu_item_id", menu_item_id)
        .execute()
      )

      return response.data[0]
    
    except Exception as e:
      logger.error(f"Error getting stock level by menu item ID: {str(e)}")
      return None
      
  async def update_stock_level(self, stock_level_data: Dict[str, Any]):
    """Update a stock level"""
    try:
      response = (
        self.supabase.table("stock_levels")
        .update(stock_level_data)
        .eq("id", stock_level_data["id"])
        .execute()
      )
      
      return response.data[0]
    
    except Exception as e:
      logger.error(f"Error updating stock level: {str(e)}")
      return None
      
