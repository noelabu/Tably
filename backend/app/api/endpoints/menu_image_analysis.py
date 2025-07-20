from fastapi import APIRouter, HTTPException, Depends, status, UploadFile, File, Form
from fastapi.responses import JSONResponse
import logging
from typing import Optional, List
import uuid
from datetime import datetime
from app.core.config import settings
from app.api.dependencies.auth import get_current_user
from app.models.auth import UserResponse
from app.models.menu_image_analysis import (
    MenuImageAnalysisRequest,
    MenuImageAnalysisResponse,
    MenuImageAnalysisResult,
    MenuImageAnalysisError,
    ExtractedMenuItem
)
from app.models.menu_items import MenuItemCreate
from app.services.menu_image_analyzer import MenuImageAnalyzer
from app.db.menu_items import MenuItemsConnection
from app.agents.menu_agent import (
    menu_intelligent_agent,
    analyze_menu_image as agent_analyze_menu_image,
    get_menu_recommendations,
    search_menu_items,
    get_allergen_information
)
import json
import io
from pdf2image import convert_from_bytes
from app.models.stock_levels import StockLevelCreate
from decimal import Decimal

logger = logging.getLogger(__name__)
router = APIRouter()

def get_menu_image_analyzer() -> MenuImageAnalyzer:
    """Dependency to get MenuImageAnalyzer instance"""
    return MenuImageAnalyzer()

def get_menu_items_db() -> MenuItemsConnection:
    """Dependency to get MenuItemsConnection instance"""
    return MenuItemsConnection()

# Utility to extract images from PDF bytes
async def extract_images_from_pdf(pdf_bytes: bytes) -> List[bytes]:
    images = convert_from_bytes(pdf_bytes)
    image_bytes_list = []
    for img in images:
        buf = io.BytesIO()
        img.save(buf, format='JPEG')
        image_bytes_list.append(buf.getvalue())
    return image_bytes_list

@router.post("/extract-only", response_model=MenuImageAnalysisResult)
async def extract_menu_items_only(
    file: UploadFile = File(..., description="Menu image file"),
    current_user: UserResponse = Depends(get_current_user),
    analyzer: MenuImageAnalyzer = Depends(get_menu_image_analyzer)
):
    try:
        logger.info("Starting menu image analysis (extract only)")
        content_type = file.content_type or ''
        results = []
        if content_type.startswith('image/'):
            image_bytes = await file.read()
            result = await analyzer.analyze_menu_image(image_bytes)
            validated_result = await analyzer.validate_menu_data(result)
            menu_analysis_result = MenuImageAnalysisResult(
                restaurant_info=validated_result.get('restaurant_info', {}),
                menu_items=[ExtractedMenuItem(**item) for item in validated_result.get('menu_items', [])],
                total_items=len(validated_result.get('menu_items', [])),
                analysis_confidence=0.9
            )
            return menu_analysis_result
        else:
            raise HTTPException(status_code=400, detail="Unsupported file type. Upload an image file.")
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error analyzing menu image: {e}")
        raise HTTPException(status_code=500, detail="An error occurred while analyzing the menu image")

@router.post("/analyze", response_model=MenuImageAnalysisResponse)
async def analyze_menu_image(
    file: UploadFile = File(..., description="Menu image file"),
    business_id: str = Form(..., description="ID of the business uploading the menu"),
    auto_create_items: bool = Form(True, description="Whether to automatically create menu items from analysis"),
    current_user: UserResponse = Depends(get_current_user),
    analyzer: MenuImageAnalyzer = Depends(get_menu_image_analyzer),
    menu_items_db: MenuItemsConnection = Depends(get_menu_items_db)
):
    analysis_id = str(uuid.uuid4())
    try:
        logger.info(f"Starting menu image analysis for business {business_id}")
        if not await menu_items_db.verify_business_ownership(business_id, current_user.id):
            raise HTTPException(status_code=403, detail="You don't have permission to access this business")
        content_type = file.content_type or ''
        results = []
        if content_type.startswith('image/'):
            image_bytes = await file.read()
            result = await analyzer.analyze_menu_image(image_bytes)
            validated_result = await analyzer.validate_menu_data(result)
            menu_analysis_result = MenuImageAnalysisResult(
                restaurant_info=validated_result.get('restaurant_info', {}),
                menu_items=[ExtractedMenuItem(**item) for item in validated_result.get('menu_items', [])],
                total_items=len(validated_result.get('menu_items', [])),
                analysis_confidence=0.9
            )
            created_items = []
            if auto_create_items and menu_analysis_result.menu_items:
                for extracted_item in menu_analysis_result.menu_items:
                    menu_item_create = MenuItemCreate(
                        business_id=business_id,
                        name=extracted_item.name,
                        description=extracted_item.description,
                        price=extracted_item.price if extracted_item.price is not None else Decimal('0.0'),
                        image_url=None,
                        available=True,
                        stock_level=StockLevelCreate(quantity_available=0, total_quantity=0)
                    )
                    menu_item_data = menu_item_create.dict()
                    result = await menu_items_db.create_menu_item(menu_item_data)
                    if result and result.get('id'):
                        created_items.append(result['id'])
            response = MenuImageAnalysisResponse(
                analysis_id=analysis_id,
                business_id=business_id,
                result=menu_analysis_result,
                created_items=created_items,
                status="completed",
                created_at=datetime.utcnow().isoformat()
            )
            return response
        else:
            raise HTTPException(status_code=400, detail="Unsupported file type. Upload an image file.")
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error analyzing menu image: {e}")
        raise HTTPException(status_code=500, detail="An error occurred while analyzing the menu image")

