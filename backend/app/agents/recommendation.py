from strands import Agent, tool
from app.agents.config import bedrock_model
from app.services.menu_image_analyzer import MenuImageAnalyzer
from typing import Dict, List, Optional, Any
import json

# Define specialized system prompts
ORDER_RECOMMENDATION_PROMPT = """
You are a specialized product recommendation assistant.
Provide personalized product suggestions based on user preferences.
Justify your recommendations clearly.
"""

ORDER_TRANSLATION_PROMPT = """
You are a specialized order translation assistant.
When a user asks in a language other than English, translate their request into English.
Respond on the same language as the user as well as the english translation.
Always ensure the translation is accurate and contextually appropriate.
If the user asks for a translation, provide it in the same language as the original request.
"""

ORDER_DIETARY_PROMPT = """
You are a specialized dietary assistant.
When a user asks about dietary preferences or restrictions, provide tailored advice.
Consider common dietary needs such as vegetarian, vegan, gluten-free, etc.
Also consider cultural dietary practices and allergies.
Always ensure the advice is practical and easy to follow.
"""

MENU_INTELLIGENT_PROMPT = """
You are a specialized menu intelligence assistant that helps users understand, analyze, and interact with restaurant menus.
Your capabilities include:
- Analyzing menu images to extract structured data
- Providing detailed menu item information including prices, descriptions, and allergens
- Recommending items based on dietary preferences and restrictions
- Answering questions about menu availability, pricing, and ingredients
- Helping with menu navigation and organization
- Providing insights about menu categories and popular items

When analyzing menus, always provide:
1. Clear, structured information about menu items
2. Accurate pricing information
3. Detailed ingredient lists when available
4. Allergen warnings and dietary considerations
5. Helpful recommendations based on user preferences

Be thorough, accurate, and helpful in your responses about menu-related queries.
"""

@tool
def order_translation_agent(query: str) -> str:
    """
    Process and respond to research-related queries.
    """
    try:
        research_agent = Agent(
            model=bedrock_model,
            system_prompt=ORDER_TRANSLATION_PROMPT,
            tools=[]
        )
        response = research_agent(query)
        return str(response)
    except Exception as e:
        return f"Error in research assistant: {str(e)}"

@tool
def order_recommendation_agent(query: str) -> str:
    """
    Handle product recommendation queries by suggesting appropriate products.
    """
    try:
        product_agent = Agent(
            model=bedrock_model,
            system_prompt=ORDER_RECOMMENDATION_PROMPT,
            tools=[]
        )
        response = product_agent(query)
        return str(response)
    except Exception as e:
        return f"Error in product recommendation: {str(e)}"

@tool
def order_dietary_agent(query: str) -> str:
    """
    Create travel itineraries and provide travel advice.
    """
    try:
        travel_agent = Agent(
            model=bedrock_model,
            system_prompt=ORDER_DIETARY_PROMPT,
            tools=[]
        )
        response = travel_agent(query)
        return str(response)
    except Exception as e:
        return f"Error in trip planning: {str(e)}"

@tool
def menu_intelligent_agent(query: str, menu_image_bytes: Optional[bytes] = None) -> str:
    """
    Intelligent menu agent that can analyze menu images and provide detailed menu information.
    Handles menu analysis, item recommendations, dietary considerations, and menu navigation.
    
    Args:
        query: User query about menu items, recommendations, or analysis
        menu_image_bytes: Optional image bytes of menu to analyze
    """
    try:
        # Initialize menu analyzer
        menu_analyzer = MenuImageAnalyzer()
        
        # If menu image is provided, analyze it first
        menu_context = ""
        if menu_image_bytes:
            try:
                menu_analysis = menu_analyzer.analyze_menu_image(menu_image_bytes)
                menu_context = f"""
                
MENU ANALYSIS RESULTS:
{json.dumps(menu_analysis, indent=2)}

Use this menu data to answer questions about available items, prices, allergens, and make recommendations.
"""
            except Exception as e:
                menu_context = f"\nNote: Could not analyze menu image: {str(e)}"
        
        # Create the menu intelligence agent
        menu_agent = Agent(
            model=bedrock_model,
            system_prompt=MENU_INTELLIGENT_PROMPT + menu_context,
            tools=[]
        )
        
        # Process the query
        response = menu_agent(query)
        return str(response)
        
    except Exception as e:
        return f"Error in menu intelligence agent: {str(e)}"

@tool
def analyze_menu_image(image_bytes: bytes) -> str:
    """
    Analyze a menu image and extract structured menu data.
    
    Args:
        image_bytes: Bytes of the menu image to analyze
    """
    try:
        menu_analyzer = MenuImageAnalyzer()
        analysis_result = menu_analyzer.analyze_menu_image(image_bytes)
        
        # Format the result for better readability
        formatted_result = {
            "restaurant_info": analysis_result.get("restaurant_info", {}),
            "menu_categories": analysis_result.get("menu_categories", []),
            "total_items": len(analysis_result.get("menu_items", [])),
            "menu_items": analysis_result.get("menu_items", [])
        }
        
        return json.dumps(formatted_result, indent=2)
        
    except Exception as e:
        return f"Error analyzing menu image: {str(e)}"