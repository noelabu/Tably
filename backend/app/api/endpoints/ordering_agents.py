import re
from fastapi import APIRouter, HTTPException, Depends, status, Form, Query
from fastapi.responses import StreamingResponse
from fastapi.security import HTTPBearer
import logging
from typing import Optional, List, Dict, Any
import json
from datetime import datetime
import asyncio
from app.core.config import settings
from app.api.dependencies.auth import get_current_user
from app.models.auth import UserResponse
from app.agents.ordering_agents import (
    ordering_assistant_agent,
    recommendation_agent,
    translation_agent,
    process_multilingual_order,
    order_recommendation_combo
)
from app.agents.orchestrator import orchestrator, create_orchestrator_with_business_context
from app.agents.swarm_tools import ordering_swarm
from pydantic import BaseModel, Field

logger = logging.getLogger(__name__)
router = APIRouter()

def filter_thinking_tags(content: str) -> str:
    """
    Filter out thinking tags from AI responses.
    
    Args:
        content: Raw AI response content
        
    Returns:
        Cleaned content without thinking tags
    """
    if not content:
        return content
    
    # Remove thinking tags and their content
    # Pattern matches <thinking>...</thinking> with any content inside
    thinking_pattern = r'<thinking>.*?</thinking>'
    cleaned_content = re.sub(thinking_pattern, '', content, flags=re.DOTALL | re.IGNORECASE)
    
    # Also remove any standalone thinking tags
    standalone_thinking = r'<thinking>.*?'
    cleaned_content = re.sub(standalone_thinking, '', cleaned_content, flags=re.DOTALL | re.IGNORECASE)
    
    # Clean up any extra whitespace that might be left
    cleaned_content = re.sub(r'\n\s*\n', '\n', cleaned_content)
    cleaned_content = cleaned_content.strip()
    
    return cleaned_content

# Request/Response Models
class OrderAssistantRequest(BaseModel):
    customer_request: str = Field(..., description="Customer's order request or question")
    menu_data: Optional[str] = Field(None, description="Optional JSON string containing menu data")
    order_context: Optional[str] = Field(None, description="Optional context about current order")

class RecommendationRequest(BaseModel):
    customer_preferences: str = Field(..., description="Customer's preferences and tastes")
    menu_data: Optional[str] = Field(None, description="Optional JSON string containing menu data")
    dietary_restrictions: Optional[str] = Field(None, description="Optional dietary restrictions")
    budget_range: Optional[str] = Field(None, description="Optional budget considerations")
    occasion: Optional[str] = Field(None, description="Optional dining occasion")

class TranslationRequest(BaseModel):
    customer_message: str = Field(..., description="Customer's message in their native language")
    source_language: Optional[str] = Field(None, description="Source language (auto-detected if not provided)")
    target_language: str = Field("english", description="Target language for translation")

class MultilingualOrderRequest(BaseModel):
    customer_message: str = Field(..., description="Customer's order in their native language")
    menu_data: Optional[str] = Field(None, description="Optional JSON string containing menu data")
    source_language: Optional[str] = Field(None, description="Optional source language hint")

class OrderRecommendationComboRequest(BaseModel):
    customer_preferences: str = Field(..., description="Customer preferences in any language")
    menu_data: Optional[str] = Field(None, description="Optional JSON string containing menu data")
    dietary_restrictions: Optional[str] = Field(None, description="Optional dietary restrictions")
    language: Optional[str] = Field(None, description="Optional language specification")

class OrderingResponse(BaseModel):
    response: str = Field(..., description="Agent response")
    request_id: str = Field(..., description="Unique identifier for the request")
    timestamp: str = Field(..., description="Response timestamp")
    agent_type: str = Field(..., description="Type of agent that processed the request")

class StreamingOrderRequest(BaseModel):
    message: str = Field(..., description="Customer message")
    context: Optional[str] = Field(None, description="Optional context")
    business_id: Optional[str] = Field(None, description="Business ID for menu context")
    session_id: Optional[str] = Field(None, description="Session ID for conversation memory")

@router.post("/order-assistant", response_model=OrderingResponse)
async def order_assistant_endpoint(
    request: OrderAssistantRequest,
    current_user: UserResponse = Depends(get_current_user)
):
    """
    Get assistance with placing orders, order modifications, and order-related questions.
    """
    try:
        logger.info(f"Order assistant request from user {current_user.id}")
        
        # Use the ordering assistant agent
        response = ordering_assistant_agent(
            request.customer_request,
            request.menu_data,
            request.order_context
        )
        
        # Filter out thinking tags from the response
        cleaned_response = filter_thinking_tags(response)
        
        # Create response
        return OrderingResponse(
            response=cleaned_response,
            request_id=f"order_{datetime.utcnow().strftime('%Y%m%d_%H%M%S')}",
            timestamp=datetime.utcnow().isoformat(),
            agent_type="ordering_assistant"
        )
        
    except Exception as e:
        logger.error(f"Error in order assistant: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="An error occurred while processing your order request"
        )

