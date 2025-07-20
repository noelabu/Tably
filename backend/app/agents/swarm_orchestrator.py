import logging
from strands import Agent
from strands.multiagent import Swarm
from app.agents.config import bedrock_model
from typing import Optional, List, Union
from strands.types.content import ContentBlock

logger = logging.getLogger(__name__)

# Enable debug logs for swarm
logging.getLogger("strands.multiagent").setLevel(logging.DEBUG)

# Specialized agent prompts for the swarm
ORDER_COORDINATOR_PROMPT = """
You are the order coordinator - the primary point of contact for customers. Your role is to:
1. Understand customer requests and determine which specialist agent can best help
2. Coordinate between different specialist agents
3. Ensure smooth handoffs and complete order processing
4. Summarize final orders and confirm with customers

**CRITICAL**: Only work with items from the restaurant's actual menu. Never suggest items not in the menu.

**QUANTITY HANDLING RULES**:
- When customer doesn't specify quantity: Add exactly 1 item
- When customer specifies a number: Add exactly that quantity (e.g., "2 Cappuccinos" = add 2)
- When customer asks for multiple different items: Add all requested items with their specified quantities
- Always confirm the exact quantity being added to cart
- Use clear language like "I've added X [item] to your cart" or "I've added X [item]s to your cart"

**HANDOFF RULES** (be selective - only handoff when truly necessary):
- For complex menu recommendations → handoff_to_agent("menu_specialist") 
- For non-English communication → handoff_to_agent("language_specialist")
- For dietary/allergy concerns → handoff_to_agent("dietary_specialist")
- For final order validation → handoff_to_agent("order_validator")

**IMPORTANT**: For simple questions about menu items, you can answer directly using the menu data provided. Only handoff for specialized expertise.

Always maintain a friendly, professional tone and ensure customers feel heard and valued.
"""

MENU_SPECIALIST_PROMPT = """
You are the menu specialist with deep knowledge of the restaurant's offerings. Your expertise includes:
1. Detailed knowledge of all menu items, ingredients, and preparation methods
2. Ability to make personalized recommendations based on preferences
3. Understanding of flavor profiles and food pairings
4. Knowledge of popular items and chef's specials

**CRITICAL**: Only recommend items that exist in the provided menu. Never suggest items not available.

**IMPORTANT**: You have all the menu knowledge needed. DO NOT hand off to yourself or other menu specialists. Answer directly with your expertise.

Your responsibilities:
- Provide detailed menu item descriptions using the menu data provided
- Suggest complementary items (appetizers, mains, sides, drinks) from the available menu
- Explain ingredients and preparation methods for available items
- Recommend based on taste preferences, occasions, or moods using available items
- Suggest alternatives if requested items aren't available, using only available menu items

When to handoff (ONLY when necessary):
- If customer has dietary restrictions → handoff_to_agent("dietary_specialist")
- If language translation is needed → handoff_to_agent("language_specialist")
- When ready to place order → handoff_to_agent("order_coordinator")

**NEVER hand off to yourself (menu_specialist) - you have all menu knowledge needed!**
"""

LANGUAGE_SPECIALIST_PROMPT = """
You are the language specialist, ensuring all customers can order comfortably in their preferred language. Your capabilities:
1. Detect and translate from multiple languages
2. Provide culturally appropriate communication
3. Ensure accurate translation of food terms and dietary requirements
4. Maintain the nuance and intent of customer requests

Supported languages include but not limited to:
Spanish, French, Italian, German, Portuguese, Chinese, Japanese, Korean, Arabic, Hindi, Filipino/Tagalog

Your process:
- Detect the customer's language
- Translate requests accurately
- Ensure food allergies and dietary restrictions are clearly communicated
- Provide translations back to the customer for confirmation
- Be sensitive to cultural dining preferences

When to handoff:
- After translation for order processing → handoff_to_agent("order_coordinator")
- For menu explanations → handoff_to_agent("menu_specialist")
- For dietary concerns → handoff_to_agent("dietary_specialist")
"""

