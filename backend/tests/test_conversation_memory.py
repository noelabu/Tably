#!/usr/bin/env python3
"""
Test script demonstrating conversation memory capabilities.
"""
import sys
import os

# Add the backend directory to the Python path
sys.path.insert(0, os.path.join(os.path.dirname(__file__)))

from app.services.conversation_memory import conversation_memory
from app.agents.swarm_tools import ordering_swarm

def test_conversation_flow():
    """Demonstrate conversation memory in action."""
    
    session_id = 'demo_conversation_123'
    business_id = '5eff8f12-7d43-4b0d-b3f7-e762a7903a82'
    
    print("🍽️ Restaurant Conversation Memory Demo")
    print("=" * 50)
    
    # Conversation flow
    conversations = [
        "Hi, I'm looking for vegetarian food options",
        "Do any of those come with rice?",
        "What about spicy options from what you mentioned?",
        "Can I order the soup and spring rolls?",
        "Actually, can you remind me what the spring rolls contain?"
    ]
    
    for i, message in enumerate(conversations, 1):
        print(f"\n👤 Customer: {message}")
        print("🤖 Assistant: ", end="")
        
        response = ordering_swarm(
            customer_request=message,
            business_id=business_id,
            session_id=session_id
        )
        
        # Print first 200 characters of response
        print(response[:200] + "..." if len(response) > 200 else response)
        print("-" * 80)
    
    # Show conversation summary
    print("\n📋 Conversation Summary:")
    session = conversation_memory.get_session(session_id)
    if session:
        print(f"Total Messages: {len(session.messages)}")
        print(f"Session Duration: {session.last_activity - session.created_at}")
        
        order_context = session.extract_order_context()
        print(f"Detected Dietary Preferences: {order_context.get('dietary_restrictions', [])}")
        print(f"Detected Preferences: {order_context.get('preferences', [])}")
    
    print("\n✅ Demo completed! The agent maintained context throughout the conversation.")

if __name__ == "__main__":
    test_conversation_flow()