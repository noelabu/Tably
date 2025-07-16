import logging
from supabase import Client, create_client
from typing import Dict, Any

from app.core.config import settings

logger = logging.getLogger(__name__)

class BusinessConnection:
  def __init__(self):
    self.supabase: Client = create_client(
      settings.SUPABASE_URL, settings.SUPABASE_KEY
    )

  async def create_business(self, business_data: Dict[str, Any]):
    """Create a new business"""
    try:
      response = (
        self.supabase.table("businesses")
        .insert(business_data)
        .execute()
      )
      
      if not response.data:
        return None
      
      return response.data[0]
    
    except Exception as e:
      logger.error(f"Error creating business: {str(e)}")
      return None

  async def get_business_by_id(self, business_id: str):
    """Get a business by ID"""
    try:
      response = (
        self.supabase.table("businesses")
        .select("*")
        .eq("id", business_id)
        .execute()
      )

      if not response.data:
        return None
      
      return response.data[0]
    
    except Exception as e:
      logger.error(f"Error fetching business: {str(e)}")
      return None

  async def get_business_by_owner_id(self, owner_id: str):
    """Get a business by owner ID"""
    try:
      response = (
        self.supabase.table("businesses")
        .select("*")
        .eq("owner_id", owner_id)
        .execute()
      )

      if not response.data:
        return None
      
      return response.data[0]
    
    except Exception as e:
      logger.error(f"Error fetching business: {str(e)}")
      return None

  async def verify_business_ownership(self, business_id: str, owner_id: str):
    """Verify if a business belongs to an owner"""
    try:
      response = (
        self.supabase.table("businesses")
        .select("*")
        .eq("id", business_id)  
        .eq("owner_id", owner_id)
        .execute()
      )
      
      return response.data is not None
    
    except Exception as e:  
      logger.error(f"Error verifying business ownership: {str(e)}")
      return False
      
  async def update_business(self, business_id: str, update_data: Dict[str, Any]):
    """Update a business"""
    try:
      response = (
        self.supabase.table("businesses")
        .update(update_data)
        .eq("id", business_id)
        .execute()
      )

      if not response.data:
        return None
      
      return response.data[0]
    
    except Exception as e:
      logger.error(f"Error updating business: {str(e)}")
      return None

  async def get_all_businesses(self, page: int = 1, page_size: int = 20):
    """Get all businesses with pagination (for customers to browse)"""
    try:
      # Calculate offset
      offset = (page - 1) * page_size
      
      # Get total count
      count_response = (
        self.supabase.table("businesses")
        .select("*", count="exact")
        .execute()
      )
      total = count_response.count if count_response.count is not None else 0
      
      # Get businesses with pagination
      response = (
        self.supabase.table("businesses")
        .select("*")
        .range(offset, offset + page_size - 1)
        .order("created_at", desc=True)
        .execute()
      )

      if not response.data:
        return {
          "items": [],
          "total": total,
          "page": page,
          "page_size": page_size
        }
      
      return {
        "items": response.data,
        "total": total,
        "page": page,
        "page_size": page_size
      }
    
    except Exception as e:
      logger.error(f"Error fetching businesses: {str(e)}")
      return None
      
