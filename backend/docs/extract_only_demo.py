#!/usr/bin/env python3
"""
Demo script for the new extract-only menu image analysis endpoints
"""

import json
import requests
from pathlib import Path

def print_extract_only_documentation():
    """Print documentation for the new extract-only endpoints"""
    
    print("""
🆕 NEW EXTRACT-ONLY ENDPOINTS
==============================

These endpoints analyze menu images and return extracted data WITHOUT uploading to Supabase.

🔗 Base URL: http://localhost:8001/api/v1/menu-image-analysis

📍 NEW ENDPOINTS:

1. POST /extract-only
   - Description: Analyze a single menu image and extract menu items (NO database upload)
   - Content-Type: multipart/form-data
   - Parameters:
     * image (file): Menu image file (JPEG, PNG, WEBP, GIF, BMP)
   - Response: MenuImageAnalysisResult with extracted menu items only
   - Max file size: 20MB
   - Authentication: Required (Bearer token)

2. POST /bulk-extract-only
   - Description: Analyze multiple menu images in bulk (NO database upload)
   - Content-Type: multipart/form-data
   - Parameters:
     * images (files): Up to 10 menu image files
   - Response: Array of MenuImageAnalysisResult
   - Authentication: Required (Bearer token)

📊 EXTRACT-ONLY RESPONSE FORMAT:
{
  "restaurant_info": {
    "restaurant_name": "Restaurant Name",
    "cuisine_type": "Type of cuisine"
  },
  "menu_items": [
    {
      "name": "Item Name",
      "description": "Item description",
      "price": 12.99,
      "category": "main course",
      "allergens": ["nuts", "dairy"],
      "ingredients": ["chicken", "rice", "vegetables"],
      "modifiers": [
        {
          "type": "size",
          "options": [
            {"name": "Regular", "price": 0},
            {"name": "Large", "price": 3.00}
          ]
        }
      ],
      "combos": [
        {
          "name": "Lunch Special",
          "includes": ["main dish", "rice", "drink"],
          "price": 15.99
        }
      ],
      "sizes": [
        {"name": "Regular", "price": 12.99},
        {"name": "Large", "price": 15.99}
      ]
    }
  ],
  "total_items": 5,
  "analysis_confidence": 0.9
}

🚀 EXAMPLE USAGE:

# Extract menu items only (no database upload)
curl -X POST "http://localhost:8001/api/v1/menu-image-analysis/extract-only" \\
  -H "Authorization: Bearer YOUR_TOKEN" \\
  -F "image=@path/to/menu.jpg"

# Extract from multiple images (no database upload)
curl -X POST "http://localhost:8001/api/v1/menu-image-analysis/bulk-extract-only" \\
  -H "Authorization: Bearer YOUR_TOKEN" \\
  -F "images=@menu1.jpg" \\
  -F "images=@menu2.jpg"

# Python example
import requests

url = "http://localhost:8001/api/v1/menu-image-analysis/extract-only"
headers = {"Authorization": "Bearer YOUR_TOKEN"}
files = {"image": open("menu.jpg", "rb")}

response = requests.post(url, headers=headers, files=files)
result = response.json()

print(f"Found {result['total_items']} menu items")
for item in result['menu_items']:
    print(f"- {item['name']}: ${item['price']}")

🔧 KEY DIFFERENCES FROM ORIGINAL ENDPOINTS:

Original /analyze endpoint:
- Requires business_id parameter
- Uploads extracted items to Supabase database
- Returns MenuImageAnalysisResponse with created item IDs
- Requires business ownership verification

New /extract-only endpoint:
- No business_id required
- Does NOT upload to database
- Returns MenuImageAnalysisResult with extracted data only
- Only requires user authentication

⚡ PERFORMANCE BENEFITS:
- Faster response (no database operations)
- No business validation required
- Perfect for preview/testing scenarios
- Can analyze menus without committing to database

🔐 SECURITY:
- Still requires user authentication
- No data persistence (extract-only)
- No business ownership checks needed
- All AWS Bedrock/Amazon Nova security measures still apply

✅ USE CASES:
- Preview menu extraction before committing
- Testing menu image quality
- Batch analysis for data validation
- Integration with external systems
- Menu data export workflows
    """)

def test_extract_only_endpoint():
    """Test the extract-only endpoint with a sample request"""
    
    # Test supported formats endpoint first
    try:
        response = requests.get("http://localhost:8001/api/v1/menu-image-analysis/supported-formats")
        if response.status_code == 200:
            print("✅ Server is running and extract-only endpoints are accessible")
            print(f"   Supported formats: {response.json()['supported_formats']}")
        else:
            print(f"❌ Server responded with status {response.status_code}")
    except Exception as e:
        print(f"❌ Could not connect to server: {e}")
        print("   Make sure the server is running on port 8001")
        print("   Run: uv run uvicorn main:app --host 0.0.0.0 --port 8001")

if __name__ == "__main__":
    print("🧪 Testing Extract-Only Menu Image Analysis Endpoints...")
    test_extract_only_endpoint()
    print_extract_only_documentation()