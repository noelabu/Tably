import asyncio
import json
from app.agents.ordering_agents import (
    ordering_assistant_agent,
    recommendation_agent,
    translation_agent,
    process_multilingual_order,
    order_recommendation_combo
)
from app.agents.orchestrator import orchestrator

# Sample menu data for testing
sample_menu_data = json.dumps({
    "restaurant_info": {
        "name": "Bella Vista Restaurant",
        "cuisine_type": "Italian",
        "location": "Downtown"
    },
    "menu_categories": ["Appetizers", "Pasta", "Pizza", "Salads", "Desserts", "Beverages"],
    "menu_items": [
        {
            "name": "Margherita Pizza",
            "category": "Pizza",
            "price": 18.99,
            "description": "Fresh tomato sauce, mozzarella, basil",
            "sizes": ["Medium", "Large"],
            "allergens": ["dairy", "gluten"],
            "dietary_info": ["vegetarian"]
        },
        {
            "name": "Chicken Alfredo",
            "category": "Pasta",
            "price": 22.99,
            "description": "Grilled chicken, fettuccine, cream sauce",
            "allergens": ["dairy", "gluten"],
            "dietary_info": []
        },
        {
            "name": "Caesar Salad",
            "category": "Salads",
            "price": 14.99,
            "description": "Romaine lettuce, parmesan, croutons, caesar dressing",
            "allergens": ["dairy", "gluten"],
            "dietary_info": ["vegetarian"]
        },
        {
            "name": "Vegan Pasta Primavera",
            "category": "Pasta",
            "price": 19.99,
            "description": "Seasonal vegetables, olive oil, herbs",
            "allergens": ["gluten"],
            "dietary_info": ["vegan", "vegetarian"]
        },
        {
            "name": "Coca Cola",
            "category": "Beverages",
            "price": 3.99,
            "description": "Classic cola soft drink",
            "allergens": [],
            "dietary_info": []
        }
    ]
})

async def test_ordering_assistant():
    """Test the ordering assistant agent"""
    print("=" * 60)
    print("TESTING ORDERING ASSISTANT AGENT")
    print("=" * 60)
    
    test_cases = [
        {
            "name": "Simple Order",
            "request": "I want to order a large Margherita pizza",
            "context": None
        },
        {
            "name": "Order Modification",
            "request": "Actually, can you change that to a medium pizza and add a Coca Cola?",
            "context": "Customer previously ordered: Large Margherita Pizza"
        },
        {
            "name": "Menu Question",
            "request": "What pasta dishes do you have available?",
            "context": None
        },
        {
            "name": "Dietary Request",
            "request": "I'm vegetarian, what would you recommend?",
            "context": None
        }
    ]
    
    for i, test_case in enumerate(test_cases, 1):
        print(f"\n{i}. {test_case['name']}:")
        print("-" * 30)
        print(f"Request: {test_case['request']}")
        if test_case['context']:
            print(f"Context: {test_case['context']}")
        
        try:
            response = ordering_assistant_agent(
                test_case['request'],
                sample_menu_data,
                test_case['context']
            )
            print(f"Response: {response}")
        except Exception as e:
            print(f"Error: {e}")
        print()

async def test_recommendation_agent():
    """Test the recommendation agent"""
    print("=" * 60)
    print("TESTING RECOMMENDATION AGENT")
    print("=" * 60)
    
    test_cases = [
        {
            "name": "Basic Preferences",
            "preferences": "I love spicy food and seafood",
            "dietary": None,
            "budget": None,
            "occasion": None
        },
        {
            "name": "Dietary Restrictions",
            "preferences": "I enjoy Italian cuisine",
            "dietary": "vegetarian, no nuts",
            "budget": None,
            "occasion": None
        },
        {
            "name": "Budget Conscious",
            "preferences": "Something filling and satisfying",
            "dietary": None,
            "budget": "under $20",
            "occasion": None
        },
        {
            "name": "Special Occasion",
            "preferences": "Something elegant and sophisticated",
            "dietary": None,
            "budget": "$30-50",
            "occasion": "romantic dinner"
        }
    ]
    
    for i, test_case in enumerate(test_cases, 1):
        print(f"\n{i}. {test_case['name']}:")
        print("-" * 30)
        print(f"Preferences: {test_case['preferences']}")
        if test_case['dietary']:
            print(f"Dietary: {test_case['dietary']}")
        if test_case['budget']:
            print(f"Budget: {test_case['budget']}")
        if test_case['occasion']:
            print(f"Occasion: {test_case['occasion']}")
        
        try:
            response = recommendation_agent(
                test_case['preferences'],
                sample_menu_data,
                test_case['dietary'],
                test_case['budget'],
                test_case['occasion']
            )
            print(f"Response: {response}")
        except Exception as e:
            print(f"Error: {e}")
        print()

