from fastapi import APIRouter, HTTPException
from typing import Dict, Any, Optional
from pydantic import BaseModel, Field
import logging
import uuid

# from app.agents.simple_voice_agent import SimpleVoiceOrderingAgent  # Module moved to tests directory

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
    
@router.post("/text-order", response_model=TextOrderResponse)
async def process_text_order(request: TextOrderRequest) -> TextOrderResponse:
    """Process a text-based order using the voice ordering agent."""
    # This endpoint is disabled because SimpleVoiceOrderingAgent was moved to tests
    raise HTTPException(
        status_code=503, 
        detail="This simple voice ordering service is temporarily disabled. Please use /restaurant-voice/sessions for voice ordering."
    )

@router.get("/sessions/{session_id}", response_model=VoiceSessionInfo)
async def get_voice_session(session_id: str) -> VoiceSessionInfo:
    """Get information about a voice ordering session."""
    # This endpoint is disabled because SimpleVoiceOrderingAgent was moved to tests
    raise HTTPException(
        status_code=503, 
        detail="This simple voice ordering service is temporarily disabled. Please use /restaurant-voice/sessions for voice ordering."
    )

@router.delete("/sessions/{session_id}")
async def end_voice_session(session_id: str) -> Dict[str, str]:
    """End a voice ordering session."""
    # This endpoint is disabled because SimpleVoiceOrderingAgent was moved to tests
    raise HTTPException(
        status_code=503, 
        detail="This simple voice ordering service is temporarily disabled. Please use /restaurant-voice/sessions for voice ordering."
    )

@router.get("/sessions")
async def list_voice_sessions() -> Dict[str, Any]:
    """List all active voice ordering sessions."""
    # This endpoint is disabled because SimpleVoiceOrderingAgent was moved to tests
    raise HTTPException(
        status_code=503, 
        detail="This simple voice ordering service is temporarily disabled. Please use /restaurant-voice/sessions for voice ordering."
    )

@router.get("/health")
async def voice_service_health() -> Dict[str, Any]:
    """Check the health of the simple voice ordering service."""
    return {
        "status": "disabled",
        "message": "This simple voice ordering service is temporarily disabled",
        "service": "simple_voice_ordering_legacy",
        "alternative": "/restaurant-voice/health"
    }