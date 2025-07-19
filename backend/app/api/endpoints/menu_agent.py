from fastapi import APIRouter, HTTPException, Depends, status, UploadFile, File, Form, Query
from fastapi.responses import JSONResponse, StreamingResponse
from fastapi.security import HTTPBearer
import logging
from typing import Optional, List, Dict, Any
import json
import base64
from datetime import datetime
import asyncio
from app.core.config import settings
from app.api.dependencies.auth import get_current_user
from app.models.auth import UserResponse
from app.agents.menu_agent import (
    menu_intelligent_agent,
    analyze_menu_image,
    get_menu_recommendations,
    search_menu_items,
    get_allergen_information,
    menu_agent
)
from app.agents.orchestrator import orchestrator
from pydantic import BaseModel, Field

logger = logging.getLogger(__name__)
router = APIRouter()

# Request/Response Models
class MenuAgentQuery(BaseModel):
    query: str = Field(..., description="User query about menu items or recommendations")
    menu_data: Optional[str] = Field(None, description="Optional JSON string containing menu data")

class MenuAgentResponse(BaseModel):
    response: str = Field(..., description="Agent response to the query")
    query_id: str = Field(..., description="Unique identifier for the query")
    timestamp: str = Field(..., description="Response timestamp")

class MenuRecommendationRequest(BaseModel):
    dietary_preferences: str = Field(..., description="User's dietary preferences and restrictions")
    menu_data: Optional[str] = Field(None, description="Optional JSON string containing menu data")

class MenuSearchRequest(BaseModel):
    search_term: str = Field(..., description="Term to search for in menu items")
    menu_data: Optional[str] = Field(None, description="Optional JSON string containing menu data")

class AllergenInformationRequest(BaseModel):
    allergen: str = Field(..., description="Specific allergen to check for")
    menu_data: Optional[str] = Field(None, description="Optional JSON string containing menu data")

class MenuImageAnalysisRequest(BaseModel):
    analysis_status: str
    restaurant_info: Dict[str, Any]
    menu_categories: List[str]
    total_items: int
    menu_items: List[Dict[str, Any]]
    confidence_score: float

class ChatMessage(BaseModel):
    message: str = Field(..., description="Chat message from user")
    menu_data: Optional[str] = Field(None, description="Optional menu data context")

@router.post("/chat", response_model=MenuAgentResponse)
async def chat_with_menu_agent(
    request: MenuAgentQuery,
    current_user: UserResponse = Depends(get_current_user)
):
    """
    Chat with the menu intelligent agent about menu items, recommendations, and analysis.
    """
    try:
        logger.info(f"Menu agent query from user {current_user.id}: {request.query}")
        
        # Use the menu intelligent agent
        response = menu_intelligent_agent(request.query, request.menu_data)
        
        # Create response
        menu_response = MenuAgentResponse(
            response=response,
            query_id=f"query_{datetime.utcnow().strftime('%Y%m%d_%H%M%S')}",
            timestamp=datetime.utcnow().isoformat()
        )
        
        return menu_response
        
    except Exception as e:
        logger.error(f"Error in menu agent chat: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="An error occurred while processing your query"
        )

@router.post("/chat/stream")
async def chat_with_menu_agent_stream(
    message: ChatMessage,
    current_user: UserResponse = Depends(get_current_user)
):
    """
    Stream chat with the menu intelligent agent for real-time responses.
    """
    try:
        logger.info(f"Streaming menu agent query from user {current_user.id}: {message.message}")
        
        async def generate_response():
            try:
                # Use the orchestrator for streaming responses
                agent_stream = orchestrator.stream_async(message.message)
                
                async for event in agent_stream:
                    if "data" in event:
                        yield f"data: {json.dumps({'content': event['data']})}\n\n"
                
                # Send completion signal
                yield f"data: {json.dumps({'content': '[DONE]'})}\n\n"
                
            except Exception as e:
                logger.error(f"Error in streaming response: {e}")
                yield f"data: {json.dumps({'error': str(e)})}\n\n"
        
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
        logger.error(f"Error in menu agent streaming: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="An error occurred while processing your streaming query"
        )

@router.post("/analyze-image", response_model=MenuImageAnalysisRequest)
async def analyze_menu_image_with_agent(
    image: UploadFile = File(..., description="Menu image file"),
    current_user: UserResponse = Depends(get_current_user)
):
    """
    Analyze a menu image using the menu intelligent agent.
    """
    try:
        logger.info(f"Menu image analysis request from user {current_user.id}")
        
        # Validate image file
        if not image.content_type or not image.content_type.startswith('image/'):
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Invalid file type. Please upload an image file."
            )
        
        # Read image bytes
        image_bytes = await image.read()
        
        if len(image_bytes) == 0:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Empty image file"
            )
        
        # Check file size (max 20MB)
        max_size = 20 * 1024 * 1024  # 20MB
        if len(image_bytes) > max_size:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Image file too large. Maximum size is 20MB."
            )
        
        # Analyze the image using the menu agent
        analysis_result = analyze_menu_image(image_bytes)
        
        # Parse the JSON response from the agent
        parsed_result = json.loads(analysis_result)
        
        # Create response
        return MenuImageAnalysisRequest(**parsed_result)
        
    except json.JSONDecodeError as e:
        logger.error(f"Error parsing menu analysis result: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Error parsing menu analysis result"
        )
    except Exception as e:
        logger.error(f"Error in menu image analysis: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="An error occurred while analyzing the menu image"
        )

