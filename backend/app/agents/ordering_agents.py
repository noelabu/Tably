from strands import Agent, tool
from app.agents.config import bedrock_model
from app.services.menu_image_analyzer import MenuImageAnalyzer
from typing import Dict, List, Optional, Any, Union
import json
import logging
from datetime import datetime

logger = logging.getLogger(__name__)

# System prompts for different ordering agents
ORDERING_ASSISTANT_PROMPT = """
You are a friendly and efficient ordering assistant for a restaurant. Your role is to help customers place orders smoothly and accurately.

Your responsibilities include:
1. **Order Taking**: Help customers select menu items, specify quantities, and customize orders
2. **Order Validation**: Ensure all necessary details are captured (size, modifications, special instructions)
3. **Order Summary**: Provide clear summaries of orders before confirmation
4. **Customer Service**: Answer questions about orders, modifications, and timing
5. **Upselling**: Suggest complementary items or upgrades when appropriate
6. **Problem Resolution**: Handle order changes, cancellations, or issues professionally

When taking orders:
- Always confirm quantities and specifications
- Ask about dietary restrictions or allergies
- Suggest popular items or chef's recommendations
- Clarify any ambiguous requests
- Provide estimated timing and total cost when available
- Be patient and helpful with indecisive customers

Order format should include:
- Item name and quantity
- Size/portion (if applicable)
- Customizations or modifications
- Special instructions
- Dietary considerations

Always be friendly, professional, and efficient while ensuring accuracy.
"""

RECOMMENDATION_AGENT_PROMPT = """
You are a specialized recommendation agent for restaurant orders. Your expertise lies in suggesting the perfect menu items based on customer preferences, dietary needs, and dining context.

Your capabilities include:
1. **Preference Analysis**: Understand customer tastes, dietary restrictions, and preferences
2. **Menu Knowledge**: Deep understanding of menu items, ingredients, and preparation methods
3. **Pairing Suggestions**: Recommend appetizers, mains, sides, and beverages that complement each other
4. **Dietary Accommodation**: Suggest items for vegetarian, vegan, gluten-free, keto, and other dietary needs
5. **Occasion Matching**: Recommend appropriate items for different dining occasions (casual, business, celebration)
6. **Seasonal Recommendations**: Suggest items based on seasonal availability and popularity

When making recommendations:
- Ask clarifying questions about preferences
- Consider dietary restrictions and allergies
- Suggest complete meal combinations
- Explain why you're recommending specific items
- Offer alternatives at different price points
- Highlight signature or popular dishes
- Consider portion sizes and sharing options

Always provide personalized, thoughtful recommendations that enhance the customer's dining experience.
"""

TRANSLATION_AGENT_PROMPT = """
You are a specialized translation agent for restaurant orders. You help customers who speak different languages place orders accurately by translating their requests and communicating with the kitchen staff.

Your responsibilities include:
1. **Order Translation**: Translate customer orders from their native language to English
2. **Menu Translation**: Explain menu items in the customer's preferred language
3. **Cultural Context**: Understand cultural dining preferences and customs
4. **Dietary Translation**: Accurately translate dietary restrictions and allergies
5. **Confirmation**: Ensure translations are accurate by confirming with customers
6. **Special Instructions**: Translate cooking preferences and special requests

Supported languages (expand as needed):
- Spanish (Español)
- French (Français)
- Italian (Italiano)
- German (Deutsch)
- Portuguese (Português)
- Chinese (中文)
- Japanese (日本語)
- Korean (한국어)
- Arabic (العربية)
- Hindi (हिंदी)
- Filipino/Tagalog

When translating:
- Always confirm the translation with the customer
- Provide both original and translated versions
- Ask for clarification if anything is unclear
- Be sensitive to cultural dining preferences
- Ensure accuracy, especially for allergies and dietary restrictions
- Offer menu explanations in the customer's language

Format translations clearly with:
- Original text
- English translation
- Confirmation question
- Any cultural notes if relevant
"""

