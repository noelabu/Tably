from pydantic import BaseModel, Field
from typing import List, Optional, Dict, Any
from decimal import Decimal

class ModifierOption(BaseModel):
    name: str = Field(..., description="Name of the modifier option")
    price: Optional[Decimal] = Field(None, description="Additional price for this option")

class Modifier(BaseModel):
    type: str = Field(..., description="Type of modifier (size, spice_level, extras, etc.)")
    options: List[ModifierOption] = Field(default_factory=list, description="Available options for this modifier")

class ComboItem(BaseModel):
    name: str = Field(..., description="Name of the combo")
    includes: List[str] = Field(default_factory=list, description="Items included in the combo")
    price: Optional[Decimal] = Field(None, description="Price of the combo")

class SizeOption(BaseModel):
    name: str = Field(..., description="Size name (Regular, Large, etc.)")
    price: Optional[Decimal] = Field(None, description="Price for this size")

class ExtractedMenuItem(BaseModel):
    name: str = Field(..., description="Name of the menu item")
    description: Optional[str] = Field(None, description="Description of the menu item")
    price: Optional[Decimal] = Field(None, description="Price of the menu item")
    category: str = Field(default="other", description="Category of the menu item")
    allergens: List[str] = Field(default_factory=list, description="List of allergens")
    ingredients: List[str] = Field(default_factory=list, description="List of ingredients")
    modifiers: List[Modifier] = Field(default_factory=list, description="Available modifiers")
    combos: List[ComboItem] = Field(default_factory=list, description="Available combos")
    sizes: List[SizeOption] = Field(default_factory=list, description="Available sizes")

class RestaurantInfo(BaseModel):
    restaurant_name: Optional[str] = Field(None, description="Name of the restaurant")
    cuisine_type: Optional[str] = Field(None, description="Type of cuisine")

class MenuImageAnalysisResult(BaseModel):
    restaurant_info: RestaurantInfo = Field(default_factory=RestaurantInfo, description="Restaurant information")
    menu_items: List[ExtractedMenuItem] = Field(default_factory=list, description="Extracted menu items")
    total_items: int = Field(default=0, description="Total number of items extracted")
    analysis_confidence: Optional[float] = Field(None, description="Confidence score of the analysis")

class MenuImageAnalysisRequest(BaseModel):
    business_id: str = Field(..., description="ID of the business uploading the menu")
    image_name: Optional[str] = Field(None, description="Name of the uploaded image file")
    auto_create_items: bool = Field(True, description="Whether to automatically create menu items from analysis")

class MenuImageAnalysisResponse(BaseModel):
    analysis_id: str = Field(..., description="ID of the analysis")
    business_id: str = Field(..., description="ID of the business")
    result: MenuImageAnalysisResult = Field(..., description="Analysis results")
    created_items: List[str] = Field(default_factory=list, description="IDs of created menu items")
    status: str = Field(..., description="Status of the analysis")
    created_at: str = Field(..., description="Timestamp of analysis creation")
    
class MenuImageAnalysisError(BaseModel):
    error_code: str = Field(..., description="Error code")
    error_message: str = Field(..., description="Error message")
    details: Optional[Dict[str, Any]] = Field(None, description="Additional error details")