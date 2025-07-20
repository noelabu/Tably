"""
Conversation management endpoints for chat sessions.
"""
from fastapi import APIRouter, HTTPException, Depends, status
import logging
from typing import Optional, List, Dict, Any
from datetime import datetime
from app.core.config import settings
from app.api.dependencies.auth import get_current_user
from app.models.auth import UserResponse
from app.services.conversation_memory import conversation_memory
from pydantic import BaseModel, Field

logger = logging.getLogger(__name__)
router = APIRouter()

class SessionRequest(BaseModel):
    business_id: Optional[str] = Field(None, description="Business ID for the session")

class SessionResponse(BaseModel):
    session_id: str = Field(..., description="Unique session identifier")
    business_id: Optional[str] = Field(None, description="Business ID")
    created_at: str = Field(..., description="Session creation timestamp")
    message_count: int = Field(..., description="Number of messages in session")

class ConversationHistoryResponse(BaseModel):
    session_id: str = Field(..., description="Session identifier")
    messages: List[Dict[str, Any]] = Field(..., description="Conversation messages")
    total_messages: int = Field(..., description="Total number of messages")

@router.post("/sessions", response_model=SessionResponse)
async def create_conversation_session(
    request: SessionRequest,
    current_user: UserResponse = Depends(get_current_user)
):
    """
    Create a new conversation session.
    """
    try:
        # Generate session ID
        session_id = f"user_{current_user.id}_{datetime.utcnow().strftime('%Y%m%d_%H%M%S_%f')}"
        
        # Create session
        session = conversation_memory.create_session(
            session_id=session_id,
            business_id=request.business_id,
            user_id=str(current_user.id)
        )
        
        logger.info(f"Created conversation session {session_id} for user {current_user.id}")
        
        return SessionResponse(
            session_id=session.session_id,
            business_id=session.business_id,
            created_at=session.created_at.isoformat(),
            message_count=len(session.messages)
        )
        
    except Exception as e:
        logger.error(f"Error creating conversation session: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to create conversation session"
        )

@router.get("/sessions/{session_id}", response_model=ConversationHistoryResponse)
async def get_conversation_history(
    session_id: str,
    current_user: UserResponse = Depends(get_current_user)
):
    """
    Get conversation history for a session.
    """
    try:
        session = conversation_memory.get_session(session_id)
        
        if not session:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Conversation session not found"
            )
        
        # Verify user owns this session
        if session.user_id != str(current_user.id):
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Access denied to this conversation session"
            )
        
        # Convert messages to response format
        messages = [msg.to_dict() for msg in session.messages]
        
        return ConversationHistoryResponse(
            session_id=session.session_id,
            messages=messages,
            total_messages=len(messages)
        )
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error getting conversation history: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to retrieve conversation history"
        )

@router.delete("/sessions/{session_id}")
async def clear_conversation_session(
    session_id: str,
    current_user: UserResponse = Depends(get_current_user)
):
    """
    Clear a conversation session.
    """
    try:
        session = conversation_memory.get_session(session_id)
        
        if session and session.user_id != str(current_user.id):
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Access denied to this conversation session"
            )
        
        success = conversation_memory.clear_session(session_id)
        
        if success:
            logger.info(f"Cleared conversation session {session_id} for user {current_user.id}")
            return {"message": "Conversation session cleared successfully"}
        else:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Conversation session not found"
            )
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error clearing conversation session: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to clear conversation session"
        )

@router.get("/sessions")
async def list_user_sessions(
    current_user: UserResponse = Depends(get_current_user)
):
    """
    List all active sessions for the current user.
    """
    try:
        stats = conversation_memory.get_session_stats()
        
        # Filter sessions for current user
        user_sessions = []
        for session_id, session in conversation_memory.sessions.items():
            if session.user_id == str(current_user.id):
                user_sessions.append({
                    "session_id": session.session_id,
                    "business_id": session.business_id,
                    "created_at": session.created_at.isoformat(),
                    "last_activity": session.last_activity.isoformat(),
                    "message_count": len(session.messages)
                })
        
        return {
            "sessions": user_sessions,
            "total_sessions": len(user_sessions)
        }
        
    except Exception as e:
        logger.error(f"Error listing user sessions: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to retrieve user sessions"
        )