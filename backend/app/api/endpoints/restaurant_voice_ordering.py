from fastapi import APIRouter, HTTPException, WebSocket, WebSocketDisconnect
from fastapi.responses import JSONResponse
from typing import Dict, Any, Optional
from pydantic import BaseModel, Field
import asyncio
import logging
import json
import base64
from datetime import datetime

from app.agents.restaurant_voice_agent import RestaurantStreamManager, RestaurantToolProcessor

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/restaurant-voice", tags=["restaurant-voice-ordering"])

class VoiceSessionRequest(BaseModel):
    business_id: str = Field(..., description="ID of the business for voice ordering")
    debug: bool = Field(False, description="Enable debug mode")

class VoiceSessionResponse(BaseModel):
    session_id: str
    business_id: str
    websocket_url: str
    message: str
    instructions: Dict[str, str]

class AudioChunkRequest(BaseModel):
    session_id: str
    audio_data: str = Field(..., description="Base64 encoded audio data")
    format: str = Field("pcm16", description="Audio format")
    sample_rate: int = Field(16000, description="Sample rate in Hz")

class VoiceStreamManager:
    """Manages active voice streaming sessions"""
    
    def __init__(self):
        self.active_sessions: Dict[str, RestaurantStreamManager] = {}
        self.session_info: Dict[str, Dict[str, Any]] = {}
    
    async def create_session(self, business_id: str, debug: bool = False) -> Dict[str, Any]:
        """Create a new voice streaming session"""
        import uuid
        session_id = str(uuid.uuid4())
        
        try:
            # Create stream manager
            stream_manager = RestaurantStreamManager(
                business_id=business_id, 
                model_id='amazon.nova-sonic-v1:0', 
                region='us-east-1'
            )
            
            # Initialize the stream
            await stream_manager.initialize_stream()
            
            # Store session
            self.active_sessions[session_id] = stream_manager
            self.session_info[session_id] = {
                "business_id": business_id,
                "created_at": datetime.now().isoformat(),
                "debug": debug,
                "status": "active"
            }
            
            return {
                "session_id": session_id,
                "business_id": business_id,
                "status": "initialized"
            }
            
        except Exception as e:
            logger.error(f"Failed to create voice session: {e}")
            raise HTTPException(status_code=500, detail=f"Failed to create voice session: {str(e)}")
    
    async def end_session(self, session_id: str) -> bool:
        """End a voice streaming session"""
        if session_id in self.active_sessions:
            try:
                stream_manager = self.active_sessions[session_id]
                await stream_manager.close()
                del self.active_sessions[session_id]
                
                if session_id in self.session_info:
                    self.session_info[session_id]["status"] = "ended"
                
                return True
            except Exception as e:
                logger.error(f"Error ending session {session_id}: {e}")
                return False
        return False
    
    def get_session(self, session_id: str) -> Optional[RestaurantStreamManager]:
        """Get active session"""
        return self.active_sessions.get(session_id)
    
    def get_session_info(self, session_id: str) -> Optional[Dict[str, Any]]:
        """Get session information"""
        return self.session_info.get(session_id)

# Global session manager
voice_manager = VoiceStreamManager()

@router.post("/sessions", response_model=VoiceSessionResponse)
async def create_voice_session(request: VoiceSessionRequest) -> VoiceSessionResponse:
    """Create a new restaurant voice ordering session."""
    try:
        session_data = await voice_manager.create_session(
            business_id=request.business_id,
            debug=request.debug
        )
        
        return VoiceSessionResponse(
            session_id=session_data["session_id"],
            business_id=session_data["business_id"],
            websocket_url=f"/restaurant-voice/ws/{session_data['session_id']}",
            message="Voice ordering session created successfully",
            instructions={
                "websocket": "Connect to the WebSocket URL to start voice streaming",
                "audio_format": "Send base64-encoded PCM audio data at 16kHz",
                "stop_session": f"DELETE /restaurant-voice/sessions/{session_data['session_id']}",
                "manual_stop": "Press Enter or send empty message to stop"
            }
        )
        
    except Exception as e:
        logger.error(f"Error creating voice session: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Failed to create voice session: {str(e)}")

@router.get("/sessions/{session_id}")
async def get_voice_session(session_id: str) -> Dict[str, Any]:
    """Get information about a voice ordering session."""
    session_info = voice_manager.get_session_info(session_id)
    
    if not session_info:
        raise HTTPException(status_code=404, detail="Voice session not found")
    
    return {
        "session_id": session_id,
        **session_info,
        "websocket_url": f"/restaurant-voice/ws/{session_id}"
    }

@router.delete("/sessions/{session_id}")
async def end_voice_session(session_id: str) -> Dict[str, str]:
    """End a voice ordering session."""
    success = await voice_manager.end_session(session_id)
    
    if not success:
        raise HTTPException(status_code=404, detail="Voice session not found or already ended")
    
    return {"message": "Voice session ended successfully"}

