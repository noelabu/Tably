from strands import Agent, tool
from app.agents.config import bedrock_model
from app.services.menu_image_analyzer import MenuImageAnalyzer
from app.services.menu_context_service import menu_context_service
from typing import Dict, List, Optional, Any, Union
import json
import logging
from datetime import datetime
import asyncio

logger = logging.getLogger(__name__)

# System prompts for different ordering agents
ORDERING_ASSISTANT_PROMPT = """
You are a friendly and efficient ordering assistant for a restaurant. Your role is to help customers place orders smoothly and accurately.

**CRITICAL REQUIREMENT**: You MUST ONLY recommend, suggest, or mention items that are available in the restaurant's menu provided in your context. NEVER suggest items that are not explicitly listed in the menu data. If a customer asks for something not on the menu, politely inform them it's not available and suggest similar items from the actual menu.

Your responsibilities include:
1. **Order Taking**: Help customers select menu items, specify quantities, and customize orders
2. **Order Validation**: Ensure all necessary details are captured (size, modifications, special instructions)
3. **Order Summary**: Provide clear summaries of orders before confirmation
4. **Customer Service**: Answer questions about orders, modifications, and timing
5. **Upselling**: Suggest complementary items or upgrades when appropriate (ONLY from the menu)
6. **Problem Resolution**: Handle order changes, cancellations, or issues professionally

When taking orders:
- Always confirm quantities and specifications
- Ask about dietary restrictions or allergies
- Suggest popular items or chef's recommendations (ONLY from the provided menu)
- Clarify any ambiguous requests
- Provide accurate pricing from the menu
- Be patient and helpful with indecisive customers

**MENU RESTRICTIONS**:
- ONLY use items from the provided menu data
- Use exact item names as they appear in the menu
- Use exact prices as listed in the menu
- If an item is not in the menu, say "That item is not available" and suggest alternatives from the menu

Order format should include:
- Item name and quantity (exact name from menu)
- Size/portion (if applicable)
- Customizations or modifications
- Special instructions
- Dietary considerations

Always be friendly, professional, and efficient while ensuring accuracy.
"""

RECOMMENDATION_AGENT_PROMPT = """
You are a specialized recommendation agent for restaurant orders. Your expertise lies in suggesting the perfect menu items based on customer preferences, dietary needs, and dining context.

**CRITICAL REQUIREMENT**: You MUST ONLY recommend items that are available in the restaurant's menu provided in your context. NEVER suggest items that are not explicitly listed in the menu data. All recommendations must come from the actual menu with accurate names and prices.

Your capabilities include:
1. **Preference Analysis**: Understand customer tastes, dietary restrictions, and preferences
2. **Menu Knowledge**: Deep understanding of menu items, ingredients, and preparation methods (ONLY from provided menu)
3. **Pairing Suggestions**: Recommend appetizers, mains, sides, and beverages that complement each other (ONLY from menu)
4. **Dietary Accommodation**: Suggest items for vegetarian, vegan, gluten-free, keto, and other dietary needs (ONLY from menu)
5. **Occasion Matching**: Recommend appropriate items for different dining occasions (ONLY from menu)
6. **Seasonal Recommendations**: Suggest items based on availability in the menu

**MENU RESTRICTIONS**:
- ONLY recommend items from the provided menu data
- Use exact item names as they appear in the menu
- Use exact prices as listed in the menu
- If no suitable items exist in the menu for a request, explain this and suggest the closest alternatives from the menu

When making recommendations:
- Ask clarifying questions about preferences
- Consider dietary restrictions and allergies
- Suggest complete meal combinations (ONLY from available menu items)
- Explain why you're recommending specific items from the menu
- Offer alternatives at different price points (ONLY from menu)
- Highlight signature or popular dishes (ONLY from menu)
- Consider portion sizes and sharing options

Always provide personalized, thoughtful recommendations that enhance the customer's dining experience using ONLY the available menu items.
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
    order_context: Optional[str] = None,
    business_id: Optional[str] = None
) -> str:
    """
    Intelligent ordering assistant that helps customers place orders efficiently.
    
    Args:
        customer_request: Customer's order request or question
        menu_data: Optional JSON string containing menu information (deprecated - use business_id)
        order_context: Optional context about current order or customer preferences
        business_id: Optional business ID to fetch menu from database
    """
    try:
        # Build context with menu and order information
        context = ""
        
        # Prefer business_id for fetching real menu data
        if business_id:
            try:
                # Run async function in sync context
                loop = asyncio.new_event_loop()
                asyncio.set_event_loop(loop)
                menu_context = loop.run_until_complete(
                    menu_context_service.get_business_menu_context(business_id)
                )
                loop.close()
                
                context += f"\n\n{menu_context}"
                logger.info(f"Loaded menu data for business {business_id}")
            except Exception as e:
                logger.error(f"Error loading menu from database: {e}")
                context += "\nNote: Unable to load restaurant menu. Using general assistance."
        elif menu_data:
            # Fallback to provided menu_data if no business_id
            try:
                parsed_menu = json.loads(menu_data) if isinstance(menu_data, str) else menu_data
                context += f"""

AVAILABLE MENU:
{json.dumps(parsed_menu, indent=2)}

Use this menu information to help customers place accurate orders and make suggestions.
"""
            except json.JSONDecodeError:
                context += "\nNote: Menu data provided but could not be parsed."
        else:
            context += "\nNote: No specific restaurant menu available. Using general ordering assistance."
        
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
    occasion: Optional[str] = None,
    business_id: Optional[str] = None
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
        
        # Prefer business_id for fetching real menu data
        if business_id:
            try:
                # Run async function in sync context
                loop = asyncio.new_event_loop()
                asyncio.set_event_loop(loop)
                menu_context = loop.run_until_complete(
                    menu_context_service.get_business_menu_context(business_id)
                )
                loop.close()
                
                context += f"\n\n{menu_context}"
                logger.info(f"Loaded menu data for business {business_id}")
            except Exception as e:
                logger.error(f"Error loading menu from database: {e}")
                context += "\nNote: Unable to load restaurant menu. Using general recommendations."
        elif menu_data:
            try:
                parsed_menu = json.loads(menu_data) if isinstance(menu_data, str) else menu_data
                context += f"""

AVAILABLE MENU:
{json.dumps(parsed_menu, indent=2)}

Use this menu to make specific recommendations with accurate prices and descriptions.
"""
            except json.JSONDecodeError:
                context += "\nNote: Menu data provided but could not be parsed."
        
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
    source_language: Optional[str] = None,
    business_id: Optional[str] = None
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
        order_result = ordering_assistant_agent(
            english_order, 
            menu_data=menu_data,
            business_id=business_id
        )
        
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
    language: Optional[str] = None,
    business_id: Optional[str] = None
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
            menu_data=menu_data,
            business_id=business_id
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