@router.get("/analysis/{analysis_id}", response_model=MenuImageAnalysisResponse)
async def get_menu_analysis(
    analysis_id: str,
    current_user: UserResponse = Depends(get_current_user)
):
    """
    Get the results of a previous menu image analysis.
    Note: This is a placeholder endpoint - in a real implementation,
    you would store analysis results in a database.
    """
    # This would typically fetch from a database
    # For now, return a placeholder response
    raise HTTPException(
        status_code=status.HTTP_501_NOT_IMPLEMENTED,
        detail="Analysis retrieval not implemented yet. Analysis results are returned immediately after processing."
    )

@router.post("/bulk-extract-only", response_model=List[MenuImageAnalysisResult])
async def bulk_extract_menu_items_only(
    files: List[UploadFile] = File(..., description="Multiple menu image files"),
    current_user: UserResponse = Depends(get_current_user),
    analyzer: MenuImageAnalyzer = Depends(get_menu_image_analyzer)
):
    try:
        logger.info(f"Starting bulk menu image analysis (extract only) with {len(files)} files")
        if len(files) > 10:
            raise HTTPException(status_code=400, detail="Too many files. Maximum 10 per request.")
        results = []
        for file in files:
            content_type = file.content_type or ''
            if content_type.startswith('image/'):
                image_bytes = await file.read()
                result = await analyzer.analyze_menu_image(image_bytes)
                validated_result = await analyzer.validate_menu_data(result)
                menu_analysis_result = MenuImageAnalysisResult(
                    restaurant_info=validated_result.get('restaurant_info', {}),
                    menu_items=[ExtractedMenuItem(**item) for item in validated_result.get('menu_items', [])],
                    total_items=len(validated_result.get('menu_items', [])),
                    analysis_confidence=0.9
                )
                results.append(menu_analysis_result)
            else:
                results.append(MenuImageAnalysisResult(analysis_confidence=None))
        return results
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error in bulk menu image extract-only analysis: {e}")
        raise HTTPException(status_code=500, detail="An error occurred while analyzing the menu images")