@router.get("/sessions")
async def list_voice_sessions() -> Dict[str, Any]:
    """List all active voice ordering sessions."""
    active_sessions = list(voice_manager.session_info.keys())
    
    return {
        "active_sessions": len(active_sessions),
        "session_ids": active_sessions,
        "sessions": voice_manager.session_info
    }

@router.websocket("/ws/{session_id}")
async def websocket_voice_endpoint(websocket: WebSocket, session_id: str):
    """WebSocket endpoint for real-time voice streaming."""
    await websocket.accept()
    
    # Get the session
    stream_manager = voice_manager.get_session(session_id)
    if not stream_manager:
        await websocket.close(code=4004, reason="Session not found")
        return
    
    try:
        await websocket.send_text(json.dumps({
            "type": "session_ready",
            "session_id": session_id,
            "message": "Voice session ready. Send audio data to start ordering.",
            "audio_config": {
                "format": "pcm16",
                "sample_rate": 16000,
                "channels": 1,
                "encoding": "base64"
            }
        }))
        
        # Create tasks for handling audio input and output
        async def handle_audio_output():
            """Send audio output to WebSocket"""
            while stream_manager.is_active:
                try:
                    # Get audio output from stream manager
                    audio_data = await asyncio.wait_for(
                        stream_manager.audio_output_queue.get(),
                        timeout=1.0
                    )
                    
                    if audio_data:
                        # Send audio data as base64
                        audio_b64 = base64.b64encode(audio_data).decode('utf-8')
                        await websocket.send_text(json.dumps({
                            "type": "audio_output",
                            "audio_data": audio_b64,
                            "format": "pcm16",
                            "sample_rate": 24000
                        }))
                        
                except asyncio.TimeoutError:
                    continue
                except Exception as e:
                    logger.error(f"Error sending audio output: {e}")
                    break
        
        # Start audio output task
        output_task = asyncio.create_task(handle_audio_output())
        
        # Handle incoming messages
        while stream_manager.is_active:
            try:
                # Receive message from WebSocket
                data = await websocket.receive_text()
                message = json.loads(data)
                
                if message.get("type") == "audio_input":
                    # Process audio input
                    audio_b64 = message.get("audio_data", "")
                    if audio_b64:
                        try:
                            audio_bytes = base64.b64decode(audio_b64)
                            stream_manager.add_audio_chunk(audio_bytes)
                        except Exception as e:
                            logger.error(f"Error processing audio input: {e}")
                
                elif message.get("type") == "end_session":
                    # End the session
                    break
                    
                elif message.get("type") == "ping":
                    # Respond to ping
                    await websocket.send_text(json.dumps({
                        "type": "pong",
                        "timestamp": datetime.now().isoformat()
                    }))
                
            except WebSocketDisconnect:
                break
            except Exception as e:
                logger.error(f"Error in WebSocket loop: {e}")
                break
        
        # Cancel output task
        output_task.cancel()
        
        # End the voice stream
        await stream_manager.send_audio_content_end_event()
        await stream_manager.send_prompt_end_event()
        await stream_manager.send_session_end_event()
        
    except Exception as e:
        logger.error(f"WebSocket error: {e}")
    finally:
        # Clean up session
        await voice_manager.end_session(session_id)
        await websocket.close()

@router.post("/sessions/{session_id}/audio")
async def send_audio_chunk(session_id: str, request: AudioChunkRequest) -> Dict[str, str]:
    """Send an audio chunk to the voice session (alternative to WebSocket)."""
    stream_manager = voice_manager.get_session(session_id)
    
    if not stream_manager:
        raise HTTPException(status_code=404, detail="Voice session not found")
    
    try:
        # Decode base64 audio data
        audio_bytes = base64.b64decode(request.audio_data)
        
        # Add to stream manager
        stream_manager.add_audio_chunk(audio_bytes)
        
        return {"message": "Audio chunk processed successfully"}
        
    except Exception as e:
        logger.error(f"Error processing audio chunk: {e}")
        raise HTTPException(status_code=500, detail=f"Failed to process audio: {str(e)}")

@router.get("/health")
async def voice_service_health() -> Dict[str, Any]:
    """Check the health of the restaurant voice ordering service."""
    try:
        active_count = len(voice_manager.active_sessions)
        
        return {
            "status": "healthy",
            "service": "restaurant_voice_ordering",
            "active_sessions": active_count,
            "features": [
                "amazon_nova_sonic",
                "real_time_voice_streaming",
                "restaurant_menu_tools",
                "order_management",
                "websocket_streaming"
            ],
            "endpoints": {
                "create_session": "POST /restaurant-voice/sessions",
                "websocket": "WS /restaurant-voice/ws/{session_id}",
                "audio_http": "POST /restaurant-voice/sessions/{session_id}/audio"
            }
        }
        
    except Exception as e:
        logger.error(f"Voice service health check failed: {str(e)}")
        return {
            "status": "unhealthy",
            "error": str(e),
            "service": "restaurant_voice_ordering"
        }