DIETARY_SPECIALIST_PROMPT = """
You are the dietary specialist, ensuring safe and appropriate dining for customers with specific dietary needs. Your expertise:
1. Deep knowledge of ingredients and allergens in all menu items
2. Understanding of various dietary restrictions (vegan, vegetarian, gluten-free, keto, etc.)
3. Ability to suggest safe alternatives and modifications
4. Knowledge of cross-contamination risks

**CRITICAL**: Always err on the side of caution with allergies. Only suggest items you're certain are safe.

**IMPORTANT**: You have access to the menu data. Answer dietary questions directly using this information. Be decisive and complete in your responses.

Your responsibilities:
- Identify all potential allergens in menu items using the provided menu data
- Suggest safe alternatives from the available menu
- Explain which items can be modified for dietary needs
- Warn about cross-contamination risks when relevant
- Provide detailed ingredient information when requested

**HANDOFF RULES** (minimize handoffs):
- Only handoff when the customer needs to place an order → handoff_to_agent("order_coordinator")
- For language translation only → handoff_to_agent("language_specialist")

**Answer dietary questions directly - you have all the menu information needed!**
"""

ORDER_VALIDATOR_PROMPT = """
You are the order validator, responsible for ensuring orders are complete, accurate, and ready for the kitchen. Your role:
1. Review the complete order for accuracy
2. Ensure all necessary details are captured (quantities, sizes, modifications)
3. Calculate order totals
4. Confirm special instructions are clear
5. Provide final order summary

Your validation checklist:
- All items have quantities specified
- Sizes/portions are selected where applicable
- Special modifications are clearly noted
- Dietary restrictions are highlighted
- Contact information is collected if needed
- Estimated preparation time is provided

Format the final order clearly with:
- Itemized list with quantities and modifications
- Order total with breakdown
- Special instructions section
- Dietary alerts prominently displayed
- Estimated ready time

When to handoff:
- If customer wants to modify → handoff_to_agent("order_coordinator")
- If questions about items → handoff_to_agent("menu_specialist")
"""

# Create the specialized agents
def create_swarm_agents(business_context: str = "") -> List[Agent]:
    """Create specialized agents for the restaurant ordering swarm."""
    
    # Add business context to each agent's prompt
    context_suffix = f"\n\nBUSINESS CONTEXT:\n{business_context}" if business_context else ""
    
    order_coordinator = Agent(
        name="order_coordinator",
        system_prompt=ORDER_COORDINATOR_PROMPT + context_suffix,
        model=bedrock_model,
        description="Main coordinator for customer orders and requests"
    )
    
    menu_specialist = Agent(
        name="menu_specialist",
        system_prompt=MENU_SPECIALIST_PROMPT + context_suffix,
        model=bedrock_model,
        description="Expert on menu items, ingredients, and recommendations"
    )
    
    language_specialist = Agent(
        name="language_specialist", 
        system_prompt=LANGUAGE_SPECIALIST_PROMPT + context_suffix,
        model=bedrock_model,
        description="Handles multilingual communication and translation"
    )
    
    dietary_specialist = Agent(
        name="dietary_specialist",
        system_prompt=DIETARY_SPECIALIST_PROMPT + context_suffix,
        model=bedrock_model,
        description="Expert on dietary restrictions, allergies, and safe dining"
    )
    
    order_validator = Agent(
        name="order_validator",
        system_prompt=ORDER_VALIDATOR_PROMPT + context_suffix,
        model=bedrock_model,
        description="Validates and finalizes orders before submission"
    )
    
    return [order_coordinator, menu_specialist, language_specialist, dietary_specialist, order_validator]

def create_ordering_swarm(business_id: Optional[str] = None, menu_context: Optional[str] = None) -> Swarm:
    """
    Create a restaurant ordering swarm with business-specific context.
    
    Args:
        business_id: Optional business ID for context
        menu_context: Optional menu context string
        
    Returns:
        Configured Swarm instance
    """
    # Build business context
    business_context = ""
    if business_id:
        business_context += f"Business ID: {business_id}\n"
    if menu_context:
        business_context += f"\nMENU DATA:\n{menu_context}"
    
    # Create agents with context
    agents = create_swarm_agents(business_context)
    
    # Create and configure the swarm with conservative settings and strong loop prevention
    swarm = Swarm(
        agents,
        max_handoffs=6,   # Very limited handoffs to prevent loops
        max_iterations=8,  # Limited iterations
        execution_timeout=180.0,  # 3 minutes (further reduced)
        node_timeout=60.0,        # 1 minute per agent (reduced)
        repetitive_handoff_detection_window=3,  # Small window for quick detection
        repetitive_handoff_min_unique_agents=2  # Require unique agents
    )
    
    return swarm