@router.post("/recommendations", response_model=MenuAgentResponse)
async def get_menu_recommendations_endpoint(
    request: MenuRecommendationRequest,
    current_user: UserResponse = Depends(get_current_user)
):
    """
    Get menu recommendations based on dietary preferences and restrictions.
    """
    try:
        logger.info(f"Menu recommendations request from user {current_user.id}")
        
        # Get recommendations using the menu agent
        recommendations = get_menu_recommendations(request.dietary_preferences, request.menu_data)
        
        # Create response
        return MenuAgentResponse(
            response=recommendations,
            query_id=f"recommendations_{datetime.utcnow().strftime('%Y%m%d_%H%M%S')}",
            timestamp=datetime.utcnow().isoformat()
        )
        
    except Exception as e:
        logger.error(f"Error getting menu recommendations: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="An error occurred while getting menu recommendations"
        )

@router.post("/search", response_model=MenuAgentResponse)
async def search_menu_items_endpoint(
    request: MenuSearchRequest,
    current_user: UserResponse = Depends(get_current_user)
):
    """
    Search for specific menu items or ingredients.
    """
    try:
        logger.info(f"Menu search request from user {current_user.id}: {request.search_term}")
        
        # Search menu items using the menu agent
        search_results = search_menu_items(request.search_term, request.menu_data)
        
        # Create response
        return MenuAgentResponse(
            response=search_results,
            query_id=f"search_{datetime.utcnow().strftime('%Y%m%d_%H%M%S')}",
            timestamp=datetime.utcnow().isoformat()
        )
        
    except Exception as e:
        logger.error(f"Error searching menu items: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="An error occurred while searching menu items"
        )

@router.post("/allergen-info", response_model=MenuAgentResponse)
async def get_allergen_information_endpoint(
    request: AllergenInformationRequest,
    current_user: UserResponse = Depends(get_current_user)
):
    """
    Get detailed allergen information for menu items.
    """
    try:
        logger.info(f"Allergen information request from user {current_user.id}: {request.allergen}")
        
        # Get allergen information using the menu agent
        allergen_info = get_allergen_information(request.allergen, request.menu_data)
        
        # Create response
        return MenuAgentResponse(
            response=allergen_info,
            query_id=f"allergen_{datetime.utcnow().strftime('%Y%m%d_%H%M%S')}",
            timestamp=datetime.utcnow().isoformat()
        )
        
    except Exception as e:
        logger.error(f"Error getting allergen information: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="An error occurred while getting allergen information"
        )

@router.post("/analyze-and-chat")
async def analyze_and_chat(
    image: UploadFile = File(..., description="Menu image file"),
    query: str = Form(..., description="Question about the menu"),
    current_user: UserResponse = Depends(get_current_user)
):
    """
    Analyze a menu image and then answer questions about it in one request.
    """
    try:
        logger.info(f"Analyze and chat request from user {current_user.id}")
        
        # Validate image file
        if not image.content_type or not image.content_type.startswith('image/'):
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Invalid file type. Please upload an image file."
            )
        
        # Read image bytes
        image_bytes = await image.read()
        
        if len(image_bytes) == 0:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Empty image file"
            )
        
        # Check file size (max 20MB)
        max_size = 20 * 1024 * 1024  # 20MB
        if len(image_bytes) > max_size:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Image file too large. Maximum size is 20MB."
            )
        
        # First analyze the image
        analysis_result = analyze_menu_image(image_bytes)
        
        # Then use the analysis result to answer the query
        response = menu_intelligent_agent(query, analysis_result)
        
        # Create response
        return {
            "analysis_result": json.loads(analysis_result),
            "chat_response": response,
            "query": query,
            "timestamp": datetime.utcnow().isoformat()
        }
        
    except json.JSONDecodeError as e:
        logger.error(f"Error parsing menu analysis result: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Error parsing menu analysis result"
        )
    except Exception as e:
        logger.error(f"Error in analyze and chat: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="An error occurred while processing your request"
        )

@router.get("/health")
async def health_check():
    """
    Health check endpoint for the menu agent service.
    """
    try:
        # Test basic agent functionality
        test_response = menu_intelligent_agent("What types of cuisine do you typically help with?")
        
        return {
            "status": "healthy",
            "timestamp": datetime.utcnow().isoformat(),
            "agent_available": True,
            "test_response_length": len(test_response)
        }
        
    except Exception as e:
        logger.error(f"Health check failed: {e}")
        return {
            "status": "unhealthy",
            "timestamp": datetime.utcnow().isoformat(),
            "agent_available": False,
            "error": str(e)
        }