@router.post("/bulk-analyze", response_model=List[MenuImageAnalysisResponse])
async def bulk_analyze_menu_images(
    files: List[UploadFile] = File(..., description="Multiple menu image files"),
    business_id: str = Form(..., description="ID of the business uploading the menus"),
    auto_create_items: bool = Form(True, description="Whether to automatically create menu items from analysis"),
    current_user: UserResponse = Depends(get_current_user),
    analyzer: MenuImageAnalyzer = Depends(get_menu_image_analyzer),
    menu_items_db: MenuItemsConnection = Depends(get_menu_items_db)
):
    try:
        logger.info(f"Starting bulk menu image analysis for business {business_id} with {len(files)} files")
        if not await menu_items_db.verify_business_ownership(business_id, current_user.id):
            raise HTTPException(status_code=403, detail="You don't have permission to access this business")
        if len(files) > 10:
            raise HTTPException(status_code=400, detail="Too many files. Maximum 10 per request.")
        results = []
        for file in files:
            content_type = file.content_type or ''
            analysis_id = str(uuid.uuid4())
            if content_type.startswith('image/'):
                image_bytes = await file.read()
                result = await analyzer.analyze_menu_image(image_bytes)
                validated_result = await analyzer.validate_menu_data(result)
                menu_analysis_result = MenuImageAnalysisResult(
                    restaurant_info=validated_result.get('restaurant_info', {}),
                    menu_items=[ExtractedMenuItem(**item) for item in validated_result.get('menu_items', [])],
                    total_items=len(validated_result.get('menu_items', [])),
                    analysis_confidence=0.9
                )
                created_items = []
                if auto_create_items and menu_analysis_result.menu_items:
                    for extracted_item in menu_analysis_result.menu_items:
                        menu_item_create = MenuItemCreate(
                            business_id=business_id,
                            name=extracted_item.name,
                            description=extracted_item.description,
                            price=extracted_item.price if extracted_item.price is not None else Decimal('0.0'),
                            image_url=None,
                            available=True,
                            stock_level=StockLevelCreate(quantity_available=0, total_quantity=0)
                        )
                        menu_item_data = menu_item_create.dict()
                        result = await menu_items_db.create_menu_item(menu_item_data)
                        if result and result.get('id'):
                            created_items.append(result['id'])
                response = MenuImageAnalysisResponse(
                    analysis_id=analysis_id,
                    business_id=business_id,
                    result=menu_analysis_result,
                    created_items=created_items,
                    status="completed",
                    created_at=datetime.utcnow().isoformat()
                )
                results.append(response)
            else:
                logger.warning(f"Unsupported file type: {file.filename}")
        return results
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error in bulk menu image analysis: {e}")
        raise HTTPException(status_code=500, detail="An error occurred while analyzing the menu images")

@router.get("/supported-formats")
async def get_supported_formats():
    """
    Get the list of supported image formats for menu analysis.
    """
    return {
        "supported_formats": [
            "JPEG",
            "PNG",
            "WEBP",
            "GIF",
            "BMP"
        ],
        "max_file_size": "20MB",
        "max_dimensions": "2048x2048",
        "recommended_formats": ["JPEG", "PNG"]
    }

@router.post("/extract-with-intelligence", response_model=MenuImageAnalysisResult)
async def extract_menu_items_with_intelligence(
    image: UploadFile = File(..., description="Menu image file"),
    query: Optional[str] = Form(None, description="Optional question about the menu"),
    current_user: UserResponse = Depends(get_current_user),
    analyzer: MenuImageAnalyzer = Depends(get_menu_image_analyzer)
):
    """
    Analyze a menu image using both traditional analysis and AI intelligence.
    Optionally answer questions about the menu.
    """
    try:
        logger.info("Starting intelligent menu image analysis")
        
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
        
        logger.info(f"Analyzing image of size {len(image_bytes)} bytes with AI intelligence")
        
        # Use the menu agent to analyze the image
        agent_analysis = agent_analyze_menu_image(image_bytes)
        
        # Parse the agent's response
        try:
            parsed_analysis = json.loads(agent_analysis)
        except json.JSONDecodeError:
            logger.error("Failed to parse agent analysis response")
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Error parsing menu analysis result"
            )
        
        # Create MenuImageAnalysisResult object
        menu_analysis_result = MenuImageAnalysisResult(
            restaurant_info=parsed_analysis.get('restaurant_info', {}),
            menu_items=[
                ExtractedMenuItem(
                    name=item.get('name', ''),
                    description=item.get('description', ''),
                    price=item.get('price'),
                    category=item.get('category', ''),
                    allergens=item.get('allergens', []),
                    dietary_info=item.get('dietary_info', [])
                ) for item in parsed_analysis.get('menu_items', [])
            ],
            total_items=parsed_analysis.get('total_items', 0),
            analysis_confidence=parsed_analysis.get('confidence_score', 0.9)
        )
        
        # If there's a query, use the menu agent to answer it
        if query:
            logger.info(f"Processing query: {query}")
            intelligence_response = menu_intelligent_agent(query, agent_analysis)
            
            # Add the intelligence response to the restaurant info
            menu_analysis_result.restaurant_info['intelligence_response'] = intelligence_response
            menu_analysis_result.restaurant_info['user_query'] = query
        
        logger.info(f"Intelligent menu image analysis completed. Found {len(menu_analysis_result.menu_items)} items")
        
        return menu_analysis_result
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error in intelligent menu image analysis: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="An error occurred while analyzing the menu image with AI intelligence"
        )

