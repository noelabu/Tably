from fastapi import APIRouter, HTTPException
from typing import Dict, Any, Optional
from pydantic import BaseModel, Field
import logging
import uuid

from app.agents.simple_voice_agent import SimpleVoiceOrderingAgent

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/simple-voice-ordering", tags=["simple-voice-ordering"])

class TextOrderRequest(BaseModel):
    business_id: str = Field(..., description="ID of the business")
    message: str = Field(..., description="Customer's text message")
    session_id: Optional[str] = Field(None, description="Optional session ID for context")

class TextOrderResponse(BaseModel):
    response: str
    session_id: str

class VoiceSessionInfo(BaseModel):
    session_id: str
    business_id: str
    status: str
    
# Simple in-memory session storage (in production, use Redis or database)
active_sessions: Dict[str, SimpleVoiceOrderingAgent] = {}

@router.post("/text-order", response_model=TextOrderResponse)
async def process_text_order(request: TextOrderRequest) -> TextOrderResponse:
    """Process a text-based order using the voice ordering agent."""
    try:
        # Get or create session
        session_id = request.session_id or str(uuid.uuid4())
        
        if session_id not in active_sessions:
            # Create new voice agent for this session
            active_sessions[session_id] = SimpleVoiceOrderingAgent(business_id=request.business_id)
        
        agent = active_sessions[session_id]
        
        # Process the message
        response = await agent.process_voice_input(request.message)
        
        return TextOrderResponse(
            response=response,
            session_id=session_id
        )
        
    except Exception as e:
        logger.error(f"Error processing text order: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Failed to process text order: {str(e)}")

@router.get("/sessions/{session_id}", response_model=VoiceSessionInfo)
async def get_voice_session(session_id: str) -> VoiceSessionInfo:
    """Get information about a voice ordering session."""
    try:
        if session_id not in active_sessions:
            raise HTTPException(status_code=404, detail="Voice session not found")
        
        agent = active_sessions[session_id]
        
        return VoiceSessionInfo(
            session_id=session_id,
            business_id=agent.business_id,
            status="active"
        )
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error getting voice session: {str(e)}")
        raise HTTPException(status_code=500, detail="Failed to get voice session info")

@router.delete("/sessions/{session_id}")
async def end_voice_session(session_id: str) -> Dict[str, str]:
    """End a voice ordering session."""
    try:
        if session_id not in active_sessions:
            raise HTTPException(status_code=404, detail="Voice session not found")
        
        # Clean up the session
        del active_sessions[session_id]
        
        return {"message": "Voice session ended successfully"}
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error ending voice session: {str(e)}")
        raise HTTPException(status_code=500, detail="Failed to end voice session")

@router.get("/sessions")
async def list_voice_sessions() -> Dict[str, Any]:
    """List all active voice ordering sessions."""
    try:
        sessions = {}
        for session_id, agent in active_sessions.items():
            sessions[session_id] = {
                "business_id": agent.business_id,
                "current_order_items": len(agent.current_order),
                "status": "active"
            }
        
        return {
            "active_sessions": len(sessions),
            "sessions": sessions
        }
        
    except Exception as e:
        logger.error(f"Error listing voice sessions: {str(e)}")
        raise HTTPException(status_code=500, detail="Failed to list voice sessions")

@router.post("/sessions/{session_id}/reset")
async def reset_voice_session(session_id: str) -> Dict[str, str]:
    """Reset a voice ordering session (clear current order)."""
    try:
        if session_id not in active_sessions:
            raise HTTPException(status_code=404, detail="Voice session not found")
        
        agent = active_sessions[session_id]
        agent.reset_order()
        
        return {"message": "Voice session reset successfully"}
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error resetting voice session: {str(e)}")
        raise HTTPException(status_code=500, detail="Failed to reset voice session")

@router.get("/health")
async def voice_service_health() -> Dict[str, Any]:
    """Check the health of the simple voice ordering service."""
    try:
        return {
            "status": "healthy",
            "active_sessions": len(active_sessions),
            "service": "simple_voice_ordering",
            "features": [
                "text_based_ordering",
                "menu_retrieval",
                "order_management",
                "session_management"
            ]
        }
        
    except Exception as e:
        logger.error(f"Voice service health check failed: {str(e)}")
        return {
            "status": "unhealthy",
            "error": str(e),
            "service": "simple_voice_ordering"
        }