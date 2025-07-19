from strands import tool
from typing import Optional, Union
import asyncio
import logging
from app.agents.swarm_orchestrator import process_order_with_swarm, process_order_with_swarm_async
from app.services.menu_context_service import menu_context_service
from app.services.conversation_memory import conversation_memory

logger = logging.getLogger(__name__)

@tool
def ordering_swarm(
    customer_request: str,
    business_id: Optional[str] = None,
    include_menu_context: bool = True,
    use_swarm_mode: bool = False,
    session_id: Optional[str] = None
) -> str:
    """
    Process customer orders using intelligent agent system (optimized for Nova Lite).
    
    This system uses a comprehensive single agent by default for optimal performance,
    with optional swarm mode for complex scenarios:
    - Order Coordination: Routes requests and maintains conversation flow
    - Menu Expertise: Deep menu knowledge and recommendations  
    - Language Support: Multilingual support and translation
    - Dietary Assistance: Handles allergies and dietary restrictions
    - Order Validation: Ensures complete and accurate orders
    
    Args:
        customer_request: The customer's order or question
        business_id: Optional business ID to load specific menu
        include_menu_context: Whether to load menu data (default: True)
        use_swarm_mode: Force swarm mode (default: False for stability)
        session_id: Optional session ID for conversation memory
        
    Returns:
        Processed order response from the intelligent agent system
    """
    try:
        menu_context = None
        conversation_context = None
        
        # Load menu context if requested and business_id provided
        if include_menu_context and business_id:
            try:
                # Run async function in sync context
                loop = asyncio.new_event_loop()
                asyncio.set_event_loop(loop)
                menu_context = loop.run_until_complete(
                    menu_context_service.get_business_menu_context(business_id)
                )
                loop.close()
                logger.info(f"Loaded menu context for business {business_id}")
            except Exception as e:
                logger.error(f"Error loading menu context: {e}")
                menu_context = None
        
        # Load conversation context if session_id provided
        if session_id:
            try:
                # Add user message to conversation
                conversation_memory.add_user_message(session_id, customer_request, business_id)
                # Get conversation context
                conversation_context = conversation_memory.get_conversation_context(session_id)
                logger.info(f"Loaded conversation context for session {session_id}")
            except Exception as e:
                logger.error(f"Error loading conversation context: {e}")
                conversation_context = None
        
        # Process with optimized agent system  
        result = process_order_with_swarm(
            customer_request=customer_request,
            business_id=business_id,
            menu_context=menu_context,
            conversation_context=conversation_context,
            force_swarm=use_swarm_mode
        )
        
        # Add assistant response to conversation
        if session_id:
            try:
                conversation_memory.add_assistant_message(session_id, result)
            except Exception as e:
                logger.error(f"Error saving assistant response: {e}")
        
        return result
        
    except Exception as e:
        logger.error(f"Error in ordering swarm tool: {e}")
        return f"I apologize, but I encountered an error with the ordering system. Error: {str(e)}"

@tool 
def recommendation_swarm(
    preferences: str,
    dietary_restrictions: Optional[str] = None,
    occasion: Optional[str] = None,
    business_id: Optional[str] = None
) -> str:
    """
    Get personalized menu recommendations using a swarm of specialist agents.
    
    The swarm will collaborate to:
    - Understand your preferences and dietary needs
    - Suggest appropriate menu items
    - Consider the dining occasion
    - Provide complete meal recommendations
    
    Args:
        preferences: Customer's taste preferences or what they're looking for
        dietary_restrictions: Any dietary restrictions or allergies
        occasion: The dining occasion (date, business lunch, family dinner, etc.)
        business_id: Optional business ID for specific menu
        
    Returns:
        Personalized recommendations from the swarm
    """
    try:
        # Build the request for the swarm
        request = f"I need menu recommendations. Preferences: {preferences}"
        
        if dietary_restrictions:
            request += f"\nDietary restrictions: {dietary_restrictions}"
            
        if occasion:
            request += f"\nOccasion: {occasion}"
            
        request += "\nPlease provide detailed recommendations with complete meal suggestions."
        
        # Load menu context if business_id provided
        menu_context = None
        if business_id:
            try:
                loop = asyncio.new_event_loop()
                asyncio.set_event_loop(loop)
                menu_context = loop.run_until_complete(
                    menu_context_service.get_business_menu_context(business_id)
                )
                loop.close()
            except Exception as e:
                logger.error(f"Error loading menu context: {e}")
        
        # Process with optimized agent system
        result = process_order_with_swarm(
            customer_request=request,
            business_id=business_id,
            menu_context=menu_context,
            force_swarm=False  # Use stable single agent approach
        )
        
        return result
        
    except Exception as e:
        logger.error(f"Error in recommendation swarm tool: {e}")
        return f"I apologize, but I couldn't generate recommendations. Error: {str(e)}"

@tool
def multilingual_ordering_swarm(
    customer_message: str,
    detected_language: Optional[str] = None,
    business_id: Optional[str] = None
) -> str:
    """
    Process orders in any language using a swarm with language specialists.
    
    The swarm will:
    - Detect the customer's language
    - Translate the request accurately
    - Process the order with full understanding
    - Respond in the customer's language when possible
    
    Args:
        customer_message: Order or request in any language
        detected_language: Optional hint about the language
        business_id: Optional business ID for menu context
        
    Returns:
        Processed order with translation support
    """
    try:
        # Add language context to the request
        request = customer_message
        if detected_language:
            request = f"[Customer language: {detected_language}]\n{customer_message}"
        
        # Load menu context
        menu_context = None
        if business_id:
            try:
                loop = asyncio.new_event_loop()
                asyncio.set_event_loop(loop)
                menu_context = loop.run_until_complete(
                    menu_context_service.get_business_menu_context(business_id)
                )
                loop.close()
            except Exception as e:
                logger.error(f"Error loading menu context: {e}")
        
        # Process with optimized agent system - comprehensive language support  
        result = process_order_with_swarm(
            customer_request=request,
            business_id=business_id,
            menu_context=menu_context,
            force_swarm=False  # Use stable single agent approach
        )
        
        return result
        
    except Exception as e:
        logger.error(f"Error in multilingual ordering swarm: {e}")
        return f"Translation error occurred. Error: {str(e)}"