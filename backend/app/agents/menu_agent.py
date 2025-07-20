from strands import Agent, tool
from app.agents.config import bedrock_model
from app.services.menu_image_analyzer import MenuImageAnalyzer
from typing import Dict, List, Optional, Any, Union
import json
import base64
import io

MENU_INTELLIGENT_PROMPT = """
You are a specialized menu intelligence assistant for restaurants. Your role is to help customers understand, analyze, and interact with restaurant menus effectively.

Your key capabilities include:
1. **Menu Analysis**: Analyze menu images to extract structured data including items, prices, descriptions, and allergen information
2. **Item Recommendations**: Suggest menu items based on dietary preferences, restrictions, and customer preferences
3. **Dietary Assistance**: Help customers with specific dietary needs (vegetarian, vegan, gluten-free, allergies, etc.)
4. **Menu Navigation**: Guide customers through menu categories and help them find specific items
5. **Price Information**: Provide accurate pricing information for menu items
6. **Ingredient Analysis**: Identify ingredients and potential allergens in menu items
7. **Nutritional Guidance**: Offer insights about nutritional aspects of menu items when possible

When responding to queries:
- Be accurate and thorough in your analysis
- Always prioritize customer safety regarding allergens and dietary restrictions
- Provide clear, structured information about menu items
- Include relevant details like prices, ingredients, and preparation methods
- Offer helpful alternatives when items don't meet customer requirements
- Be friendly and professional in your communication

Remember to always double-check allergen information and recommend customers confirm with restaurant staff for critical dietary restrictions.
"""

@tool
def menu_intelligent_agent(query: str, menu_data: Optional[str] = None) -> str:
    """
    Intelligent menu agent that provides comprehensive menu analysis and recommendations.
    
    Args:
        query: User query about menu items, recommendations, or analysis
        menu_data: Optional JSON string containing menu analysis data
    """
    try:
        # Build context with menu data if provided
        context = ""
        if menu_data:
            try:
                parsed_data = json.loads(menu_data) if isinstance(menu_data, str) else menu_data
                context = f"""

AVAILABLE MENU DATA:
{json.dumps(parsed_data, indent=2)}

Use this menu information to provide accurate answers about available items, prices, ingredients, and recommendations.
"""
            except json.JSONDecodeError:
                context = f"\nNote: Menu data provided but could not be parsed: {menu_data}"
        
        # Create the menu intelligence agent
        menu_agent = Agent(
            model=bedrock_model,
            system_prompt=MENU_INTELLIGENT_PROMPT + context,
            tools=[]
        )
        
        # Process the query
        response = menu_agent(query)
        return str(response)
        
    except Exception as e:
        return f"Error in menu intelligence agent: {str(e)}"

@tool
def analyze_menu_image(image_data: Union[bytes, str]) -> str:
    """
    Analyze a menu image and extract structured menu data.
    
    Args:
        image_data: Image bytes or base64 encoded image string
    """
    try:
        # Handle different input formats
        if isinstance(image_data, str):
            # Assume base64 encoded
            try:
                image_bytes = base64.b64decode(image_data)
            except Exception:
                return "Error: Invalid base64 image data provided"
        else:
            image_bytes = image_data
        
        # Initialize menu analyzer
        menu_analyzer = MenuImageAnalyzer()
        
        # Analyze the menu image
        analysis_result = menu_analyzer.analyze_menu_image(image_bytes)
        
        # Format the result for better readability
        formatted_result = {
            "analysis_status": "success",
            "restaurant_info": analysis_result.get("restaurant_info", {}),
            "menu_categories": analysis_result.get("menu_categories", []),
            "total_items": len(analysis_result.get("menu_items", [])),
            "menu_items": analysis_result.get("menu_items", []),
            "extracted_at": analysis_result.get("extracted_at", ""),
            "confidence_score": analysis_result.get("confidence_score", 0.0)
        }
        
        return json.dumps(formatted_result, indent=2)
        
    except Exception as e:
        error_result = {
            "analysis_status": "error",
            "error_message": str(e),
            "menu_items": []
        }
        return json.dumps(error_result, indent=2)

@tool
def get_menu_recommendations(dietary_preferences: str, menu_data: Optional[str] = None) -> str:
    """
    Get menu recommendations based on dietary preferences and restrictions.
    
    Args:
        dietary_preferences: User's dietary preferences and restrictions
        menu_data: Optional JSON string containing menu analysis data
    """
    try:
        query = f"""
        Based on the following dietary preferences and restrictions, recommend suitable menu items:
        
        Dietary Preferences: {dietary_preferences}
        
        Please provide:
        1. Recommended items that match the dietary requirements
        2. Items to avoid and why
        3. Alternatives or modifications that could work
        4. Any important allergen warnings
        """
        
        return menu_intelligent_agent(query, menu_data)
        
    except Exception as e:
        return f"Error getting menu recommendations: {str(e)}"

@tool
def search_menu_items(search_term: str, menu_data: Optional[str] = None) -> str:
    """
    Search for specific menu items or ingredients.
    
    Args:
        search_term: Term to search for in menu items
        menu_data: Optional JSON string containing menu analysis data
    """
    try:
        query = f"""
        Search the menu for items containing or related to: {search_term}
        
        Please provide:
        1. Exact matches found
        2. Similar or related items
        3. Price information for found items
        4. Any relevant dietary or allergen information
        """
        
        return menu_intelligent_agent(query, menu_data)
        
    except Exception as e:
        return f"Error searching menu items: {str(e)}"

@tool
def get_allergen_information(allergen: str, menu_data: Optional[str] = None) -> str:
    """
    Get detailed allergen information for menu items.
    
    Args:
        allergen: Specific allergen to check for
        menu_data: Optional JSON string containing menu analysis data
    """
    try:
        query = f"""
        Provide detailed information about the allergen "{allergen}" in the menu:
        
        Please include:
        1. Items that contain this allergen
        2. Items that are safe (don't contain the allergen)
        3. Items with uncertain allergen status
        4. Cross-contamination risks
        5. Recommendations for safe ordering
        """
        
        return menu_intelligent_agent(query, menu_data)
        
    except Exception as e:
        return f"Error getting allergen information: {str(e)}"

# Create a standalone menu agent instance
menu_agent = Agent(
    system_prompt=MENU_INTELLIGENT_PROMPT,
    model=bedrock_model,
    tools=[
        menu_intelligent_agent,
        analyze_menu_image,
        get_menu_recommendations,
        search_menu_items,
        get_allergen_information
    ],
    callback_handler=None
)