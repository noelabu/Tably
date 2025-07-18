from fastapi import APIRouter, HTTPException, Depends, status, Query
from fastapi.responses import JSONResponse
import logging
from typing import List, Optional, Dict, Any
import json
from datetime import datetime
import uuid

from app.core.config import settings
from app.api.dependencies.auth import get_current_user
from app.models.auth import UserResponse
from app.models.ordering import (
    CustomerPreference, DietaryRestriction, OrderType, AgentSession, AgentInteraction
)
from app.agents.ordering_agents import (
    ordering_assistant_agent,
    recommendation_agent,
    translation_agent
)

logger = logging.getLogger(__name__)
router = APIRouter()

# In-memory storage for demo purposes (replace with actual database)
preferences_db: Dict[str, CustomerPreference] = {}
agent_sessions_db: Dict[str, AgentSession] = {}

@router.get("/preferences", response_model=CustomerPreference)
async def get_customer_preferences(
    current_user: UserResponse = Depends(get_current_user)
):
    """
    Get customer preferences and dietary restrictions.
    """
    try:
        user_id = current_user.id
        
        if user_id not in preferences_db:
            # Create default preferences
            preferences_db[user_id] = CustomerPreference(
                user_id=user_id,
                favorite_items=[],
                dietary_restrictions=[],
                preferred_language="english",
                spice_level=None,
                budget_range=None,
                preferred_order_type=None,
                allergen_warnings=[]
            )
        
        return preferences_db[user_id]
        
    except Exception as e:
        logger.error(f"Error retrieving preferences: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to retrieve customer preferences"
        )

@router.put("/preferences", response_model=CustomerPreference)
async def update_customer_preferences(
    preferences: CustomerPreference,
    current_user: UserResponse = Depends(get_current_user)
):
    """
    Update customer preferences and dietary restrictions.
    """
    try:
        user_id = current_user.id
        preferences.user_id = user_id
        preferences.updated_at = datetime.utcnow()
        
        preferences_db[user_id] = preferences
        
        # Generate AI response about updated preferences
        dietary_str = ", ".join([dr.value for dr in preferences.dietary_restrictions])
        agent_response = recommendation_agent(
            f"Updated preferences with dietary restrictions: {dietary_str}",
            None,
            dietary_str if dietary_str else None,
            preferences.budget_range,
            None
        )
        
        logger.info(f"Updated preferences for user {user_id}")
        
        return preferences
        
    except Exception as e:
        logger.error(f"Error updating preferences: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to update customer preferences"
        )

@router.post("/preferences/favorite/{item_id}")
async def add_favorite_item(
    item_id: str,
    current_user: UserResponse = Depends(get_current_user)
):
    """
    Add item to customer's favorites.
    """
    try:
        user_id = current_user.id
        
        # Get or create preferences
        if user_id not in preferences_db:
            preferences_db[user_id] = CustomerPreference(
                user_id=user_id,
                favorite_items=[],
                dietary_restrictions=[],
                preferred_language="english"
            )
        
        preferences = preferences_db[user_id]
        
        if item_id not in preferences.favorite_items:
            preferences.favorite_items.append(item_id)
            preferences.updated_at = datetime.utcnow()
            
            # Generate AI response
            agent_response = recommendation_agent(
                f"Customer added item {item_id} to favorites",
                None,
                ", ".join([dr.value for dr in preferences.dietary_restrictions]) if preferences.dietary_restrictions else None
            )
            
            return {
                "message": "Item added to favorites",
                "favorite_items": preferences.favorite_items,
                "agent_response": agent_response
            }
        else:
            return {
                "message": "Item already in favorites",
                "favorite_items": preferences.favorite_items
            }
        
    except Exception as e:
        logger.error(f"Error adding favorite item: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to add favorite item"
        )

@router.delete("/preferences/favorite/{item_id}")
async def remove_favorite_item(
    item_id: str,
    current_user: UserResponse = Depends(get_current_user)
):
    """
    Remove item from customer's favorites.
    """
    try:
        user_id = current_user.id
        
        if user_id not in preferences_db:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Customer preferences not found"
            )
        
        preferences = preferences_db[user_id]
        
        if item_id in preferences.favorite_items:
            preferences.favorite_items.remove(item_id)
            preferences.updated_at = datetime.utcnow()
            
            return {
                "message": "Item removed from favorites",
                "favorite_items": preferences.favorite_items
            }
        else:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Item not in favorites"
            )
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error removing favorite item: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to remove favorite item"
        )