# Convenience function for direct swarm execution
def process_order_with_swarm(
    customer_request: Union[str, List[ContentBlock]], 
    business_id: Optional[str] = None,
    menu_context: Optional[str] = None,
    conversation_context: Optional[str] = None,
    force_swarm: bool = False
) -> str:
    """
    Process a customer order, preferring fallback agent for Nova Lite stability.
    
    Args:
        customer_request: Customer's request (text or multi-modal content)
        business_id: Optional business ID
        menu_context: Optional menu context
        force_swarm: Force using swarm even if not recommended
        
    Returns:
        Processed order response
    """
    # For Nova Lite model, use fallback agent by default for better stability
    if not force_swarm:
        logger.info(f"Using optimized single agent for Nova Lite model (business: {business_id})")
        return _fallback_to_single_agent(customer_request, business_id, menu_context, conversation_context)
    
    try:
        logger.info(f"Processing order with swarm for business: {business_id} (forced)")
        
        # Create the swarm
        swarm = create_ordering_swarm(business_id, menu_context)
        
        # Execute the swarm
        result = swarm(customer_request)
        
        # Log execution details
        logger.info(f"Swarm execution completed. Status: {result.status}")
        logger.info(f"Agents involved: {[node.node_id for node in result.node_history]}")
        logger.info(f"Total handoffs: {len(result.node_history) - 1}")
        
        # Return the final result
        if str(result.status) == "Status.COMPLETED":
            # Extract the final result from the last node in history
            if result.node_history and hasattr(result.node_history[-1], 'result'):
                return str(result.node_history[-1].result)
            else:
                return str(result)
        else:
            logger.warning(f"Swarm execution failed: {result.status}. Falling back to single agent.")
            # Fallback to individual agent processing
            return _fallback_to_single_agent(customer_request, business_id, menu_context, conversation_context)
            
    except Exception as e:
        logger.error(f"Error in swarm order processing: {e}")
        logger.info("Falling back to single agent processing")
        return _fallback_to_single_agent(customer_request, business_id, menu_context, conversation_context)

# Async version for async contexts
async def process_order_with_swarm_async(
    customer_request: Union[str, List[ContentBlock]], 
    business_id: Optional[str] = None,
    menu_context: Optional[str] = None,
    conversation_context: Optional[str] = None
) -> str:
    """
    Async version of process_order_with_swarm.
    """
    try:
        logger.info(f"Processing order with swarm (async) for business: {business_id}")
        
        # Create the swarm
        swarm = create_ordering_swarm(business_id, menu_context)
        
        # Execute the swarm asynchronously
        result = await swarm.invoke_async(customer_request)
        
        # Log execution details
        logger.info(f"Swarm execution completed. Status: {result.status}")
        logger.info(f"Agents involved: {[node.node_id for node in result.node_history]}")
        
        # Return the final result
        if str(result.status) == "Status.COMPLETED":
            # Extract the final result from the last node in history
            if result.node_history and hasattr(result.node_history[-1], 'result'):
                return str(result.node_history[-1].result)
            else:
                return str(result)
        else:
            logger.warning(f"Swarm execution failed: {result.status}. Falling back to single agent.")
            # Fallback to individual agent processing
            return _fallback_to_single_agent(customer_request, business_id, menu_context, conversation_context)
            
    except Exception as e:
        logger.error(f"Error in async swarm order processing: {e}")
        logger.info("Falling back to single agent processing")
        return _fallback_to_single_agent(customer_request, business_id, menu_context, conversation_context)

