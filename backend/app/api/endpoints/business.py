from fastapi import APIRouter, HTTPException, Depends, status, Form, Query
import logging
from typing import List
from app.core.config import settings
from app.api.dependencies.auth import get_current_user
from app.models.auth import UserResponse
from app.models.business import (
    BusinessCreate,
    BusinessUpdate,
    BusinessResponse,
    BusinessesListResponse,
    BusinessDeleteResponse
)
from app.db.business import BusinessConnection

# Configure logging
logging.basicConfig(level=getattr(logging, settings.LOG_LEVEL))
logger = logging.getLogger(__name__)

router = APIRouter()

def get_business_db() -> BusinessConnection:
    """Dependency to get BusinessConnection instance"""
    return BusinessConnection()

# CREATE - Add new business
@router.post("/", response_model=BusinessResponse, status_code=status.HTTP_201_CREATED)
async def create_business(
    business: BusinessCreate,
    current_user: UserResponse = Depends(get_current_user),
    business_db: BusinessConnection = Depends(get_business_db)
):
    """Create a new business"""
    try:
      logger.info(f"Creating business for user {current_user.id}")
      logger.debug(f"Business data: {business.model_dump()}")
      # Verify user is authenticated
      if not current_user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="You must be logged in to create a business"
        )
      # Create business
      business_data = {
        "name": business.name,
        "address": business.address,
        "city": business.city,
        "state": business.state,
        "zip_code": business.zip_code,
        "phone": business.phone,
        "email": business.email,
        "cuisine_type": business.cuisine_type,
        "open_time": business.open_time,
        "close_time": business.close_time,
        "owner_id": current_user.id,
      }

      result = await business_db.create_business(business_data)
      if not result:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Failed to create business"
        )
      return BusinessResponse(**result)

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error creating business: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to create business"
        )

# READ - Get business by owner (current user)
@router.get("/my", response_model=BusinessResponse)
async def get_business(
    current_user: UserResponse = Depends(get_current_user),
    business_db: BusinessConnection = Depends(get_business_db)
):
    """Get the business for the current user (owner)"""
    try:
        logger.info(f"Getting business for owner {current_user.id}")
        result = await business_db.get_business_by_owner_id(current_user.id)
        if not result:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="No business found for this owner"
            )
        return BusinessResponse(**result)
    except Exception as e:
        logger.error(f"Error getting business: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to get business"
        )

# UPDATE - Update business
@router.patch("/{business_id}", response_model=BusinessResponse)
async def update_business(
    business_id: str,
    business_update: BusinessUpdate,
    current_user: UserResponse = Depends(get_current_user),
    business_db: BusinessConnection = Depends(get_business_db)
):
    """Update a business"""
    try:
      logger.info(f"Updating business {business_id} for user {current_user.id}")
      # Verify user is authenticated
      if not current_user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="You must be logged in to update a business"
        )

      # Build update data (only include fields that are not None)
      update_data = {}
      if business_update.name is not None:
        update_data["name"] = business_update.name
      if business_update.address is not None:
        update_data["address"] = business_update.address
      if business_update.city is not None:
        update_data["city"] = business_update.city
      if business_update.state is not None:
        update_data["state"] = business_update.state
      
      if not update_data:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="No fields provided for update"
        )

      # Update business if it exists and user owns it
      if not await business_db.verify_business_ownership(business_id, current_user.id):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail=f"You don't have permission to update this business {business_id} for user {current_user.id}"
        )
      
      result = await business_db.update_business(business_id, update_data)

      if not result:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Failed to update business"
        )
      return BusinessResponse(**result)
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error updating business: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="An error occurred while updating the business"
        )