import asyncio
import logging
from typing import Optional, Dict, Any
import json
import uuid

from pipecat.frames.frames import (
    AudioRawFrame,
    TextFrame,
    TranscriptionFrame,
    TTSStartedFrame,
    TTSStoppedFrame,
    UserStartedSpeakingFrame,
    UserStoppedSpeakingFrame,
)
from pipecat.pipeline.pipeline import Pipeline
from pipecat.pipeline.task import PipelineTask
from pipecat.services.ai_services import LLMService
from pipecat.services.amazon import AmazonTTSService, AmazonSTTService
from pipecat.transports.services.helpers.daily_rest import DailyRESTHelper, DailyRoomObject
from pipecat.transports.daily import DailyTransport

from app.agents.voice_ordering_agent import VoiceOrderingAgent
from app.core.config import settings

logger = logging.getLogger(__name__)

class VoiceOrderingLLMService(LLMService):
    """Custom LLM service that integrates with our Strands voice ordering agent."""
    
    def __init__(self, business_id: str, **kwargs):
        super().__init__(**kwargs)
        self.business_id = business_id
        self.voice_agent = VoiceOrderingAgent(business_id)
        self.session_id = str(uuid.uuid4())
        
    async def run_llm(self, messages) -> None:
        """Process messages through our voice ordering agent."""
        try:
            # Get the last user message
            user_message = None
            for message in reversed(messages):
                if message.get("role") == "user":
                    user_message = message.get("content", "")
                    break
            
            if not user_message:
                return
            
            # Process through our voice agent
            response = await self.voice_agent.process_voice_input(user_message)
            
            # Send response back through pipeline
            await self.push_frame(TextFrame(text=response))
            
        except Exception as e:
            logger.error(f"Error in voice ordering LLM service: {str(e)}")
            await self.push_frame(TextFrame(text="I'm sorry, I'm having trouble processing your request right now."))

class VoiceStreamingService:
    """Service for handling voice-to-voice ordering using Pipecat and Daily."""
    
    def __init__(self):
        self.daily_helper = DailyRESTHelper(
            daily_api_key=settings.DAILY_API_KEY,
            daily_api_url=settings.DAILY_API_URL or "https://api.daily.co/v1"
        )
        self.active_sessions: Dict[str, Dict[str, Any]] = {}
    
    async def create_voice_session(self, business_id: str, customer_name: Optional[str] = None) -> Dict[str, Any]:
        """Create a new voice ordering session."""
        try:
            session_id = str(uuid.uuid4())
            
            # Create Daily room for the session
            room_config = {
                "name": f"voice-order-{session_id}",
                "properties": {
                    "max_participants": 2,
                    "enable_chat": False,
                    "enable_screenshare": False,
                    "start_audio_off": False,
                    "start_video_off": True,
                    "exp": int(asyncio.get_event_loop().time()) + 3600  # 1 hour expiry
                }
            }
            
            room: DailyRoomObject = await self.daily_helper.create_room(room_config)
            
            if not room or not room.url:
                raise Exception("Failed to create Daily room")
            
            # Store session info
            self.active_sessions[session_id] = {
                "business_id": business_id,
                "customer_name": customer_name,
                "room_url": room.url,
                "room_name": room.name,
                "created_at": asyncio.get_event_loop().time()
            }
            
            return {
                "session_id": session_id,
                "room_url": room.url,
                "token": await self.daily_helper.get_token(room.url)
            }
            
        except Exception as e:
            logger.error(f"Error creating voice session: {str(e)}")
            raise Exception(f"Failed to create voice session: {str(e)}")
    
    async def start_voice_bot(self, session_id: str) -> bool:
        """Start the voice bot for a session."""
        try:
            session = self.active_sessions.get(session_id)
            if not session:
                raise Exception("Session not found")
            
            business_id = session["business_id"]
            room_url = session["room_url"]
            
            # Get Daily token for the bot
            token = await self.daily_helper.get_token(room_url)
            
            # Create transport
            transport = DailyTransport(
                room_url=room_url,
                token=token,
                bot_name="Voice Ordering Assistant",
                params={
                    "audio_in_enabled": True,
                    "audio_out_enabled": True,
                    "camera_enabled": False,
                    "vad_enabled": True,
                    "vad_analyzer": {
                        "params": {
                            "stop_secs": 0.8
                        }
                    }
                }
            )
            
            # Create services
            stt_service = AmazonSTTService(
                aws_access_key_id=settings.AWS_ACCESS_KEY_ID,
                aws_secret_access_key=settings.AWS_SECRET_ACCESS_KEY,
                region=settings.AWS_REGION or "us-east-1",
                language="en-US"
            )
            
            llm_service = VoiceOrderingLLMService(business_id=business_id)
            
            tts_service = AmazonTTSService(
                aws_access_key_id=settings.AWS_ACCESS_KEY_ID,
                aws_secret_access_key=settings.AWS_SECRET_ACCESS_KEY,
                region=settings.AWS_REGION or "us-east-1",
                voice_id="Joanna",  # Natural sounding voice
                sample_rate=24000
            )
            
            # Create pipeline
            pipeline = Pipeline([
                transport.input(),
                stt_service,
                llm_service,
                tts_service,
                transport.output()
            ])
            
            # Create and start task
            task = PipelineTask(pipeline, params={
                "allow_interruptions": True,
                "enable_metrics": True,
                "report_only_initial_ttfb": True
            })
            
            # Store task reference for cleanup
            session["task"] = task
            
            # Start the task
            await task.queue_frames([
                TextFrame(text="Hello! Welcome to our restaurant. I'm your voice ordering assistant. How can I help you today?")
            ])
            
            # Run the task (this will block until the session ends)
            await task.run()
            
            return True
            
        except Exception as e:
            logger.error(f"Error starting voice bot: {str(e)}")
            return False
    
    async def end_voice_session(self, session_id: str) -> bool:
        """End a voice ordering session."""
        try:
            session = self.active_sessions.get(session_id)
            if not session:
                return False
            
            # Stop the pipeline task if running
            if "task" in session:
                try:
                    await session["task"].stop()
                except Exception as e:
                    logger.warning(f"Error stopping pipeline task: {str(e)}")
            
            # Delete the Daily room
            try:
                await self.daily_helper.delete_room(session["room_name"])
            except Exception as e:
                logger.warning(f"Error deleting Daily room: {str(e)}")
            
            # Remove from active sessions
            del self.active_sessions[session_id]
            
            return True
            
        except Exception as e:
            logger.error(f"Error ending voice session: {str(e)}")
            return False
    
    async def get_session_info(self, session_id: str) -> Optional[Dict[str, Any]]:
        """Get information about a voice session."""
        return self.active_sessions.get(session_id)
    
    async def list_active_sessions(self) -> Dict[str, Dict[str, Any]]:
        """List all active voice sessions."""
        return self.active_sessions.copy()
    
    async def cleanup_expired_sessions(self) -> int:
        """Clean up expired sessions (older than 1 hour)."""
        current_time = asyncio.get_event_loop().time()
        expired_sessions = []
        
        for session_id, session in self.active_sessions.items():
            if current_time - session["created_at"] > 3600:  # 1 hour
                expired_sessions.append(session_id)
        
        for session_id in expired_sessions:
            await self.end_voice_session(session_id)
        
        return len(expired_sessions)

# Global instance
voice_streaming_service = VoiceStreamingService()