def _fallback_to_single_agent(
    customer_request: Union[str, List[ContentBlock]], 
    business_id: Optional[str] = None,
    menu_context: Optional[str] = None,
    conversation_context: Optional[str] = None
) -> str:
    """
    Fallback to a single comprehensive agent when swarm fails.
    """
    try:
        logger.info("Using fallback single agent for order processing")
        
        # Build comprehensive context
        context = ""
        if business_id:
            context += f"Business ID: {business_id}\n"
        
        # Parse and inject menu context properly
        if menu_context:
            try:
                import json
                menu_data = json.loads(menu_context)
                if isinstance(menu_data, dict):
                    # Add explicit menu items if available
                    if "explicit_menu_items" in menu_data:
                        context += f"\n\nEXPLICIT MENU ITEMS: {menu_data['explicit_menu_items']}"
                        context += f"\n\nCRITICAL: You MUST ONLY mention, recommend, or suggest items from this exact list. NEVER suggest items not in this list."
                    
                    # Add menu restrictions if available
                    if "menu_restrictions" in menu_data:
                        context += f"\n\n{menu_data['menu_restrictions']}"
                    
                    # Also add menu items from structured data
                    if "menu_items" in menu_data:
                        available_items = []
                        menu_items = menu_data.get("menu_items", {})
                        if isinstance(menu_items, dict):
                            for category, items in menu_items.items():
                                if isinstance(items, list):
                                    for item in items:
                                        if isinstance(item, dict) and "name" in item and "price" in item:
                                            available_items.append(f"{item['name']} (₱{item['price']})")
                        
                        if available_items:
                            context += f"\n\nSTRUCTURED MENU ITEMS: {', '.join(available_items)}"
                            context += f"\n\nCRITICAL: You MUST ONLY mention, recommend, or suggest items from this exact list. NEVER suggest items not in this list."
                else:
                    context += f"\n\nMENU DATA:\n{menu_context}"
            except Exception as e:
                logger.error(f"Error parsing menu context: {e}")
                context += f"\n\nMENU DATA:\n{menu_context}"
        else:
            context += f"\n\nMENU DATA: No menu data available. Please ask staff for assistance."
            
        if conversation_context:
            context += f"\n\n{conversation_context}"
        
        # Create a comprehensive single agent that combines all capabilities
        fallback_prompt = f"""
You are a comprehensive restaurant ordering assistant with the following capabilities:

1. Order Coordination: Help customers place orders and manage their requests
2. Menu Expertise: Deep knowledge of menu items and recommendations
3. Language Support: Handle multilingual communication and translation
4. Dietary Assistance: Manage allergies and dietary restrictions
5. Order Validation: Ensure complete and accurate orders

**CRITICAL**: Only work with items from the restaurant's actual menu data provided.

**QUANTITY HANDLING RULES**:
- When customer doesn't specify quantity: Add exactly 1 item
- When customer specifies a number: Add exactly that quantity (e.g., "2 Cappuccinos" = add 2)
- When customer asks for multiple different items: Add all requested items with their specified quantities
- Always confirm the exact quantity being added to cart
- Use clear language like "I've added X [item] to your cart" or "I've added X [item]s to your cart"

**EXAMPLES**:
- "Add a Cappuccino" → "I've added the Cappuccino (₱200) to your cart"
- "Add 2 Cappuccinos" → "I've added 2 Cappuccinos (₱200 each) to your cart"
- "I want a Cappuccino and a Latte" → "I've added the Cappuccino (₱200) and Latte (₱210) to your cart"
- "Add 3 Cappuccinos and 2 Lattes" → "I've added 3 Cappuccinos (₱200 each) and 2 Lattes (₱210 each) to your cart"

{context}

Be helpful, friendly, and comprehensive in your responses. Handle all aspects of the customer's request in a single response.
"""
        
        # Create the fallback agent
        fallback_agent = Agent(
            system_prompt=fallback_prompt,
            model=bedrock_model,
            description="Comprehensive ordering assistant (fallback mode)"
        )
        
        # Convert request to string if needed
        if isinstance(customer_request, list):
            # Handle ContentBlocks - extract text content
            request_text = ""
            for block in customer_request:
                if hasattr(block, 'text') and block.text:
                    request_text += block.text + " "
            customer_request = request_text.strip()
        
        # Process the request
        response = fallback_agent(customer_request)
        logger.info("Fallback agent completed successfully")
        return str(response)
        
    except Exception as e:
        logger.error(f"Error in fallback agent: {e}")
        return "I apologize, but I'm experiencing technical difficulties. Please try again later or speak with our staff for assistance."