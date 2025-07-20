import requests
import json
from typing import Dict, Any
import logging

# Setup logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class MenuAgentEndpointTester:
    """Test class for menu agent endpoints"""
    
    def __init__(self, base_url: str = "http://localhost:8000"):
        self.base_url = base_url
        self.headers = {
            "Content-Type": "application/json",
            "Accept": "application/json"
        }
        self.auth_token = None
        
    def set_auth_token(self, token: str):
        """Set authentication token for requests"""
        self.auth_token = token
        self.headers["Authorization"] = f"Bearer {token}"
        
    def test_menu_agent_health(self) -> Dict[str, Any]:
        """Test the menu agent health endpoint"""
        try:
            url = f"{self.base_url}/api/menu-agent/health"
            response = requests.get(url, headers=self.headers)
            
            print(f"Health Check Status: {response.status_code}")
            print(f"Health Check Response: {response.json()}")
            
            return response.json()
            
        except Exception as e:
            logger.error(f"Health check failed: {e}")
            return {"error": str(e)}
    
    def test_menu_agent_chat(self, query: str, menu_data: str = None) -> Dict[str, Any]:
        """Test the menu agent chat endpoint"""
        try:
            url = f"{self.base_url}/api/menu-agent/chat"
            
            payload = {
                "query": query,
                "menu_data": menu_data
            }
            
            response = requests.post(url, json=payload, headers=self.headers)
            
            print(f"Chat Status: {response.status_code}")
            print(f"Chat Response: {response.json()}")
            
            return response.json()
            
        except Exception as e:
            logger.error(f"Chat test failed: {e}")
            return {"error": str(e)}
    
    def test_menu_recommendations(self, dietary_preferences: str, menu_data: str = None) -> Dict[str, Any]:
        """Test the menu recommendations endpoint"""
        try:
            url = f"{self.base_url}/api/menu-agent/recommendations"
            
            payload = {
                "dietary_preferences": dietary_preferences,
                "menu_data": menu_data
            }
            
            response = requests.post(url, json=payload, headers=self.headers)
            
            print(f"Recommendations Status: {response.status_code}")
            print(f"Recommendations Response: {response.json()}")
            
            return response.json()
            
        except Exception as e:
            logger.error(f"Recommendations test failed: {e}")
            return {"error": str(e)}
    
    def test_menu_search(self, search_term: str, menu_data: str = None) -> Dict[str, Any]:
        """Test the menu search endpoint"""
        try:
            url = f"{self.base_url}/api/menu-agent/search"
            
            payload = {
                "search_term": search_term,
                "menu_data": menu_data
            }
            
            response = requests.post(url, json=payload, headers=self.headers)
            
            print(f"Search Status: {response.status_code}")
            print(f"Search Response: {response.json()}")
            
            return response.json()
            
        except Exception as e:
            logger.error(f"Search test failed: {e}")
            return {"error": str(e)}
    
    def test_allergen_information(self, allergen: str, menu_data: str = None) -> Dict[str, Any]:
        """Test the allergen information endpoint"""
        try:
            url = f"{self.base_url}/api/menu-agent/allergen-info"
            
            payload = {
                "allergen": allergen,
                "menu_data": menu_data
            }
            
            response = requests.post(url, json=payload, headers=self.headers)
            
            print(f"Allergen Info Status: {response.status_code}")
            print(f"Allergen Info Response: {response.json()}")
            
            return response.json()
            
        except Exception as e:
            logger.error(f"Allergen info test failed: {e}")
            return {"error": str(e)}
    
    def run_all_tests(self):
        """Run all endpoint tests"""
        print("=" * 60)
        print("MENU AGENT ENDPOINT TESTS")
        print("=" * 60)
        
        # Sample menu data for testing
        sample_menu_data = json.dumps({
            "restaurant_info": {
                "name": "Test Restaurant",
                "cuisine_type": "Italian"
            },
            "menu_categories": ["Appetizers", "Pasta", "Pizza", "Desserts"],
            "menu_items": [
                {
                    "name": "Margherita Pizza",
                    "category": "Pizza",
                    "price": 15.99,
                    "description": "Fresh tomato sauce, mozzarella, basil",
                    "allergens": ["dairy", "gluten"],
                    "dietary_info": ["vegetarian"]
                },
                {
                    "name": "Chicken Alfredo",
                    "category": "Pasta",
                    "price": 18.99,
                    "description": "Grilled chicken, fettuccine, cream sauce",
                    "allergens": ["dairy", "gluten"],
                    "dietary_info": []
                },
                {
                    "name": "Caesar Salad",
                    "category": "Appetizers",
                    "price": 12.99,
                    "description": "Romaine lettuce, parmesan, croutons, caesar dressing",
                    "allergens": ["dairy", "gluten"],
                    "dietary_info": ["vegetarian"]
                }
            ]
        })
        
        # Test 1: Health check
        print("\n1. Testing Health Check:")
        print("-" * 30)
        self.test_menu_agent_health()
        
        # Test 2: Chat functionality
        print("\n2. Testing Chat Functionality:")
        print("-" * 30)
        self.test_menu_agent_chat(
            "What vegetarian options are available?", 
            sample_menu_data
        )
        
        # Test 3: Recommendations
        print("\n3. Testing Recommendations:")
        print("-" * 30)
        self.test_menu_recommendations(
            "vegetarian, gluten-free", 
            sample_menu_data
        )
        
        # Test 4: Search
        print("\n4. Testing Search:")
        print("-" * 30)
        self.test_menu_search(
            "pizza", 
            sample_menu_data
        )
        
        # Test 5: Allergen information
        print("\n5. Testing Allergen Information:")
        print("-" * 30)
        self.test_allergen_information(
            "dairy", 
            sample_menu_data
        )
        
        print("\n" + "=" * 60)
        print("ENDPOINT TESTING COMPLETED")
        print("=" * 60)

def main():
    """Main function to run the tests"""
    # Initialize tester
    tester = MenuAgentEndpointTester()
    
    # Note: In a real scenario, you would need to:
    # 1. Start the FastAPI server
    # 2. Get an authentication token
    # 3. Set the token using tester.set_auth_token(token)
    
    # For now, run tests without auth (they will fail with 401, but structure is tested)
    print("Starting Menu Agent Endpoint Tests...")
    print("Note: These tests will fail without authentication token")
    print("To run with authentication:")
    print("1. Start the FastAPI server")
    print("2. Get an auth token from /api/auth/login")
    print("3. Set the token using tester.set_auth_token(token)")
    
    tester.run_all_tests()

if __name__ == "__main__":
    main()