@router.post("/analyze-with-recommendations")
async def analyze_menu_with_recommendations(
    image: UploadFile = File(..., description="Menu image file"),
    business_id: str = Form(..., description="ID of the business uploading the menu"),
    dietary_preferences: Optional[str] = Form(None, description="Dietary preferences for recommendations"),
    auto_create_items: bool = Form(True, description="Whether to automatically create menu items from analysis"),
    current_user: UserResponse = Depends(get_current_user),
    analyzer: MenuImageAnalyzer = Depends(get_menu_image_analyzer),
    menu_items_db: MenuItemsConnection = Depends(get_menu_items_db)
):
    """
    Analyze a menu image, create items in database, and provide intelligent recommendations.
    """
    analysis_id = str(uuid.uuid4())
    
    try:
        logger.info(f"Starting intelligent menu analysis with recommendations for business {business_id}")
        
        # Verify user owns the business
        if not await menu_items_db.verify_business_ownership(business_id, current_user.id):
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="You don't have permission to access this business"
            )
        
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
        
        logger.info(f"Analyzing image of size {len(image_bytes)} bytes with AI intelligence")
        
        # Use the menu agent to analyze the image
        agent_analysis = agent_analyze_menu_image(image_bytes)
        
        # Parse the agent's response
        try:
            parsed_analysis = json.loads(agent_analysis)
        except json.JSONDecodeError:
            logger.error("Failed to parse agent analysis response")
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Error parsing menu analysis result"
            )
        
        # Create MenuImageAnalysisResult object
        menu_analysis_result = MenuImageAnalysisResult(
            restaurant_info=parsed_analysis.get('restaurant_info', {}),
            menu_items=[
                ExtractedMenuItem(
                    name=item.get('name', ''),
                    description=item.get('description', ''),
                    price=item.get('price'),
                    category=item.get('category', ''),
                    allergens=item.get('allergens', []),
                    dietary_info=item.get('dietary_info', [])
                ) for item in parsed_analysis.get('menu_items', [])
            ],
            total_items=parsed_analysis.get('total_items', 0),
            analysis_confidence=parsed_analysis.get('confidence_score', 0.9)
        )
        
        created_items = []
        
        # Automatically create menu items if requested
        if auto_create_items and menu_analysis_result.menu_items:
            logger.info(f"Auto-creating {len(menu_analysis_result.menu_items)} menu items")
            
            for extracted_item in menu_analysis_result.menu_items:
                try:
                    # Create menu item data
                    menu_item_create = MenuItemCreate(
                        business_id=business_id,
                        name=extracted_item.name,
                        description=extracted_item.description,
                        price=extracted_item.price if extracted_item.price is not None else 0.0,
                        image_url=None,
                        available=True
                    )
                    
                    # Create menu item in database
                    menu_item_data = {
                        "business_id": menu_item_create.business_id,
                        "name": menu_item_create.name,
                        "description": menu_item_create.description,
                        "price": float(menu_item_create.price),
                        "image_url": menu_item_create.image_url,
                        "available": menu_item_create.available
                    }
                    
                    result = await menu_items_db.create_menu_item(menu_item_data)
                    
                    if result and result.get('id'):
                        created_items.append(result['id'])
                        logger.info(f"Created menu item: {extracted_item.name} (ID: {result['id']})")
                    else:
                        logger.warning(f"Failed to create menu item: {extracted_item.name}")
                        
                except Exception as e:
                    logger.error(f"Error creating menu item '{extracted_item.name}': {e}")
                    continue
        
        # Get recommendations if dietary preferences are provided
        recommendations = None
        if dietary_preferences:
            logger.info(f"Getting recommendations for dietary preferences: {dietary_preferences}")
            recommendations = get_menu_recommendations(dietary_preferences, agent_analysis)
        
        # Create response
        response = {
            "analysis_id": analysis_id,
            "business_id": business_id,
            "result": menu_analysis_result,
            "created_items": created_items,
            "recommendations": recommendations,
            "status": "completed",
            "created_at": datetime.utcnow().isoformat()
        }
        
        logger.info(f"Intelligent menu analysis completed. Found {len(menu_analysis_result.menu_items)} items, created {len(created_items)} items")
        
        return response
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error in intelligent menu analysis with recommendations: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="An error occurred while analyzing the menu image with AI intelligence"
        )