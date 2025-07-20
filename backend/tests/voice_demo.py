#!/usr/bin/env python3
"""
Demo script for Voice-to-Voice Ordering Assistant

This script demonstrates how to use the voice ordering system with text input/output
for testing purposes without requiring actual voice hardware.
"""

import asyncio
import logging
import sys
from typing import Optional

# Setup logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

async def voice_ordering_demo(business_id: str):
    """Run a demo of the voice ordering system using text input/output."""
    
    try:
        from app.agents.simple_voice_agent import SimpleVoiceOrderingAgent as VoiceOrderingAgent
    except ImportError as e:
        logger.error(f"Import error: {e}")
        logger.error("Make sure all dependencies are installed: pip install -e .")
        return
    
    print("🎙️  Voice Ordering Assistant Demo")
    print("=" * 50)
    print(f"Business ID: {business_id}")
    print("Type 'quit' or 'exit' to end the demo")
    print("=" * 50)
    
    # Initialize the voice ordering agent with voice model enabled
    try:
        agent = VoiceOrderingAgent(business_id=business_id, use_voice_model=True)
        print("✅ Voice ordering agent initialized successfully!")
    except Exception as e:
        logger.error(f"Failed to initialize voice agent: {e}")
        return
    
    # Start the conversation
    print("\n🤖 Assistant: Hello! Welcome to our restaurant. I'm your voice ordering assistant. How can I help you today?")
    
    while True:
        try:
            # Get user input
            user_input = input("\n👤 You: ").strip()
            
            if user_input.lower() in ['quit', 'exit', 'bye']:
                print("\n🤖 Assistant: Thank you for visiting! Have a great day!")
                break
            
            if not user_input:
                continue
            
            # Process through the voice agent
            print("\n🤖 Assistant: ", end="", flush=True)
            response = await agent.process_voice_input(user_input)
            print(response)
            
        except KeyboardInterrupt:
            print("\n\n👋 Demo ended by user")
            break
        except Exception as e:
            logger.error(f"Error processing input: {e}")
            print(f"\n🤖 Assistant: I'm sorry, I encountered an error: {e}")

async def main():
    """Main function to run the demo."""
    
    # Default business ID (you can change this to test with different businesses)
    default_business_id = "test-business-123"
    
    if len(sys.argv) > 1:
        business_id = sys.argv[1]
    else:
        business_id = default_business_id
        print(f"Using default business ID: {business_id}")
        print("To use a different business ID, run: python voice_demo.py <business_id>")
        print()
    
    await voice_ordering_demo(business_id)

if __name__ == "__main__":
    asyncio.run(main())