@router.get("/preferences/recommendations")
async def get_personalized_recommendations(
    current_user: UserResponse = Depends(get_current_user),
    menu_data: Optional[str] = Query(None, description="Optional menu data as JSON string"),
    occasion: Optional[str] = Query(None, description="Special occasion context")
):
    """
    Get personalized recommendations based on customer preferences.
    """
    try:
        user_id = current_user.id
        
        # Get customer preferences
        preferences = preferences_db.get(user_id)
        if not preferences:
            # Use default preferences for recommendation
            preferences = CustomerPreference(
                user_id=user_id,
                favorite_items=[],
                dietary_restrictions=[],
                preferred_language="english"
            )
        
        # Build preference string
        preference_parts = []
        if preferences.spice_level:
            preference_parts.append(f"spice level: {preferences.spice_level}")
        if preferences.favorite_items:
            preference_parts.append(f"previously enjoyed items: {', '.join(preferences.favorite_items[:3])}")
        
        preference_string = ", ".join(preference_parts) if preference_parts else "general recommendations"
        
        # Get dietary restrictions
        dietary_restrictions = ", ".join([dr.value for dr in preferences.dietary_restrictions]) if preferences.dietary_restrictions else None
        
        # Get recommendations
        recommendations = recommendation_agent(
            preference_string,
            menu_data,
            dietary_restrictions,
            preferences.budget_range,
            occasion
        )
        
        return {
            "recommendations": recommendations,
            "based_on": {
                "dietary_restrictions": [dr.value for dr in preferences.dietary_restrictions],
                "spice_level": preferences.spice_level,
                "budget_range": preferences.budget_range,
                "favorite_items_count": len(preferences.favorite_items)
            },
            "timestamp": datetime.utcnow().isoformat()
        }
        
    except Exception as e:
        logger.error(f"Error getting personalized recommendations: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to get personalized recommendations"
        )

@router.post("/preferences/dietary-restrictions")
async def update_dietary_restrictions(
    dietary_restrictions: List[DietaryRestriction],
    current_user: UserResponse = Depends(get_current_user)
):
    """
    Update customer's dietary restrictions.
    """
    try:
        user_id = current_user.id
        
        # Get or create preferences
        if user_id not in preferences_db:
            preferences_db[user_id] = CustomerPreference(
                user_id=user_id,
                favorite_items=[],
                dietary_restrictions=[],
                preferred_language="english"
            )
        
        preferences = preferences_db[user_id]
        preferences.dietary_restrictions = dietary_restrictions
        preferences.updated_at = datetime.utcnow()
        
        # Generate AI response about dietary restrictions
        dietary_str = ", ".join([dr.value for dr in dietary_restrictions])
        agent_response = ordering_assistant_agent(
            f"I have updated my dietary restrictions to: {dietary_str}",
            None,
            "Customer is updating dietary preferences"
        )
        
        return {
            "message": "Dietary restrictions updated",
            "dietary_restrictions": [dr.value for dr in dietary_restrictions],
            "agent_response": agent_response
        }
        
    except Exception as e:
        logger.error(f"Error updating dietary restrictions: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to update dietary restrictions"
        )

@router.post("/preferences/language")
async def update_preferred_language(
    language: str,
    current_user: UserResponse = Depends(get_current_user)
):
    """
    Update customer's preferred language.
    """
    try:
        user_id = current_user.id
        
        # Get or create preferences
        if user_id not in preferences_db:
            preferences_db[user_id] = CustomerPreference(
                user_id=user_id,
                favorite_items=[],
                dietary_restrictions=[],
                preferred_language="english"
            )
        
        preferences = preferences_db[user_id]
        old_language = preferences.preferred_language
        preferences.preferred_language = language
        preferences.updated_at = datetime.utcnow()
        
        # Generate AI response in the new language
        message = f"Language preference updated from {old_language} to {language}"
        agent_response = translation_agent(
            message,
            "english",
            language
        )
        
        return {
            "message": "Language preference updated",
            "old_language": old_language,
            "new_language": language,
            "agent_response": agent_response
        }
        
    except Exception as e:
        logger.error(f"Error updating language preference: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to update language preference"
        )

@router.get("/agent-sessions")
async def get_agent_sessions(
    current_user: UserResponse = Depends(get_current_user),
    limit: int = Query(10, ge=1, le=100, description="Number of sessions to retrieve")
):
    """
    Get customer's recent agent interaction sessions.
    """
    try:
        user_id = current_user.id
        
        # Filter user's sessions
        user_sessions = [
            session for session in agent_sessions_db.values()
            if session.user_id == user_id
        ]
        
        # Sort by creation date (newest first)
        user_sessions.sort(key=lambda x: x.created_at, reverse=True)
        
        # Limit results
        user_sessions = user_sessions[:limit]
        
        return {
            "sessions": user_sessions,
            "total_count": len(user_sessions)
        }
        
    except Exception as e:
        logger.error(f"Error retrieving agent sessions: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to retrieve agent sessions"
        )

