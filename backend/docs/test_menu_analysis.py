#!/usr/bin/env python3
"""
Test script for menu image analysis endpoint
"""

import json
from pathlib import Path

def test_menu_image_analysis_setup():
    """Test that all required components are properly set up"""
    
    # Check if all required files exist
    required_files = [
        "app/services/menu_image_analyzer.py",
        "app/models/menu_image_analysis.py", 
        "app/api/endpoints/menu_image_analysis.py",
        "app/core/config.py"
    ]
    
    backend_dir = Path(__file__).parent.parent
    
    for file_path in required_files:
        full_path = backend_dir / file_path
        if not full_path.exists():
            print(f"❌ Missing file: {file_path}")
            return False
        else:
            print(f"✅ Found: {file_path}")
    
    # Test that .env has AWS_BEARER_TOKEN_BEDROCK
    env_file = backend_dir / ".env"
    if env_file.exists():
        with open(env_file, 'r') as f:
            env_content = f.read()
            if "AWS_BEARER_TOKEN_BEDROCK" in env_content:
                print("✅ Found AWS_BEARER_TOKEN_BEDROCK in .env")
            else:
                print("❌ Missing AWS_BEARER_TOKEN_BEDROCK in .env")
                return False
    else:
        print("❌ .env file not found")
        return False
    
    print("\n🎉 All components are properly set up!")
    return True

def print_api_documentation():
    """Print API documentation for the menu image analysis endpoint"""
    
    print("""
📋 MENU IMAGE ANALYSIS API DOCUMENTATION
==========================================

🔗 Base URL: http://localhost:8000/api/v1/menu-image-analysis

📍 ENDPOINTS:

1. POST /analyze
   - Description: Analyze a single menu image and extract menu items
   - Content-Type: multipart/form-data
   - Parameters:
     * image (file): Menu image file (JPEG, PNG, WEBP, GIF, BMP)
     * business_id (form): ID of the business uploading the menu
     * auto_create_items (form, optional): Whether to automatically create menu items (default: true)
   - Response: MenuImageAnalysisResponse with extracted menu items
   - Max file size: 20MB
   - Authentication: Required (Bearer token)

2. POST /bulk-analyze
   - Description: Analyze multiple menu images in bulk
   - Content-Type: multipart/form-data
   - Parameters:
     * images (files): Up to 10 menu image files
     * business_id (form): ID of the business uploading the menus
     * auto_create_items (form, optional): Whether to automatically create menu items (default: true)
   - Response: Array of MenuImageAnalysisResponse
   - Authentication: Required (Bearer token)

3. GET /supported-formats
   - Description: Get supported image formats and limits
   - Response: JSON with supported formats and limits
   - Authentication: Not required

📊 RESPONSE FORMAT:
{
  "analysis_id": "uuid",
  "business_id": "string",
  "result": {
    "restaurant_info": {
      "restaurant_name": "string",
      "cuisine_type": "string"
    },
    "menu_items": [
      {
        "name": "string",
        "description": "string",
        "price": 12.99,
        "category": "string",
        "allergens": ["string"],
        "ingredients": ["string"],
        "modifiers": [
          {
            "type": "string",
            "options": [
              {
                "name": "string",
                "price": 0.0
              }
            ]
          }
        ],
        "combos": [
          {
            "name": "string",
            "includes": ["string"],
            "price": 15.99
          }
        ],
        "sizes": [
          {
            "name": "string",
            "price": 12.99
          }
        ]
      }
    ],
    "total_items": 5,
    "analysis_confidence": 0.9
  },
  "created_items": ["menu_item_id_1", "menu_item_id_2"],
  "status": "completed",
  "created_at": "2025-01-15T10:30:00"
}

🚀 EXAMPLE USAGE:

# Using curl to analyze a menu image
curl -X POST "http://localhost:8000/api/v1/menu-image-analysis/analyze" \\
  -H "Authorization: Bearer YOUR_TOKEN" \\
  -F "image=@path/to/menu.jpg" \\
  -F "business_id=your-business-id" \\
  -F "auto_create_items=true"

# Using Python requests
import requests

url = "http://localhost:8000/api/v1/menu-image-analysis/analyze"
headers = {"Authorization": "Bearer YOUR_TOKEN"}
files = {"image": open("menu.jpg", "rb")}
data = {
    "business_id": "your-business-id",
    "auto_create_items": True
}

response = requests.post(url, headers=headers, files=files, data=data)
result = response.json()

🔧 FEATURES:
- Extracts menu items with names, descriptions, prices
- Identifies categories (appetizer, main course, dessert, beverage)
- Detects allergens and ingredients
- Captures modifiers (sizes, spice levels, extras)
- Identifies combo meals and pricing
- Automatically creates menu items in database
- Supports bulk processing of multiple images
- Comprehensive error handling and validation

⚠️  REQUIREMENTS:
- Valid AWS Bedrock credentials configured
- Business ownership verification
- Supported image formats only
- Maximum file size: 20MB per image
- Authentication required for all endpoints
    """)

if __name__ == "__main__":
    print("🧪 Testing Menu Image Analysis Setup...")
    success = test_menu_image_analysis_setup()
    
    if success:
        print_api_documentation()
    else:
        print("\n❌ Setup incomplete. Please check the missing components.")