from fastapi import APIRouter, HTTPException, Depends, BackgroundTasks
from typing import Dict, Any, Optional
from pydantic import BaseModel, Field
import logging

# from app.services.voice_streaming_service import voice_streaming_service  # Disabled due to pipecat compatibility issues
# from app.agents.voice_ordering_agent import VoiceOrderingAgent  # Disabled due to strands compatibility issues
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
    # This endpoint is disabled due to pipecat compatibility issues
    # Use /restaurant-voice/sessions instead for the new Nova Sonic voice ordering
    raise HTTPException(
        status_code=503, 
        detail="This voice service is temporarily disabled. Please use /restaurant-voice/sessions for voice ordering."
    )

@router.get("/sessions/{session_id}", response_model=VoiceSessionInfo)
async def get_voice_session(session_id: str) -> VoiceSessionInfo:
    """Get information about a voice ordering session."""
    # This endpoint is disabled due to pipecat compatibility issues
    raise HTTPException(
        status_code=503, 
        detail="This voice service is temporarily disabled. Please use /restaurant-voice/sessions for voice ordering."
    )

@router.delete("/sessions/{session_id}")
async def end_voice_session(session_id: str) -> Dict[str, str]:
    """End a voice ordering session."""
    # This endpoint is disabled due to pipecat compatibility issues
    raise HTTPException(
        status_code=503, 
        detail="This voice service is temporarily disabled. Please use /restaurant-voice/sessions for voice ordering."
    )

@router.get("/sessions")
async def list_voice_sessions(
    current_user: Dict[str, Any] = Depends(get_current_user)
) -> Dict[str, Any]:
    """List all active voice ordering sessions (admin only)."""
    # This endpoint is disabled due to pipecat compatibility issues
    raise HTTPException(
        status_code=503, 
        detail="This voice service is temporarily disabled. Please use /restaurant-voice/sessions for voice ordering."
    )

@router.post("/text-order", response_model=TextOrderResponse)
async def process_text_order(request: TextOrderRequest) -> TextOrderResponse:
    """Process a text-based order (for testing or fallback)."""
    # This endpoint is disabled due to strands compatibility issues
    raise HTTPException(
        status_code=503, 
        detail="This text ordering service is temporarily disabled. Please use /restaurant-voice/sessions for voice ordering."
    )

@router.post("/cleanup-expired")
async def cleanup_expired_sessions(
    current_user: Dict[str, Any] = Depends(get_current_user)
) -> Dict[str, Any]:
    """Clean up expired voice sessions (admin only)."""
    # This endpoint is disabled due to pipecat compatibility issues
    raise HTTPException(
        status_code=503, 
        detail="This voice service is temporarily disabled. Please use /restaurant-voice/sessions for voice ordering."
    )

@router.get("/health")
async def voice_service_health() -> Dict[str, Any]:
    """Check the health of the voice ordering service."""
    return {
        "status": "disabled",
        "message": "This voice service is temporarily disabled due to compatibility issues",
        "service": "voice_ordering_legacy",
        "alternative": "/restaurant-voice/health"
    }