async def test_translation_agent():
    """Test the translation agent"""
    print("=" * 60)
    print("TESTING TRANSLATION AGENT")
    print("=" * 60)
    
    test_cases = [
        {
            "name": "Spanish Order",
            "message": "Hola, quiero pedir una pizza margherita grande y una coca cola",
            "source": "spanish"
        },
        {
            "name": "French Order",
            "message": "Bonjour, je voudrais commander une salade César et un verre de vin",
            "source": "french"
        },
        {
            "name": "Italian Order",
            "message": "Ciao, vorrei ordinare pasta con pollo e una birra",
            "source": "italian"
        },
        {
            "name": "Auto-detect",
            "message": "¿Qué recomiendan para una cena romántica?",
            "source": None
        }
    ]
    
    for i, test_case in enumerate(test_cases, 1):
        print(f"\n{i}. {test_case['name']}:")
        print("-" * 30)
        print(f"Message: {test_case['message']}")
        print(f"Source Language: {test_case['source'] or 'Auto-detect'}")
        
        try:
            response = translation_agent(
                test_case['message'],
                test_case['source']
            )
            print(f"Response: {response}")
        except Exception as e:
            print(f"Error: {e}")
        print()

async def test_multilingual_order():
    """Test multilingual order processing"""
    print("=" * 60)
    print("TESTING MULTILINGUAL ORDER PROCESSING")
    print("=" * 60)
    
    test_cases = [
        {
            "name": "Spanish Order with Menu",
            "message": "Quiero pedir pasta con pollo y una ensalada. ¿Cuánto cuesta?",
            "source": "spanish"
        },
        {
            "name": "French Dietary Request",
            "message": "Je suis végétarien, que me recommandez-vous?",
            "source": "french"
        },
        {
            "name": "Italian Order Modification",
            "message": "Posso cambiare la mia pizza con una media invece di grande?",
            "source": "italian"
        }
    ]
    
    for i, test_case in enumerate(test_cases, 1):
        print(f"\n{i}. {test_case['name']}:")
        print("-" * 30)
        print(f"Message: {test_case['message']}")
        print(f"Source Language: {test_case['source']}")
        
        try:
            response = process_multilingual_order(
                test_case['message'],
                sample_menu_data,
                test_case['source']
            )
            print(f"Response: {response}")
        except Exception as e:
            print(f"Error: {e}")
        print()

async def test_combo_agent():
    """Test the combined recommendation and ordering agent"""
    print("=" * 60)
    print("TESTING COMBO RECOMMENDATION & ORDERING AGENT")
    print("=" * 60)
    
    test_cases = [
        {
            "name": "English Preferences",
            "preferences": "I want something healthy and light for lunch",
            "dietary": "vegetarian",
            "language": "english"
        },
        {
            "name": "Spanish Preferences",
            "preferences": "Quiero algo picante y sabroso para la cena",
            "dietary": None,
            "language": "spanish"
        },
        {
            "name": "French Preferences",
            "preferences": "Je voudrais quelque chose d'élégant pour un dîner d'affaires",
            "dietary": None,
            "language": "french"
        }
    ]
    
    for i, test_case in enumerate(test_cases, 1):
        print(f"\n{i}. {test_case['name']}:")
        print("-" * 30)
        print(f"Preferences: {test_case['preferences']}")
        print(f"Language: {test_case['language']}")
        if test_case['dietary']:
            print(f"Dietary: {test_case['dietary']}")
        
        try:
            response = order_recommendation_combo(
                test_case['preferences'],
                sample_menu_data,
                test_case['dietary'],
                test_case['language']
            )
            print(f"Response: {response}")
        except Exception as e:
            print(f"Error: {e}")
        print()

async def test_orchestrator():
    """Test the orchestrator with various ordering scenarios"""
    print("=" * 60)
    print("TESTING ORCHESTRATOR WITH ORDERING SCENARIOS")
    print("=" * 60)
    
    test_cases = [
        "I want to order a pizza",
        "¿Qué recomiendan para una cena romántica?",
        "I'm vegetarian and need something gluten-free",
        "Can you help me modify my order?",
        "Bonjour, je voudrais commander une salade",
        "What are your most popular dishes?",
        "I have a nut allergy, what's safe for me?",
        "Vorrei ordinare pasta con pollo"
    ]
    
    for i, query in enumerate(test_cases, 1):
        print(f"\n{i}. Testing Query: {query}")
        print("-" * 50)
        
        try:
            # Test streaming response
            print("Streaming Response:")
            agent_stream = orchestrator.stream_async(query)
            async for event in agent_stream:
                if "data" in event:
                    print(event["data"], end="", flush=True)
            print("\n")
            
        except Exception as e:
            print(f"Error: {e}")
        print()

async def run_all_tests():
    """Run all ordering system tests"""
    print("🍽️  COMPREHENSIVE ORDERING SYSTEM TESTS")
    print("=" * 80)
    
    await test_ordering_assistant()
    await test_recommendation_agent()
    await test_translation_agent()
    await test_multilingual_order()
    await test_combo_agent()
    await test_orchestrator()
    
    print("=" * 80)
    print("✅ ALL ORDERING SYSTEM TESTS COMPLETED")
    print("=" * 80)

if __name__ == "__main__":
    asyncio.run(run_all_tests())