import asyncio
import json
import sys
import os

# Add the backend directory to the path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', '..'))

from app.agents.menu_agent import (
    menu_intelligent_agent,
    analyze_menu_image,
    get_menu_recommendations,
    search_menu_items,
    get_allergen_information,
    menu_agent
)
from app.agents.orchestrator import orchestrator

async def test_menu_agent():
    """Test the menu intelligent agent functionality"""
    
    print("=" * 60)
    print("TESTING MENU INTELLIGENT AGENT")
    print("=" * 60)
    
    # Test 1: Basic menu intelligence query
    print("\n1. Testing basic menu intelligence query:")
    print("-" * 40)
    
    try:
        query = "What are the most popular appetizers typically found on restaurant menus?"
        response = menu_intelligent_agent(query)
        print(f"Query: {query}")
        print(f"Response: {response}")
    except Exception as e:
        print(f"Error in basic query test: {e}")
    
    # Test 2: Menu recommendations for dietary preferences
    print("\n2. Testing menu recommendations for dietary preferences:")
    print("-" * 40)
    
    try:
        dietary_prefs = "vegetarian, gluten-free, no nuts"
        response = get_menu_recommendations(dietary_prefs)
        print(f"Dietary Preferences: {dietary_prefs}")
        print(f"Response: {response}")
    except Exception as e:
        print(f"Error in dietary recommendations test: {e}")
    
    # Test 3: Search for menu items
    print("\n3. Testing menu item search:")
    print("-" * 40)
    
    try:
        search_term = "pasta"
        response = search_menu_items(search_term)
        print(f"Search Term: {search_term}")
        print(f"Response: {response}")
    except Exception as e:
        print(f"Error in menu search test: {e}")
    
    # Test 4: Allergen information
    print("\n4. Testing allergen information:")
    print("-" * 40)
    
    try:
        allergen = "peanuts"
        response = get_allergen_information(allergen)
        print(f"Allergen: {allergen}")
        print(f"Response: {response}")
    except Exception as e:
        print(f"Error in allergen information test: {e}")
    
    # Test 5: Test with orchestrator
    print("\n5. Testing with orchestrator:")
    print("-" * 40)
    
    try:
        customer_query = "Can you help me find vegetarian options that are also dairy-free?"
        print(f"Customer Query: {customer_query}")
        print("Orchestrator Response:")
        
        agent_stream = orchestrator.stream_async(customer_query)
        async for event in agent_stream:
            if "data" in event:
                print(event["data"], end="", flush=True)
        print()  # New line after streaming
        
    except Exception as e:
        print(f"Error in orchestrator test: {e}")
    
    print("\n" + "=" * 60)
    print("MENU AGENT TESTING COMPLETED")
    print("=" * 60)

async def test_menu_analysis_workflow():
    """Test the complete menu analysis workflow"""
    
    print("\n" + "=" * 60)
    print("TESTING MENU ANALYSIS WORKFLOW")
    print("=" * 60)
    
    # Simulate a menu analysis scenario
    sample_menu_data = {
        "restaurant_info": {
            "name": "Sample Restaurant",
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
    }
    
    menu_data_json = json.dumps(sample_menu_data)
    
    # Test with sample menu data
    print("\n1. Testing menu analysis with sample data:")
    print("-" * 40)
    
    try:
        query = "What vegetarian options are available and what are their prices?"
        response = menu_intelligent_agent(query, menu_data_json)
        print(f"Query: {query}")
        print(f"Response: {response}")
    except Exception as e:
        print(f"Error in menu analysis test: {e}")
    
    # Test allergen checking with menu data
    print("\n2. Testing allergen checking with menu data:")
    print("-" * 40)
    
    try:
        allergen = "dairy"
        response = get_allergen_information(allergen, menu_data_json)
        print(f"Allergen: {allergen}")
        print(f"Response: {response}")
    except Exception as e:
        print(f"Error in allergen checking test: {e}")
    
    print("\n" + "=" * 60)
    print("MENU ANALYSIS WORKFLOW TESTING COMPLETED")
    print("=" * 60)

if __name__ == "__main__":
    # Run the tests
    asyncio.run(test_menu_agent())
    asyncio.run(test_menu_analysis_workflow())