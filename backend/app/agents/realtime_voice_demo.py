#!/usr/bin/env python3
"""
Real-Time Voice-to-Voice Ordering Assistant Demo

This script demonstrates real-time voice conversation using Nova Sonic's 
bidirectional streaming API for natural voice interactions.
"""

import asyncio
import logging
import sys
import json
import base64
from typing import Optional, AsyncGenerator
import threading
import queue
import time

# Setup logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

try:
    import boto3
    import sounddevice as sd
    import numpy as np
except ImportError as e:
    logger.error(f"Missing required dependencies: {e}")
    logger.error("Install with: uv pip install sounddevice numpy boto3")
    sys.exit(1)

class RealTimeVoiceAgent:
    """Real-time voice agent using Nova Sonic bidirectional streaming."""
    
    def __init__(self, business_id: str):
        self.business_id = business_id
        self.client = None
        self.stream = None
        self.is_recording = False
        self.audio_queue = queue.Queue()
        self.response_queue = queue.Queue()
        
        # Audio parameters
        self.SAMPLE_RATE = 16000
        self.CHUNK_SIZE = 1024
        self.CHANNELS = 1
        
        self._setup_bedrock_client()
    
    def _setup_bedrock_client(self):
        """Initialize Bedrock client with proper credentials."""
        try:
            from app.agents.config import session
            
            self.client = boto3.client(
                'bedrock-runtime',
                aws_access_key_id=session.get_credentials().access_key,
                aws_secret_access_key=session.get_credentials().secret_key,
                region_name='us-east-1'
            )
            logger.info("✅ Bedrock client initialized")
        except Exception as e:
            logger.error(f"Failed to setup Bedrock client: {e}")
            raise
    
    def audio_callback(self, indata, frames, time, status):
        """Callback for continuous audio recording."""
        if status:
            logger.warning(f"Audio callback status: {status}")
        
        if self.is_recording:
            # Convert to bytes and add to queue
            audio_bytes = (indata * 32767).astype(np.int16).tobytes()
            self.audio_queue.put(audio_bytes)
    
    async def start_streaming_conversation(self):
        """Start the bidirectional streaming conversation."""
        try:
            # Initialize the streaming session
            request_body = {
                "modelId": "amazon.nova-sonic-v1:0",
                "contentType": "application/json",
                "accept": "application/json"
            }
            
            # Start bidirectional stream
            response = self.client.invoke_model_with_bidirectional_stream(**request_body)
            self.stream = response['body']
            
            logger.info("🎙️ Real-time voice conversation started!")
            logger.info("👤 Start speaking naturally - I'll respond in real-time")
            logger.info("🔇 Press Ctrl+C to end conversation")
            
            # Start audio recording
            self.is_recording = True
            with sd.InputStream(
                callback=self.audio_callback,
                samplerate=self.SAMPLE_RATE,
                channels=self.CHANNELS,
                dtype=np.float32
            ):
                # Run the conversation loop
                await asyncio.gather(
                    self._send_audio_loop(),
                    self._receive_audio_loop(),
                    self._play_responses()
                )
                
        except Exception as e:
            logger.error(f"Streaming conversation error: {e}")
        finally:
            self.is_recording = False
            if self.stream:
                self.stream.close()
    
    async def _send_audio_loop(self):
        """Continuously send audio chunks to Nova Sonic."""
        try:
            while self.is_recording:
                try:
                    # Get audio from queue (non-blocking)
                    audio_chunk = self.audio_queue.get_nowait()
                    
                    # Encode and send to Nova Sonic
                    audio_b64 = base64.b64encode(audio_chunk).decode('utf-8')
                    
                    message = {
                        "inputAudio": {
                            "format": "pcm",
                            "data": audio_b64
                        },
                        "requestMetadata": {
                            "businessContext": f"Restaurant ordering for business {self.business_id}"
                        }
                    }
                    
                    # Send to stream
                    await self._send_to_stream(message)
                    
                except queue.Empty:
                    # No audio available, continue
                    await asyncio.sleep(0.01)
                except Exception as e:
                    logger.error(f"Error sending audio: {e}")
                    
        except Exception as e:
            logger.error(f"Send audio loop error: {e}")
    
    async def _receive_audio_loop(self):
        """Continuously receive audio responses from Nova Sonic."""
        try:
            async for event in self.stream:
                if 'chunk' in event:
                    chunk = event['chunk']
                    if 'bytes' in chunk:
                        # Parse the response
                        response_data = json.loads(chunk['bytes'].decode('utf-8'))
                        
                        if 'outputAudio' in response_data:
                            # Decode audio response
                            audio_data = base64.b64decode(response_data['outputAudio']['data'])
                            self.response_queue.put(audio_data)
                            
                        if 'transcript' in response_data:
                            # Log the transcript for debugging
                            transcript = response_data['transcript']
                            logger.info(f"🤖 Assistant: {transcript}")
                            
        except Exception as e:
            logger.error(f"Receive audio loop error: {e}")
    
    async def _play_responses(self):
        """Play audio responses as they arrive."""
        try:
            while self.is_recording:
                try:
                    # Get response audio (non-blocking)
                    audio_data = self.response_queue.get_nowait()
                    
                    # Convert to numpy array and play
                    audio_array = np.frombuffer(audio_data, dtype=np.int16)
                    
                    # Play audio
                    sd.play(audio_array, self.SAMPLE_RATE)
                    
                except queue.Empty:
                    # No audio response available
                    await asyncio.sleep(0.01)
                except Exception as e:
                    logger.error(f"Error playing response: {e}")
                    
        except Exception as e:
            logger.error(f"Play responses error: {e}")
    
    async def _send_to_stream(self, message):
        """Send message to the bidirectional stream."""
        try:
            message_json = json.dumps(message)
            message_bytes = message_json.encode('utf-8')
            
            # Send to stream (this would need the actual streaming implementation)
            # For now, this is a placeholder for the bidirectional stream send
            logger.debug("Sending audio chunk to Nova Sonic")
            
        except Exception as e:
            logger.error(f"Error sending to stream: {e}")

async def main():
    """Main function to run the real-time voice demo."""
    
    # Get business ID from command line
    business_id = sys.argv[1] if len(sys.argv) > 1 else "test-business-123"
    
    print("🎙️  Real-Time Voice Ordering Assistant")
    print("=" * 50)
    print(f"Business ID: {business_id}")
    print("🎤 Speak naturally - I'll respond in real-time!")
    print("🔇 Press Ctrl+C to end conversation")
    print("=" * 50)
    
    # Initialize the voice agent
    try:
        agent = RealTimeVoiceAgent(business_id)
        
        # Start the real-time conversation
        await agent.start_streaming_conversation()
        
    except KeyboardInterrupt:
        print("\n👋 Real-time conversation ended")
    except Exception as e:
        logger.error(f"Demo error: {e}")

if __name__ == "__main__":
    asyncio.run(main())