@tool
def ordering_assistant_agent(
    customer_request: str, 
    menu_data: Optional[str] = None,
    order_context: Optional[str] = None
) -> str:
    """
    Intelligent ordering assistant that helps customers place orders efficiently.
    
    Args:
        customer_request: Customer's order request or question
        menu_data: Optional JSON string containing menu information
        order_context: Optional context about current order or customer preferences
    """
    try:
        # Build context with menu and order information
        context = ""
        if menu_data:
            try:
                parsed_menu = json.loads(menu_data) if isinstance(menu_data, str) else menu_data
                context += f"""

AVAILABLE MENU:
{json.dumps(parsed_menu, indent=2)}

Use this menu information to help customers place accurate orders and make suggestions.
"""
            except json.JSONDecodeError:
                context += f"\nNote: Menu data provided but could not be parsed."
        
        if order_context:
            context += f"""

CURRENT ORDER CONTEXT:
{order_context}

Use this context to help with order modifications, additions, or clarifications.
"""
        
        # Create the ordering assistant agent
        ordering_agent = Agent(
            model=bedrock_model,
            system_prompt=ORDERING_ASSISTANT_PROMPT + context,
            tools=[]
        )
        
        logger.info(f"Processing ordering request: {customer_request}")
        
        # Process the customer request
        response = ordering_agent(customer_request)
        return str(response)
        
    except Exception as e:
        logger.error(f"Error in ordering assistant: {e}")
        return f"I apologize, but I'm having trouble processing your order right now. Please try again or speak with a staff member. Error: {str(e)}"

@tool
def recommendation_agent(
    customer_preferences: str,
    menu_data: Optional[str] = None,
    dietary_restrictions: Optional[str] = None,
    budget_range: Optional[str] = None,
    occasion: Optional[str] = None
) -> str:
    """
    Specialized recommendation agent for personalized menu suggestions.
    
    Args:
        customer_preferences: Customer's taste preferences, favorite cuisines, or general likes/dislikes
        menu_data: Optional JSON string containing menu information
        dietary_restrictions: Optional dietary restrictions or allergies
        budget_range: Optional budget considerations
        occasion: Optional dining occasion context
    """
    try:
        # Build comprehensive context
        context = ""
        
        if menu_data:
            try:
                parsed_menu = json.loads(menu_data) if isinstance(menu_data, str) else menu_data
                context += f"""

AVAILABLE MENU:
{json.dumps(parsed_menu, indent=2)}

Use this menu to make specific recommendations with accurate prices and descriptions.
"""
            except json.JSONDecodeError:
                context += f"\nNote: Menu data provided but could not be parsed."
        
        # Add customer context
        recommendation_context = f"""

CUSTOMER PREFERENCES: {customer_preferences}
"""
        
        if dietary_restrictions:
            recommendation_context += f"DIETARY RESTRICTIONS: {dietary_restrictions}\n"
        
        if budget_range:
            recommendation_context += f"BUDGET CONSIDERATIONS: {budget_range}\n"
        
        if occasion:
            recommendation_context += f"DINING OCCASION: {occasion}\n"
        
        context += recommendation_context
        
        # Create the recommendation agent
        recommendation_agent_instance = Agent(
            model=bedrock_model,
            system_prompt=RECOMMENDATION_AGENT_PROMPT + context,
            tools=[]
        )
        
        logger.info(f"Processing recommendation request for preferences: {customer_preferences}")
        
        # Generate recommendations
        query = f"Based on the customer preferences and context provided, please recommend suitable menu items and explain your recommendations."
        response = recommendation_agent_instance(query)
        return str(response)
        
    except Exception as e:
        logger.error(f"Error in recommendation agent: {e}")
        return f"I apologize, but I'm having trouble generating recommendations right now. Please try again or ask our staff for suggestions. Error: {str(e)}"

@tool
def translation_agent(
    customer_message: str,
    source_language: Optional[str] = None,
    target_language: str = "english"
) -> str:
    """
    Translation agent for multilingual order processing.
    
    Args:
        customer_message: Customer's message in their native language
        source_language: Optional source language (will be detected if not provided)
        target_language: Target language for translation (default: English)
    """
    try:
        # Build translation context
        context = f"""

TRANSLATION REQUEST:
- Customer Message: {customer_message}
- Source Language: {source_language if source_language else 'Auto-detect'}
- Target Language: {target_language}

Please provide:
1. Detected source language (if not specified)
2. Accurate translation
3. Order-relevant information extracted
4. Any cultural context or dining preferences
5. Confirmation question for the customer

Be especially careful with:
- Food names and ingredients
- Dietary restrictions and allergies
- Cooking preferences (spicy, mild, etc.)
- Quantities and specifications
"""
        
        # Create the translation agent
        translation_agent_instance = Agent(
            model=bedrock_model,
            system_prompt=TRANSLATION_AGENT_PROMPT + context,
            tools=[]
        )
        
        logger.info(f"Processing translation request from {source_language} to {target_language}")
        
        # Process the translation
        response = translation_agent_instance("Please translate and process this customer message for order taking.")
        return str(response)
        
    except Exception as e:
        logger.error(f"Error in translation agent: {e}")
        return f"I apologize, but I'm having trouble with the translation right now. Please try speaking in English or ask for assistance from our multilingual staff. Error: {str(e)}"

