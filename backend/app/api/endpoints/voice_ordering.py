from fastapi import APIRouter, HTTPException, Depends, BackgroundTasks
from typing import Dict, Any, Optional
from pydantic import BaseModel, Field
import logging

from app.services.voice_streaming_service import voice_streaming_service
from app.agents.voice_ordering_agent import VoiceOrderingAgent
from app.api.dependencies.auth import get_current_user

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/voice-ordering", tags=["voice-ordering"])

class VoiceSessionRequest(BaseModel):
    business_id: str = Field(..., description="ID of the business for voice ordering")
    customer_name: Optional[str] = Field(None, description="Optional customer name")

class VoiceSessionResponse(BaseModel):
    session_id: str
    room_url: str
    token: str
    message: str

class VoiceSessionInfo(BaseModel):
    session_id: str
    business_id: str
    customer_name: Optional[str]
    room_url: str
    created_at: float
    status: str

class TextOrderRequest(BaseModel):
    business_id: str = Field(..., description="ID of the business")
    message: str = Field(..., description="Customer's text message")
    session_id: Optional[str] = Field(None, description="Optional session ID for context")

class TextOrderResponse(BaseModel):
    response: str
    session_id: str

@router.post("/sessions", response_model=VoiceSessionResponse)
async def create_voice_session(
    request: VoiceSessionRequest,
    background_tasks: BackgroundTasks
) -> VoiceSessionResponse:
    """Create a new voice ordering session with Daily.co room."""
    try:
        # Create the voice session
        session_data = await voice_streaming_service.create_voice_session(
            business_id=request.business_id,
            customer_name=request.customer_name
        )
        
        # Start the voice bot in the background
        background_tasks.add_task(
            voice_streaming_service.start_voice_bot,
            session_data["session_id"]
        )
        
        return VoiceSessionResponse(
            session_id=session_data["session_id"],
            room_url=session_data["room_url"],
            token=session_data["token"],
            message="Voice ordering session created successfully. Join the room to start ordering!"
        )
        
    except Exception as e:
        logger.error(f"Error creating voice session: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Failed to create voice session: {str(e)}")

@router.get("/sessions/{session_id}", response_model=VoiceSessionInfo)
async def get_voice_session(session_id: str) -> VoiceSessionInfo:
    """Get information about a voice ordering session."""
    try:
        session = await voice_streaming_service.get_session_info(session_id)
        
        if not session:
            raise HTTPException(status_code=404, detail="Voice session not found")
        
        return VoiceSessionInfo(
            session_id=session_id,
            business_id=session["business_id"],
            customer_name=session.get("customer_name"),
            room_url=session["room_url"],
            created_at=session["created_at"],
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
        success = await voice_streaming_service.end_voice_session(session_id)
        
        if not success:
            raise HTTPException(status_code=404, detail="Voice session not found")
        
        return {"message": "Voice session ended successfully"}
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error ending voice session: {str(e)}")
        raise HTTPException(status_code=500, detail="Failed to end voice session")

@router.get("/sessions")
async def list_voice_sessions(
    current_user: Dict[str, Any] = Depends(get_current_user)
) -> Dict[str, Any]:
    """List all active voice ordering sessions (admin only)."""
    try:
        sessions = await voice_streaming_service.list_active_sessions()
        return {
            "active_sessions": len(sessions),
            "sessions": sessions
        }
        
    except Exception as e:
        logger.error(f"Error listing voice sessions: {str(e)}")
        raise HTTPException(status_code=500, detail="Failed to list voice sessions")

@router.post("/text-order", response_model=TextOrderResponse)
async def process_text_order(request: TextOrderRequest) -> TextOrderResponse:
    """Process a text-based order (for testing or fallback)."""
    try:
        # Create or get existing voice agent for this session
        voice_agent = VoiceOrderingAgent(business_id=request.business_id)
        
        # Process the message
        response = await voice_agent.process_voice_input(request.message)
        
        # Use provided session_id or create a new one
        session_id = request.session_id or f"text-{voice_agent.business_id}-{id(voice_agent)}"
        
        return TextOrderResponse(
            response=response,
            session_id=session_id
        )
        
    except Exception as e:
        logger.error(f"Error processing text order: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Failed to process text order: {str(e)}")

@router.post("/cleanup-expired")
async def cleanup_expired_sessions(
    current_user: Dict[str, Any] = Depends(get_current_user)
) -> Dict[str, Any]:
    """Clean up expired voice sessions (admin only)."""
    try:
        cleaned_count = await voice_streaming_service.cleanup_expired_sessions()
        return {
            "message": f"Cleaned up {cleaned_count} expired sessions",
            "cleaned_sessions": cleaned_count
        }
        
    except Exception as e:
        logger.error(f"Error cleaning up sessions: {str(e)}")
        raise HTTPException(status_code=500, detail="Failed to clean up sessions")

@router.get("/health")
async def voice_service_health() -> Dict[str, Any]:
    """Check the health of the voice ordering service."""
    try:
        active_sessions = await voice_streaming_service.list_active_sessions()
        
        return {
            "status": "healthy",
            "active_sessions": len(active_sessions),
            "service": "voice_ordering",
            "features": [
                "voice_to_voice_ordering",
                "menu_retrieval",
                "order_management",
                "text_fallback"
            ]
        }
        
    except Exception as e:
        logger.error(f"Voice service health check failed: {str(e)}")
        return {
            "status": "unhealthy",
            "error": str(e),
            "service": "voice_ordering"
        }