@router.post("/recommendations", response_model=OrderingResponse)
async def get_recommendations_endpoint(
    request: RecommendationRequest,
    current_user: UserResponse = Depends(get_current_user)
):
    """
    Get personalized menu recommendations based on customer preferences.
    """
    try:
        logger.info(f"Recommendation request from user {current_user.id}")
        
        # Use the recommendation agent
        response = recommendation_agent(
            request.customer_preferences,
            request.menu_data,
            request.dietary_restrictions,
            request.budget_range,
            request.occasion
        )
        
        # Filter out thinking tags from the response
        cleaned_response = filter_thinking_tags(response)
        
        # Create response
        return OrderingResponse(
            response=cleaned_response,
            request_id=f"rec_{datetime.utcnow().strftime('%Y%m%d_%H%M%S')}",
            timestamp=datetime.utcnow().isoformat(),
            agent_type="recommendation"
        )
        
    except Exception as e:
        logger.error(f"Error in recommendation agent: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="An error occurred while generating recommendations"
        )

@router.post("/translate", response_model=OrderingResponse)
async def translate_message_endpoint(
    request: TranslationRequest,
    current_user: UserResponse = Depends(get_current_user)
):
    """
    Translate customer messages for order processing.
    """
    try:
        logger.info(f"Translation request from user {current_user.id}")
        
        # Use the translation agent
        response = translation_agent(
            request.customer_message,
            request.source_language,
            request.target_language
        )
        
        # Filter out thinking tags from the response
        cleaned_response = filter_thinking_tags(response)
        
        # Create response
        return OrderingResponse(
            response=cleaned_response,
            request_id=f"trans_{datetime.utcnow().strftime('%Y%m%d_%H%M%S')}",
            timestamp=datetime.utcnow().isoformat(),
            agent_type="translation"
        )
        
    except Exception as e:
        logger.error(f"Error in translation agent: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="An error occurred while translating your message"
        )

@router.post("/multilingual-order", response_model=OrderingResponse)
async def process_multilingual_order_endpoint(
    request: MultilingualOrderRequest,
    current_user: UserResponse = Depends(get_current_user)
):
    """
    Process orders in multiple languages with translation and ordering assistance.
    """
    try:
        logger.info(f"Multilingual order request from user {current_user.id}")
        
        # Use the multilingual order processing agent
        response = process_multilingual_order(
            request.customer_message,
            request.menu_data,
            request.source_language
        )
        
        # Filter out thinking tags from the response
        cleaned_response = filter_thinking_tags(response)
        
        # Create response
        return OrderingResponse(
            response=cleaned_response,
            request_id=f"multi_{datetime.utcnow().strftime('%Y%m%d_%H%M%S')}",
            timestamp=datetime.utcnow().isoformat(),
            agent_type="multilingual_order"
        )
        
    except Exception as e:
        logger.error(f"Error in multilingual order processing: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="An error occurred while processing your multilingual order"
        )

@router.post("/order-recommendation-combo", response_model=OrderingResponse)
async def order_recommendation_combo_endpoint(
    request: OrderRecommendationComboRequest,
    current_user: UserResponse = Depends(get_current_user)
):
    """
    Combined recommendation and ordering assistance with optional translation.
    """
    try:
        logger.info(f"Order recommendation combo request from user {current_user.id}")
        
        # Use the combo agent
        response = order_recommendation_combo(
            request.customer_preferences,
            request.menu_data,
            request.dietary_restrictions,
            request.language
        )
        
        # Filter out thinking tags from the response
        cleaned_response = filter_thinking_tags(response)
        
        # Create response
        return OrderingResponse(
            response=cleaned_response,
            request_id=f"combo_{datetime.utcnow().strftime('%Y%m%d_%H%M%S')}",
            timestamp=datetime.utcnow().isoformat(),
            agent_type="order_recommendation_combo"
        )
        
    except Exception as e:
        logger.error(f"Error in order recommendation combo: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="An error occurred while processing your request"
        )

@router.post("/chat")
async def chat_with_ordering_system(
    request: StreamingOrderRequest,
    current_user: UserResponse = Depends(get_current_user)
):
    """
    Chat with the intelligent ordering system using the orchestrator.
    """
    try:
        logger.info(f"Ordering chat request from user {current_user.id}")
        
        # Use the ordering swarm with conversation memory
        response = ordering_swarm(
            customer_request=request.message,
            business_id=request.business_id,
            include_menu_context=True,
            use_swarm_mode=False,
            session_id=request.session_id or f"user_{current_user.id}_{datetime.utcnow().strftime('%Y%m%d_%H%M%S')}"
        )
        
        # Filter out thinking tags from the response
        cleaned_response = filter_thinking_tags(str(response))
        
        return {
            "response": cleaned_response,
            "request_id": f"chat_{datetime.utcnow().strftime('%Y%m%d_%H%M%S')}",
            "timestamp": datetime.utcnow().isoformat(),
            "agent_type": "orchestrator"
        }
        
    except Exception as e:
        logger.error(f"Error in ordering chat: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="An error occurred while processing your message"
        )