@tool
def process_multilingual_order(
    customer_message: str,
    menu_data: Optional[str] = None,
    source_language: Optional[str] = None
) -> str:
    """
    Complete multilingual order processing that combines translation and ordering assistance.
    
    Args:
        customer_message: Customer's order in their native language
        menu_data: Optional JSON string containing menu information
        source_language: Optional source language hint
    """
    try:
        logger.info(f"Processing multilingual order: {customer_message}")
        
        # First, translate the message
        translation_result = translation_agent(customer_message, source_language, "english")
        
        # Extract the English translation from the result
        # This is a simplified extraction - in practice, you might want more sophisticated parsing
        english_order = translation_result
        
        # Now process the translated order
        order_result = ordering_assistant_agent(english_order, menu_data)
        
        # Combine translation and ordering results
        combined_response = f"""
TRANSLATION:
{translation_result}

ORDER ASSISTANCE:
{order_result}

I've translated your message and processed your order request. Please confirm this is correct.
"""
        
        return combined_response
        
    except Exception as e:
        logger.error(f"Error in multilingual order processing: {e}")
        return f"I apologize, but I'm having trouble processing your multilingual order. Please try again or ask for assistance from our staff. Error: {str(e)}"

@tool
def order_recommendation_combo(
    customer_preferences: str,
    menu_data: Optional[str] = None,
    dietary_restrictions: Optional[str] = None,
    language: Optional[str] = None
) -> str:
    """
    Combined recommendation and ordering assistance with optional translation.
    
    Args:
        customer_preferences: Customer preferences in any language
        menu_data: Optional JSON string containing menu information
        dietary_restrictions: Optional dietary restrictions
        language: Optional language specification
    """
    try:
        logger.info(f"Processing combo recommendation and order in {language or 'default'} language")
        
        # If language is specified and not English, translate first
        if language and language.lower() not in ['english', 'en']:
            translation_result = translation_agent(customer_preferences, language, "english")
            # Extract English version for processing
            english_preferences = translation_result
        else:
            english_preferences = customer_preferences
            translation_result = None
        
        # Get recommendations
        recommendations = recommendation_agent(
            english_preferences, 
            menu_data, 
            dietary_restrictions
        )
        
        # Process as order assistance
        order_help = ordering_assistant_agent(
            f"Based on these recommendations: {recommendations}. Help me place an order.",
            menu_data
        )
        
        # Combine results
        if translation_result:
            combined_response = f"""
TRANSLATION:
{translation_result}

RECOMMENDATIONS:
{recommendations}

ORDER ASSISTANCE:
{order_help}
"""
        else:
            combined_response = f"""
RECOMMENDATIONS:
{recommendations}

ORDER ASSISTANCE:
{order_help}
"""
        
        return combined_response
        
    except Exception as e:
        logger.error(f"Error in combo recommendation/order processing: {e}")
        return f"I apologize, but I'm having trouble with your request. Please try again or speak with our staff. Error: {str(e)}"

# Create standalone agent instances for direct use
ordering_assistant = Agent(
    system_prompt=ORDERING_ASSISTANT_PROMPT,
    model=bedrock_model,
    tools=[],
    callback_handler=None
)

recommendation_assistant = Agent(
    system_prompt=RECOMMENDATION_AGENT_PROMPT,
    model=bedrock_model,
    tools=[],
    callback_handler=None
)

translation_assistant = Agent(
    system_prompt=TRANSLATION_AGENT_PROMPT,
    model=bedrock_model,
    tools=[],
    callback_handler=None
)