@router.post("/agent-sessions")
async def create_agent_session(
    business_id: str,
    language: str = "english",
    current_user: UserResponse = Depends(get_current_user)
):
    """
    Create a new agent interaction session.
    """
    try:
        user_id = current_user.id
        
        # Create new session
        session = AgentSession(
            user_id=user_id,
            business_id=business_id,
            language=language,
            context={},
            interactions=[]
        )
        
        agent_sessions_db[session.session_id] = session
        
        return {
            "session": session,
            "message": "Agent session created successfully"
        }
        
    except Exception as e:
        logger.error(f"Error creating agent session: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to create agent session"
        )

@router.post("/agent-sessions/{session_id}/interact")
async def interact_with_agent(
    session_id: str,
    message: str,
    current_user: UserResponse = Depends(get_current_user)
):
    """
    Interact with agent in a specific session.
    """
    try:
        user_id = current_user.id
        
        if session_id not in agent_sessions_db:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Agent session not found"
            )
        
        session = agent_sessions_db[session_id]
        
        # Check if user owns this session
        if session.user_id != user_id:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Access denied"
            )
        
        # Process message with appropriate agent based on language
        if session.language == "english":
            agent_response = ordering_assistant_agent(
                message,
                None,
                json.dumps(session.context) if session.context else None
            )
        else:
            # Use translation agent for non-English
            agent_response = translation_agent(
                message,
                session.language,
                "english"
            )
        
        # Create interaction record
        interaction = AgentInteraction(
            session_id=session_id,
            user_id=user_id,
            message=message,
            agent_response=agent_response,
            agent_type="ordering_assistant",
            language=session.language,
            context=session.context.copy()
        )
        
        session.interactions.append(interaction)
        session.updated_at = datetime.utcnow()
        
        return {
            "interaction": interaction,
            "session_id": session_id,
            "total_interactions": len(session.interactions)
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error in agent interaction: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to process agent interaction"
        )

@router.get("/agent-sessions/{session_id}")
async def get_agent_session(
    session_id: str,
    current_user: UserResponse = Depends(get_current_user)
):
    """
    Get a specific agent session with all interactions.
    """
    try:
        user_id = current_user.id
        
        if session_id not in agent_sessions_db:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Agent session not found"
            )
        
        session = agent_sessions_db[session_id]
        
        # Check if user owns this session
        if session.user_id != user_id:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Access denied"
            )
        
        return {
            "session": session,
            "interaction_count": len(session.interactions)
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error retrieving agent session: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to retrieve agent session"
        )

@router.delete("/agent-sessions/{session_id}")
async def close_agent_session(
    session_id: str,
    current_user: UserResponse = Depends(get_current_user)
):
    """
    Close an agent session.
    """
    try:
        user_id = current_user.id
        
        if session_id not in agent_sessions_db:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Agent session not found"
            )
        
        session = agent_sessions_db[session_id]
        
        # Check if user owns this session
        if session.user_id != user_id:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Access denied"
            )
        
        # Mark session as inactive
        session.is_active = False
        session.updated_at = datetime.utcnow()
        
        return {
            "message": "Agent session closed successfully",
            "session_id": session_id,
            "interaction_count": len(session.interactions)
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error closing agent session: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to close agent session"
        )

@router.get("/preferences/summary")
async def get_preferences_summary(
    current_user: UserResponse = Depends(get_current_user)
):
    """
    Get a summary of customer preferences and activity.
    """
    try:
        user_id = current_user.id
        
        # Get preferences
        preferences = preferences_db.get(user_id)
        if not preferences:
            preferences = CustomerPreference(
                user_id=user_id,
                favorite_items=[],
                dietary_restrictions=[],
                preferred_language="english"
            )
        
        # Get session count
        user_sessions = [
            session for session in agent_sessions_db.values()
            if session.user_id == user_id
        ]
        
        total_interactions = sum(len(session.interactions) for session in user_sessions)
        
        return {
            "preferences": preferences,
            "activity_summary": {
                "total_sessions": len(user_sessions),
                "total_interactions": total_interactions,
                "favorite_items_count": len(preferences.favorite_items),
                "dietary_restrictions_count": len(preferences.dietary_restrictions),
                "last_updated": preferences.updated_at
            }
        }
        
    except Exception as e:
        logger.error(f"Error getting preferences summary: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to get preferences summary"
        )