@router.post("/chat/stream")
async def chat_with_ordering_system_stream(
    request: StreamingOrderRequest,
    current_user: UserResponse = Depends(get_current_user)
):
    """
    Stream chat with the intelligent ordering system for real-time responses.
    """
    try:
        logger.info(f"Streaming ordering chat request")
        
        async def generate_response():
            try:
                # Create orchestrator with business context if provided
                if request.business_id:
                    agent = create_orchestrator_with_business_context(request.business_id)
                else:
                    agent = orchestrator
                
                # Use the orchestrator for streaming responses
                agent_stream = agent.stream_async(request.message)
                
                async for event in agent_stream:
                    if "data" in event:
                        # Filter out thinking tags from the response
                        cleaned_content = filter_thinking_tags(event['data'])
                        if cleaned_content:  # Only send non-empty content
                            yield f"data: {json.dumps({'content': cleaned_content, 'type': 'message'})}\n\n"
                
                # Send completion signal
                yield f"data: {json.dumps({'content': '[DONE]', 'type': 'done'})}\n\n"
                
            except Exception as e:
                logger.error(f"Error in streaming response: {e}")
                yield f"data: {json.dumps({'error': str(e), 'type': 'error'})}\n\n"
        
        return StreamingResponse(
            generate_response(),
            media_type="text/plain",
            headers={
                "Cache-Control": "no-cache",
                "Connection": "keep-alive",
                "Content-Type": "text/event-stream"
            }
        )
        
    except Exception as e:
        logger.error(f"Error in ordering streaming: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="An error occurred while processing your streaming request"
        )

@router.get("/supported-languages")
async def get_supported_languages():
    """
    Get the list of supported languages for translation and multilingual ordering.
    """
    return {
        "supported_languages": [
            {"code": "en", "name": "English", "native": "English"},
            {"code": "es", "name": "Spanish", "native": "Español"},
            {"code": "fr", "name": "French", "native": "Français"},
            {"code": "it", "name": "Italian", "native": "Italiano"},
            {"code": "de", "name": "German", "native": "Deutsch"},
            {"code": "pt", "name": "Portuguese", "native": "Português"},
            {"code": "zh", "name": "Chinese", "native": "中文"},
            {"code": "ja", "name": "Japanese", "native": "日本語"},
            {"code": "ko", "name": "Korean", "native": "한국어"},
            {"code": "ar", "name": "Arabic", "native": "العربية"},
            {"code": "hi", "name": "Hindi", "native": "हिंदी"},
            {"code": "tl", "name": "Filipino/Tagalog", "native": "Filipino/Tagalog"}
        ],
        "auto_detect": True,
        "default_target": "english"
    }

@router.get("/order-flow-help")
async def get_order_flow_help():
    """
    Get help information about the ordering flow and available features.
    """
    return {
        "ordering_flow": {
            "step_1": "Browse menu or ask for recommendations",
            "step_2": "Get personalized suggestions based on preferences",
            "step_3": "Place order with assistance from ordering agent",
            "step_4": "Confirm order details and complete transaction"
        },
        "features": {
            "multilingual_support": "Order in your native language",
            "personalized_recommendations": "Get suggestions based on your preferences",
            "dietary_accommodations": "Filter by dietary restrictions and allergies",
            "order_assistance": "Get help with order modifications and questions",
            "real_time_chat": "Chat with AI assistants for immediate help"
        },
        "example_requests": [
            "I want to order a pizza",
            "¿Qué recomiendan para una cena romántica?",
            "I need something vegetarian and gluten-free",
            "Can you help me modify my order?",
            "What's popular on the menu?"
        ]
    }

@router.get("/health")
async def health_check():
    """
    Health check endpoint for the ordering agents service.
    """
    try:
        # Test basic agent functionality
        test_response = ordering_assistant_agent("Hello, I need help with ordering")
        
        return {
            "status": "healthy",
            "timestamp": datetime.utcnow().isoformat(),
            "agents_available": {
                "ordering_assistant": True,
                "recommendation": True,
                "translation": True,
                "multilingual_order": True,
                "combo": True
            },
            "test_response_length": len(test_response)
        }
        
    except Exception as e:
        logger.error(f"Health check failed: {e}")
        return {
            "status": "unhealthy",
            "timestamp": datetime.utcnow().isoformat(),
            "agents_available": {
                "ordering_assistant": False,
                "recommendation": False,
                "translation": False,
                "multilingual_order": False,
                "combo": False
            },
            "error": str(e)
        }

