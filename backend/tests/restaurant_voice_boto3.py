#!/usr/bin/env python3
"""
Restaurant Voice Ordering Assistant using boto3 for Nova Sonic

This version uses the standard boto3 library which should be more readily available.
"""

import asyncio
import base64
import json
import logging
import os
import sys
import uuid
import warnings
from typing import Dict, List, Optional, Any
from decimal import Decimal

try:
    import boto3
    import pyaudio
    import numpy as np
except ImportError as e:
    print(f"Missing required dependencies: {e}")
    print("Install with: uv pip install boto3 pyaudio numpy")
    sys.exit(1)

# Import your existing restaurant logic
try:
    from app.db.menu_items import MenuItemsConnection
    from app.db.orders import OrdersConnection
    from app.models.orders import OrderCreate, OrderItemCreate
    from app.agents.config import session
except ImportError as e:
    print(f"Missing restaurant modules: {e}")
    print("Make sure you're running from the backend directory")
    sys.exit(1)

# Suppress warnings
warnings.filterwarnings("ignore")

# Audio configuration
SAMPLE_RATE = 16000
CHANNELS = 1
FORMAT = pyaudio.paInt16
CHUNK_SIZE = 1024

# Setup logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class SimpleVoiceRestaurantAgent:
    """Simple voice restaurant agent using Nova Sonic with boto3."""
    
    def __init__(self, business_id: str):
        self.business_id = business_id
        self.menu_db = MenuItemsConnection()
        self.orders_db = OrdersConnection()
        self.current_order: List[Dict] = []
        self.customer_info: Dict[str, Any] = {}
        
        # Initialize boto3 client
        self.bedrock_client = None
        self._setup_bedrock_client()
        
        # Audio components
        self.audio = pyaudio.PyAudio()
        self.is_recording = False
        
    def _setup_bedrock_client(self):
        """Setup the Bedrock client."""
        try:
            credentials = session.get_credentials()
            self.bedrock_client = boto3.client(
                'bedrock-runtime',
                aws_access_key_id=credentials.access_key,
                aws_secret_access_key=credentials.secret_key,
                region_name='us-east-1'
            )
            logger.info("✅ Bedrock client initialized")
        except Exception as e:
            logger.error(f"Failed to setup Bedrock client: {e}")
            raise
    
    def record_audio(self, duration: int = 5) -> bytes:
        """Record audio from microphone."""
        print("🎤 Recording... (speak now)")
        
        stream = self.audio.open(
            format=FORMAT,
            channels=CHANNELS,
            rate=SAMPLE_RATE,
            input=True,
            frames_per_buffer=CHUNK_SIZE
        )
        
        frames = []
        for _ in range(0, int(SAMPLE_RATE / CHUNK_SIZE * duration)):
            data = stream.read(CHUNK_SIZE)
            frames.append(data)
        
        stream.stop_stream()
        stream.close()
        
        print("🔇 Recording stopped")
        return b''.join(frames)
    
    def play_audio(self, audio_data: bytes):
        """Play audio through speakers."""
        try:
            stream = self.audio.open(
                format=FORMAT,
                channels=CHANNELS,
                rate=24000,  # Nova Sonic output rate
                output=True
            )
            
            print("🔊 Playing response...")
            stream.write(audio_data)
            stream.stop_stream()
            stream.close()
        except Exception as e:
            logger.error(f"Error playing audio: {e}")
    
    async def process_voice_with_nova_sonic(self, audio_data: bytes) -> Optional[bytes]:
        """Process voice input through Nova Sonic and return audio response."""
        try:
            # Encode audio as base64
            audio_b64 = base64.b64encode(audio_data).decode('utf-8')
            
            # Create the request for Nova Sonic
            # This is a simplified approach - the full bidirectional streaming 
            # requires the aws-sdk-bedrock-runtime package
            request_body = {
                "messages": [{
                    "role": "user",
                    "content": [{
                        "type": "audio",
                        "audio": {
                            "format": "wav",
                            "data": audio_b64
                        }
                    }]
                }],
                "inferenceConfig": {
                    "maxTokens": 1024,
                    "temperature": 0.7,
                    "topP": 0.9
                },
                "system": [{"text": f"""You are a friendly, efficient voice ordering assistant for a restaurant (Business ID: {self.business_id}).
                
Your goal is to help customers place orders through natural conversation.

Key responsibilities:
1. Greet customers warmly and ask how you can help
2. Present menu items clearly when asked
3. Help customers add items to their order
4. Handle modifications and special requests
5. Confirm order details before finalizing
6. Collect customer information (name, phone)
7. Be conversational and helpful

Guidelines:
- Speak naturally and conversationally
- Ask clarifying questions when items are ambiguous
- Suggest popular items when customers seem unsure
- Always confirm quantities and special instructions
- Be patient with changes to the order
- Provide clear pricing information
- Keep responses concise but friendly

Available menu items include burgers, pizzas, salads, drinks, and desserts. 
When customers want to place an order, guide them through the process step by step."""}]
            }
            
            # Call Nova Sonic using regular invoke_model
            # Note: This doesn't support real-time streaming, but works for testing
            response = self.bedrock_client.invoke_model(
                modelId="amazon.nova-sonic-v1:0",
                body=json.dumps(request_body),
                contentType="application/json"
            )
            
            # Parse response
            response_body = json.loads(response['body'].read())
            
            if 'output' in response_body and 'message' in response_body['output']:
                message = response_body['output']['message']
                if 'content' in message:
                    for content_item in message['content']:
                        if content_item.get('type') == 'audio' and 'audio' in content_item:
                            # Decode the audio response
                            audio_response = base64.b64decode(content_item['audio']['data'])
                            return audio_response
            
            # If no audio response, return None
            logger.warning("No audio output in response")
            return None
                
        except Exception as e:
            logger.error(f"Error processing voice input: {e}")
            return None
    
    async def run_voice_demo(self):
        """Run the voice ordering demo."""
        print("🎙️  Restaurant Voice Ordering Assistant")
        print("=" * 50)
        print(f"Business ID: {self.business_id}")
        print("Press ENTER to record, or 'quit' to exit")
        print("=" * 50)
        
        print("\n🤖 Assistant: Hello! Welcome to our restaurant. I'm your voice ordering assistant. How can I help you today?")
        
        while True:
            try:
                user_input = input("\nPress ENTER to record (or type 'quit'): ").strip()
                
                if user_input.lower() in ['quit', 'exit', 'bye']:
                    print("\n🤖 Assistant: Thank you for visiting! Have a great day!")
                    break
                
                # Record audio
                audio_data = self.record_audio(5)  # Record for 5 seconds
                
                # Process through Nova Sonic
                print("🤖 Processing your order...")
                response_audio = await self.process_voice_with_nova_sonic(audio_data)
                
                if response_audio:
                    # Play the audio response
                    self.play_audio(response_audio)
                else:
                    print("🤖 I'm sorry, I couldn't process that. Please try again.")
                
            except KeyboardInterrupt:
                print("\n\n👋 Demo ended by user")
                break
            except Exception as e:
                logger.error(f"Error in demo loop: {e}")
                print(f"\n🤖 Assistant: I encountered an error: {e}")
    
    def cleanup(self):
        """Clean up audio resources."""
        if self.audio:
            self.audio.terminate()

async def main():
    """Main function."""
    import argparse
    
    parser = argparse.ArgumentParser(description='Restaurant Voice Ordering with Nova Sonic (boto3)')
    parser.add_argument('business_id', nargs='?', default='5eff8f12-7d43-4b0d-b3f7-e762a7903a82', help='Business ID')
    args = parser.parse_args()

    agent = SimpleVoiceRestaurantAgent(args.business_id)
    
    try:
        await agent.run_voice_demo()
    except Exception as e:
        logger.error(f"Demo error: {e}")
    finally:
        agent.cleanup()

if __name__ == "__main__":
    asyncio.run(main())