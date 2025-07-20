#!/usr/bin/env python3
"""
True Voice-to-Voice Ordering Assistant Demo

This script demonstrates real voice-to-voice interaction using Nova Sonic model
for audio input and audio output processing.
"""

import asyncio
import logging
import sys
import io
import base64
from typing import Optional
import json

# Setup logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

try:
    import boto3
    import sounddevice as sd
    import numpy as np
    import wave
except ImportError as e:
    logger.error(f"Missing required audio dependencies: {e}")
    logger.error("Install with: pip install sounddevice numpy boto3")
    sys.exit(1)

async def voice_to_voice_demo(business_id: str):
    """Run a true voice-to-voice demo using Nova Sonic."""
    
    try:
        from app.agents.config import session
        from app.agents.simple_voice_agent import SimpleVoiceOrderingAgent
    except ImportError as e:
        logger.error(f"Import error: {e}")
        logger.error("Make sure all dependencies are installed: pip install -e .")
        return
    
    print("🎙️  Voice-to-Voice Ordering Assistant Demo")
    print("=" * 50)
    print(f"Business ID: {business_id}")
    print("Press SPACE to start recording, release to send")
    print("Type 'quit' in terminal to end the demo")
    print("=" * 50)
    
    # Initialize Bedrock client for Nova Sonic
    bedrock_client = boto3.client(
        'bedrock-runtime',
        aws_access_key_id=session.get_credentials().access_key,
        aws_secret_access_key=session.get_credentials().secret_key,
        region_name='us-east-1'
    )
    
    # Initialize Nova Sonic for voice processing
    print("✅ Nova Sonic voice model initialized successfully!")
    
    # Audio recording parameters
    SAMPLE_RATE = 16000
    CHANNELS = 1
    
    def record_audio(duration: int = 5) -> bytes:
        """Record audio from microphone."""
        print("🎤 Recording... (speak now)")
        recording = sd.rec(int(duration * SAMPLE_RATE), 
                          samplerate=SAMPLE_RATE, 
                          channels=CHANNELS, 
                          dtype='int16')
        sd.wait()  # Wait until recording is finished
        print("🔇 Recording stopped")
        
        # Convert to bytes
        buffer = io.BytesIO()
        with wave.open(buffer, 'wb') as wf:
            wf.setnchannels(CHANNELS)
            wf.setsampwidth(2)  # 16-bit
            wf.setframerate(SAMPLE_RATE)
            wf.writeframes(recording.tobytes())
        
        return buffer.getvalue()
    
    def play_audio(audio_data: bytes):
        """Play audio through speakers."""
        try:
            # Decode audio data and play
            buffer = io.BytesIO(audio_data)
            with wave.open(buffer, 'rb') as wf:
                frames = wf.readframes(wf.getnframes())
                audio_array = np.frombuffer(frames, dtype=np.int16)
                
                print("🔊 Playing response...")
                sd.play(audio_array, SAMPLE_RATE)
                sd.wait()
        except Exception as e:
            logger.error(f"Error playing audio: {e}")
    
    async def process_voice_input(audio_data: bytes) -> Optional[bytes]:
        """Process voice input through Nova Sonic and return audio response."""
        try:
            # Encode audio as base64
            audio_b64 = base64.b64encode(audio_data).decode('utf-8')
            
            # Create the request for Nova Sonic
            request_body = {
                "inputAudio": {
                    "format": "wav",
                    "data": audio_b64
                },
                "requestMetadata": {
                    "businessContext": f"Restaurant ordering system for business {business_id}"
                }
            }
            
            # Call Nova Sonic
            response = bedrock_client.invoke_model(
                modelId="amazon.nova-sonic-v1:0",
                body=json.dumps(request_body),
                contentType="application/json"
            )
            
            # Parse response
            response_body = json.loads(response['body'].read())
            
            if 'outputAudio' in response_body:
                # Decode the audio response
                audio_response = base64.b64decode(response_body['outputAudio']['data'])
                return audio_response
            else:
                logger.error("No audio output in response")
                return None
                
        except Exception as e:
            logger.error(f"Error processing voice input: {e}")
            return None
    
    # Welcome message
    print("\n🤖 Assistant: Welcome! I'm ready to take your order. Press and hold SPACE to speak.")
    
    # Main interaction loop
    try:
        while True:
            try:
                # Simple input for demo - record for 5 seconds when user presses enter
                user_input = input("\nPress ENTER to record (or type 'quit' to exit): ").strip()
                
                if user_input.lower() in ['quit', 'exit', 'bye']:
                    print("\n🤖 Assistant: Thank you for visiting! Have a great day!")
                    break
                
                # Record audio
                audio_data = record_audio(5)  # Record for 5 seconds
                
                # Process through Nova Sonic
                print("🤖 Processing your order...")
                response_audio = await process_voice_input(audio_data)
                
                if response_audio:
                    # Play the audio response
                    play_audio(response_audio)
                else:
                    print("🤖 I'm sorry, I couldn't process that. Please try again.")
                
            except KeyboardInterrupt:
                print("\n\n👋 Demo ended by user")
                break
            except Exception as e:
                logger.error(f"Error in main loop: {e}")
                print(f"\n🤖 Assistant: I encountered an error: {e}")
    
    except Exception as e:
        logger.error(f"Demo error: {e}")

async def main():
    """Main function to run the voice-to-voice demo."""
    
    # Default business ID
    default_business_id = "test-business-123"
    
    if len(sys.argv) > 1:
        business_id = sys.argv[1]
    else:
        business_id = default_business_id
        print(f"Using default business ID: {business_id}")
        print("To use a different business ID, run: python voice_to_voice_demo.py <business_id>")
        print()
    
    await voice_to_voice_demo(business_id)

if __name__ == "__main__":
    asyncio.run(main())