import requests
import json
import asyncio
import websockets
from typing import Dict, Any, Optional
import logging
from datetime import datetime, timedelta
import time

# Setup logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class TablyCLI:
    """Comprehensive CLI for testing all Tably API endpoints"""
    
    def __init__(self, base_url: str = "http://localhost:8000"):
        self.base_url = base_url
        self.auth_token = None
        self.headers = {
            "Content-Type": "application/json",
            "Accept": "application/json"
        }
        self.session = requests.Session()
        
    def set_auth_token(self, token: str):
        """Set authentication token"""
        self.auth_token = token
        self.headers["Authorization"] = f"Bearer {token}"
        self.session.headers.update({"Authorization": f"Bearer {token}"})
        
    def test_auth_endpoints(self):
        """Test authentication endpoints"""
        print("🔐 TESTING AUTHENTICATION ENDPOINTS")
        print("=" * 50)
        
        # Test health check
        try:
            response = self.session.get(f"{self.base_url}/health")
            print(f"Health Check: {response.status_code} - {response.json()}")
        except Exception as e:
            print(f"Health Check Error: {e}")
        
        print()
        
    def test_menu_agent_endpoints(self):
        """Test menu agent endpoints"""
        print("🤖 TESTING MENU AGENT ENDPOINTS")
        print("=" * 50)
        
        endpoints = [
            ("/api/menu-agent/health", "GET", None),
            ("/api/menu-agent/chat", "POST", {
                "query": "What vegetarian options do you have?",
                "menu_data": None
            }),
            ("/api/menu-agent/recommendations", "POST", {
                "dietary_preferences": "vegetarian, no nuts",
                "menu_data": None
            }),
            ("/api/menu-agent/search", "POST", {
                "search_term": "pizza",
                "menu_data": None
            }),
            ("/api/menu-agent/allergen-info", "POST", {
                "allergen": "dairy",
                "menu_data": None
            })
        ]
        
        for endpoint, method, data in endpoints:
            try:
                if method == "GET":
                    response = self.session.get(f"{self.base_url}{endpoint}")
                else:
                    response = self.session.post(f"{self.base_url}{endpoint}", json=data)
                
                print(f"{method} {endpoint}: {response.status_code}")
                if response.status_code < 400:
                    result = response.json()
                    print(f"  Response: {result.get('response', 'Success')[:100]}...")
                else:
                    print(f"  Error: {response.text}")
            except Exception as e:
                print(f"  Exception: {e}")
        
        print()
        
    def test_ordering_agents_endpoints(self):
        """Test ordering agents endpoints"""
        print("🍽️ TESTING ORDERING AGENTS ENDPOINTS")
        print("=" * 50)
        
        endpoints = [
            ("/api/ordering/health", "GET", None),
            ("/api/ordering/order-assistant", "POST", {
                "customer_request": "I want to order a large pizza",
                "menu_data": None,
                "order_context": None
            }),
            ("/api/ordering/recommendations", "POST", {
                "customer_preferences": "I love spicy food",
                "dietary_restrictions": "vegetarian",
                "budget_range": "under $25"
            }),
            ("/api/ordering/translate", "POST", {
                "customer_message": "Hola, quiero pedir una pizza",
                "source_language": "spanish",
                "target_language": "english"
            }),
            ("/api/ordering/multilingual-order", "POST", {
                "customer_message": "Je voudrais commander une salade",
                "source_language": "french"
            }),
            ("/api/ordering/supported-languages", "GET", None),
            ("/api/ordering/order-flow-help", "GET", None)
        ]
        
        for endpoint, method, data in endpoints:
            try:
                if method == "GET":
                    response = self.session.get(f"{self.base_url}{endpoint}")
                else:
                    response = self.session.post(f"{self.base_url}{endpoint}", json=data)
                
                print(f"{method} {endpoint}: {response.status_code}")
                if response.status_code < 400:
                    result = response.json()
                    if 'response' in result:
                        print(f"  Response: {result['response'][:100]}...")
                    else:
                        print(f"  Success: {list(result.keys())}")
                else:
                    print(f"  Error: {response.text}")
            except Exception as e:
                print(f"  Exception: {e}")
        
        print()
        
    def test_orders_endpoints(self):
        """Test order management endpoints"""
        print("📦 TESTING ORDER MANAGEMENT ENDPOINTS")
        print("=" * 50)
        
        # Create a test order first
        order_data = {
            "business_id": "test_business",
            "customer_info": {
                "user_id": "test_user",
                "name": "John Doe",
                "email": "john@example.com",
                "preferred_language": "english"
            },
            "order_type": "dine_in",
            "items": [
                {
                    "menu_item_id": "item_1",
                    "name": "Margherita Pizza",
                    "quantity": 1,
                    "unit_price": 18.99,
                    "total_price": 18.99
                }
            ]
        }
        
        order_id = None
        
        # Test create order
        try:
            response = self.session.post(f"{self.base_url}/api/orders/create", json=order_data)
            print(f"POST /api/orders/create: {response.status_code}")
            if response.status_code < 400:
                result = response.json()
                order_id = result.get('order', {}).get('id')
                print(f"  Created order: {order_id}")
            else:
                print(f"  Error: {response.text}")
        except Exception as e:
            print(f"  Exception: {e}")
        
        # Test other order endpoints
        other_endpoints = [
            ("/api/orders/list", "GET", None),
        ]
        
        if order_id:
            other_endpoints.extend([
                (f"/api/orders/{order_id}", "GET", None),
                (f"/api/orders/{order_id}/chat", "POST", {"message": "What's my order status?"}),
                (f"/api/orders/{order_id}/track", "GET", None)
            ])
        
        for endpoint, method, data in other_endpoints:
            try:
                if method == "GET":
                    response = self.session.get(f"{self.base_url}{endpoint}")
                else:
                    response = self.session.post(f"{self.base_url}{endpoint}", json=data)
                
                print(f"{method} {endpoint}: {response.status_code}")
                if response.status_code < 400:
                    print(f"  Success")
                else:
                    print(f"  Error: {response.text}")
            except Exception as e:
                print(f"  Exception: {e}")
        
        print()
        
    def test_customer_preferences_endpoints(self):
        """Test customer preferences endpoints"""
        print("👤 TESTING CUSTOMER PREFERENCES ENDPOINTS")
        print("=" * 50)
        
        endpoints = [
            ("/api/customer/preferences", "GET", None),
            ("/api/customer/preferences/recommendations", "GET", None),
            ("/api/customer/preferences/summary", "GET", None),
            ("/api/customer/agent-sessions", "GET", None),
            ("/api/customer/agent-sessions", "POST", {
                "business_id": "test_business",
                "language": "english"
            })
        ]
        
        for endpoint, method, data in endpoints:
            try:
                if method == "GET":
                    response = self.session.get(f"{self.base_url}{endpoint}")
                else:
                    response = self.session.post(f"{self.base_url}{endpoint}", json=data)
                
                print(f"{method} {endpoint}: {response.status_code}")
                if response.status_code < 400:
                    print(f"  Success")
                else:
                    print(f"  Error: {response.text}")
            except Exception as e:
                print(f"  Exception: {e}")
        
        print()
        
    def test_order_tracking_endpoints(self):
        """Test order tracking endpoints"""
        print("📍 TESTING ORDER TRACKING ENDPOINTS")
        print("=" * 50)
        
        # For demo purposes, we'll test without a real order ID
        test_order_id = "test_order_123"
        
        endpoints = [
            (f"/api/tracking/orders/{test_order_id}/status", "GET", None),
            (f"/api/tracking/orders/{test_order_id}/tracking", "GET", None),
            (f"/api/tracking/orders/{test_order_id}/notifications", "GET", None),
        ]
        
        for endpoint, method, data in endpoints:
            try:
                if method == "GET":
                    response = self.session.get(f"{self.base_url}{endpoint}")
                else:
                    response = self.session.post(f"{self.base_url}{endpoint}", json=data)
                
                print(f"{method} {endpoint}: {response.status_code}")
                if response.status_code == 404:
                    print(f"  Expected: Order not found (demo)")
                elif response.status_code < 400:
                    print(f"  Success")
                else:
                    print(f"  Error: {response.text}")
            except Exception as e:
                print(f"  Exception: {e}")
        
        print()
        
    def test_menu_endpoints(self):
        """Test menu-related endpoints"""
        print("📋 TESTING MENU ENDPOINTS")
        print("=" * 50)
        
        endpoints = [
            ("/api/menu-image-analysis/supported-formats", "GET", None),
        ]
        
        for endpoint, method, data in endpoints:
            try:
                if method == "GET":
                    response = self.session.get(f"{self.base_url}{endpoint}")
                else:
                    response = self.session.post(f"{self.base_url}{endpoint}", json=data)
                
                print(f"{method} {endpoint}: {response.status_code}")
                if response.status_code < 400:
                    result = response.json()
                    print(f"  Success: {list(result.keys())}")
                else:
                    print(f"  Error: {response.text}")
            except Exception as e:
                print(f"  Exception: {e}")
        
        print()
        
    def test_streaming_endpoints(self):
        """Test streaming endpoints"""
        print("🔄 TESTING STREAMING ENDPOINTS")
        print("=" * 50)
        
        # Test Server-Sent Events
        try:
            response = self.session.post(
                f"{self.base_url}/api/ordering/chat/stream",
                json={"message": "Hello, I need help with ordering"},
                stream=True
            )
            print(f"POST /api/ordering/chat/stream: {response.status_code}")
            
            if response.status_code < 400:
                print("  Streaming response received")
                # Read a few lines of the stream
                for i, line in enumerate(response.iter_lines()):
                    if i >= 3:  # Just read first 3 lines
                        break
                    if line:
                        print(f"    {line.decode()}")
            else:
                print(f"  Error: {response.text}")
                
        except Exception as e:
            print(f"  Exception: {e}")
        
        print()
        
    async def test_websocket_endpoints(self):
        """Test WebSocket endpoints"""
        print("🔌 TESTING WEBSOCKET ENDPOINTS")
        print("=" * 50)
        
        # Test WebSocket connection
        try:
            ws_url = f"ws://localhost:8000/api/tracking/orders/test_order_123/track-live"
            
            async with websockets.connect(ws_url) as websocket:
                print("WebSocket connection established")
                
                # Send a heartbeat
                await websocket.send("heartbeat")
                
                # Wait for response
                try:
                    response = await asyncio.wait_for(websocket.recv(), timeout=5.0)
                    print(f"  Response: {response}")
                except asyncio.TimeoutError:
                    print("  Timeout waiting for response")
                
        except Exception as e:
            print(f"  WebSocket error: {e}")
        
        print()
        
    def run_comprehensive_tests(self):
        """Run all endpoint tests"""
        print("🚀 COMPREHENSIVE TABLY API ENDPOINT TESTS")
        print("=" * 80)
        print(f"Base URL: {self.base_url}")
        print(f"Timestamp: {datetime.now().isoformat()}")
        print("=" * 80)
        
        # Note: In production, you would authenticate first
        print("⚠️  Note: Running tests without authentication")
        print("   In production, authenticate first with /api/auth/login")
        print()
        
        # Run all tests
        self.test_auth_endpoints()
        self.test_menu_agent_endpoints()
        self.test_ordering_agents_endpoints()
        self.test_orders_endpoints()
        self.test_customer_preferences_endpoints()
        self.test_order_tracking_endpoints()
        self.test_menu_endpoints()
        self.test_streaming_endpoints()
        
        print("🏁 ALL ENDPOINT TESTS COMPLETED")
        print("=" * 80)
        
    def interactive_mode(self):
        """Interactive mode for manual testing"""
        print("🎮 INTERACTIVE MODE")
        print("=" * 50)
        print("Available commands:")
        print("  1. test-auth")
        print("  2. test-menu-agent")
        print("  3. test-ordering")
        print("  4. test-orders")
        print("  5. test-preferences")
        print("  6. test-tracking")
        print("  7. test-streaming")
        print("  8. test-all")
        print("  9. quit")
        print()
        
        while True:
            try:
                command = input("Enter command (1-9): ").strip()
                
                if command == "1":
                    self.test_auth_endpoints()
                elif command == "2":
                    self.test_menu_agent_endpoints()
                elif command == "3":
                    self.test_ordering_agents_endpoints()
                elif command == "4":
                    self.test_orders_endpoints()
                elif command == "5":
                    self.test_customer_preferences_endpoints()
                elif command == "6":
                    self.test_order_tracking_endpoints()
                elif command == "7":
                    self.test_streaming_endpoints()
                elif command == "8":
                    self.run_comprehensive_tests()
                elif command == "9":
                    print("Goodbye!")
                    break
                else:
                    print("Invalid command. Please enter 1-9.")
                    
            except KeyboardInterrupt:
                print("\nGoodbye!")
                break
            except Exception as e:
                print(f"Error: {e}")

def main():
    """Main function"""
    import sys
    
    cli = TablyCLI()
    
    if len(sys.argv) > 1:
        if sys.argv[1] == "interactive":
            cli.interactive_mode()
        elif sys.argv[1] == "websocket":
            asyncio.run(cli.test_websocket_endpoints())
        else:
            print("Usage: python test_all_endpoints.py [interactive|websocket]")
    else:
        cli.run_comprehensive_tests()

if __name__ == "__main__":
    main()