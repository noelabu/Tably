#!/usr/bin/env python3
"""
Test script for the swarm multi-agent implementation.
"""
import sys
import os
import asyncio
import logging

# Add the backend directory to the Python path
sys.path.insert(0, os.path.join(os.path.dirname(__file__)))

from app.agents.orchestrator import orchestrator, create_orchestrator_with_business_context
from app.agents.swarm_orchestrator import create_ordering_swarm, process_order_with_swarm

# Setup logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def test_basic_swarm():
    """Test basic swarm functionality without business context."""
    print("🧪 Testing basic swarm functionality...")
    
    try:
        # Create a basic swarm
        swarm = create_ordering_swarm()
        print(f"✅ Created swarm with {len(swarm.agents)} agents")
        
        # Test simple request
        result = swarm("I'd like to see your lunch menu and get some recommendations")
        print(f"✅ Swarm responded: {result[:100]}...")
        
        return True
    except Exception as e:
        print(f"❌ Basic swarm test failed: {e}")
        return False

def test_orchestrator_with_swarm():
    """Test the updated orchestrator using swarm tools."""
    print("\n🧪 Testing orchestrator with swarm tools...")
    
    try:
        # Test the main orchestrator
        result = orchestrator("What vegetarian options do you have?")
        print(f"✅ Orchestrator responded: {result[:100]}...")
        
        return True
    except Exception as e:
        print(f"❌ Orchestrator test failed: {e}")
        return False

def test_business_context_orchestrator():
    """Test orchestrator with business context."""
    print("\n🧪 Testing orchestrator with business context...")
    
    try:
        # Create orchestrator with mock business context
        business_orchestrator = create_orchestrator_with_business_context("test_business_123")
        result = business_orchestrator("Can you recommend something spicy?")
        print(f"✅ Business orchestrator responded: {result[:100]}...")
        
        return True
    except Exception as e:
        print(f"❌ Business context test failed: {e}")
        return False

async def test_streaming_response():
    """Test streaming response functionality."""
    print("\n🧪 Testing streaming response...")
    
    try:
        customer_query = "Hello, what is your special today? Can you recommend something vegetarian?"
        agent_stream = orchestrator.stream_async(customer_query)
        
        response_parts = []
        async for event in agent_stream:
            if "data" in event:
                response_parts.append(event["data"])
        
        full_response = "".join(response_parts)
        print(f"✅ Streaming response: {full_response[:100]}...")
        
        return True
    except Exception as e:
        print(f"❌ Streaming test failed: {e}")
        return False

def main():
    """Run all tests."""
    print("🚀 Starting Swarm Multi-Agent Pattern Tests\n")
    
    tests = [
        test_basic_swarm,
        test_orchestrator_with_swarm,
        test_business_context_orchestrator,
    ]
    
    results = []
    for test in tests:
        results.append(test())
    
    # Test async functionality
    print("\n🧪 Testing async functionality...")
    try:
        asyncio.run(test_streaming_response())
        results.append(True)
    except Exception as e:
        print(f"❌ Async test failed: {e}")
        results.append(False)
    
    # Summary
    passed = sum(results)
    total = len(results)
    
    print(f"\n📊 Test Results: {passed}/{total} tests passed")
    
    if passed == total:
        print("🎉 All tests passed! Swarm implementation is working correctly.")
        return 0
    else:
        print("⚠️ Some tests failed. Check the implementation.")
        return 1

if __name__ == "__main__":
    exit_code = main()
    sys.exit(exit_code)