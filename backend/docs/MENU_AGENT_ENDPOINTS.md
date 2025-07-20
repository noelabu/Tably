# Menu Agent API Endpoints

This document describes the Menu Agent API endpoints integrated with the Tably backend. The Menu Agent provides intelligent menu analysis, recommendations, and conversational interactions using AWS Bedrock and the Strands framework.

## Overview

The Menu Agent endpoints provide:
- **Intelligent Menu Analysis**: AI-powered menu image analysis with natural language processing
- **Conversational Interface**: Chat with the AI about menu items and recommendations
- **Dietary Recommendations**: Personalized suggestions based on dietary preferences and restrictions
- **Menu Search**: Intelligent search functionality for menu items
- **Allergen Information**: Detailed allergen analysis and safety information
- **Streaming Chat**: Real-time conversational responses

## Authentication

All endpoints require authentication using Bearer tokens. Include the token in the Authorization header:

```
Authorization: Bearer <your_token>
```

## Base URL

All endpoints are prefixed with `/api/menu-agent/`

## Endpoints

### 1. Health Check

**GET** `/api/menu-agent/health`

Check the health and availability of the menu agent service.

**Response:**
```json
{
  "status": "healthy",
  "timestamp": "2024-01-15T10:30:00Z",
  "agent_available": true,
  "test_response_length": 150
}
```

### 2. Chat with Menu Agent

**POST** `/api/menu-agent/chat`

Have a conversation with the menu agent about menu items, recommendations, and questions.

**Request Body:**
```json
{
  "query": "What vegetarian options are available?",
  "menu_data": "optional_json_string_with_menu_data"
}
```

**Response:**
```json
{
  "response": "Based on the menu, here are the vegetarian options available...",
  "query_id": "query_20240115_103000",
  "timestamp": "2024-01-15T10:30:00Z"
}
```

### 3. Streaming Chat

**POST** `/api/menu-agent/chat/stream`

Get real-time streaming responses from the menu agent.

**Request Body:**
```json
{
  "message": "Tell me about the pasta dishes",
  "menu_data": "optional_json_string_with_menu_data"
}
```

**Response:** Server-Sent Events (SSE)
```
data: {"content": "Based on the menu, here are the pasta dishes..."}
data: {"content": "[DONE]"}
```

### 4. Analyze Menu Image

**POST** `/api/menu-agent/analyze-image`

Analyze a menu image using the AI agent.

**Request:**
- **Content-Type:** `multipart/form-data`
- **image:** Menu image file (JPEG, PNG, WEBP, GIF, BMP)
- **Max file size:** 20MB

**Response:**
```json
{
  "analysis_status": "success",
  "restaurant_info": {
    "name": "Restaurant Name",
    "cuisine_type": "Italian"
  },
  "menu_categories": ["Appetizers", "Pasta", "Pizza"],
  "total_items": 15,
  "menu_items": [
    {
      "name": "Margherita Pizza",
      "category": "Pizza",
      "price": 15.99,
      "description": "Fresh tomato sauce, mozzarella, basil",
      "allergens": ["dairy", "gluten"],
      "dietary_info": ["vegetarian"]
    }
  ],
  "confidence_score": 0.95
}
```

### 5. Get Menu Recommendations

**POST** `/api/menu-agent/recommendations`

Get personalized menu recommendations based on dietary preferences.

**Request Body:**
```json
{
  "dietary_preferences": "vegetarian, gluten-free, no nuts",
  "menu_data": "optional_json_string_with_menu_data"
}
```

**Response:**
```json
{
  "response": "Based on your dietary preferences, I recommend...",
  "query_id": "recommendations_20240115_103000",
  "timestamp": "2024-01-15T10:30:00Z"
}
```

### 6. Search Menu Items

**POST** `/api/menu-agent/search`

Search for specific menu items or ingredients.

**Request Body:**
```json
{
  "search_term": "pasta",
  "menu_data": "optional_json_string_with_menu_data"
}
```

**Response:**
```json
{
  "response": "Here are the pasta dishes I found...",
  "query_id": "search_20240115_103000",
  "timestamp": "2024-01-15T10:30:00Z"
}
```

### 7. Get Allergen Information

**POST** `/api/menu-agent/allergen-info`

Get detailed allergen information for menu items.

**Request Body:**
```json
{
  "allergen": "dairy",
  "menu_data": "optional_json_string_with_menu_data"
}
```

**Response:**
```json
{
  "response": "Here's the allergen information for dairy...",
  "query_id": "allergen_20240115_103000",
  "timestamp": "2024-01-15T10:30:00Z"
}
```

### 8. Analyze and Chat

**POST** `/api/menu-agent/analyze-and-chat`

Analyze a menu image and immediately ask questions about it.

**Request:**
- **Content-Type:** `multipart/form-data`
- **image:** Menu image file
- **query:** Question about the menu

**Response:**
```json
{
  "analysis_result": {
    "menu_items": [...],
    "restaurant_info": {...}
  },
  "chat_response": "Answer to your question...",
  "query": "Your original question",
  "timestamp": "2024-01-15T10:30:00Z"
}
```

## Enhanced Menu Image Analysis Endpoints

### 9. Extract with Intelligence

**POST** `/api/menu-image-analysis/extract-with-intelligence`

Enhanced version of the original extract endpoint with AI intelligence.

**Request:**
- **Content-Type:** `multipart/form-data`
- **image:** Menu image file
- **query:** Optional question about the menu

**Response:** Same as original extract endpoint, but with optional intelligence_response in restaurant_info

### 10. Analyze with Recommendations

**POST** `/api/menu-image-analysis/analyze-with-recommendations`

Full analysis with database creation and intelligent recommendations.

**Request:**
- **Content-Type:** `multipart/form-data`
- **image:** Menu image file
- **business_id:** Business ID
- **dietary_preferences:** Optional dietary preferences
- **auto_create_items:** Whether to create items in database

**Response:**
```json
{
  "analysis_id": "uuid",
  "business_id": "business_id",
  "result": {
    "menu_items": [...],
    "restaurant_info": {...}
  },
  "created_items": ["item_id1", "item_id2"],
  "recommendations": "AI recommendations based on preferences",
  "status": "completed",
  "created_at": "2024-01-15T10:30:00Z"
}
```

## Menu Data Format

The `menu_data` parameter accepts a JSON string with the following structure:

```json
{
  "restaurant_info": {
    "name": "Restaurant Name",
    "cuisine_type": "Italian",
    "address": "123 Main St"
  },
  "menu_categories": ["Appetizers", "Pasta", "Pizza", "Desserts"],
  "menu_items": [
    {
      "name": "Item Name",
      "category": "Category",
      "price": 12.99,
      "description": "Item description",
      "allergens": ["dairy", "gluten"],
      "dietary_info": ["vegetarian", "spicy"],
      "ingredients": ["ingredient1", "ingredient2"]
    }
  ]
}
```

## Error Handling

All endpoints return appropriate HTTP status codes:

- **200**: Success
- **400**: Bad Request (invalid parameters)
- **401**: Unauthorized (invalid token)
- **403**: Forbidden (insufficient permissions)
- **500**: Internal Server Error

**Error Response Format:**
```json
{
  "detail": "Error message describing what went wrong"
}
```

## Usage Examples

### Example 1: Simple Chat
```bash
curl -X POST "http://localhost:8000/api/menu-agent/chat" \
  -H "Authorization: Bearer YOUR_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "query": "What are your most popular appetizers?"
  }'
```

### Example 2: Menu Analysis
```bash
curl -X POST "http://localhost:8000/api/menu-agent/analyze-image" \
  -H "Authorization: Bearer YOUR_TOKEN" \
  -F "image=@menu.jpg"
```

### Example 3: Get Recommendations
```bash
curl -X POST "http://localhost:8000/api/menu-agent/recommendations" \
  -H "Authorization: Bearer YOUR_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "dietary_preferences": "vegan, gluten-free"
  }'
```

## Integration with Frontend

The endpoints are designed to be easily integrated with the frontend application:

1. **Use the streaming endpoint** for real-time chat experiences
2. **Upload menu images** for analysis and immediate questioning
3. **Get recommendations** based on user preferences
4. **Search functionality** for finding specific items
5. **Allergen safety** for users with dietary restrictions

## Security Notes

- All endpoints require authentication
- File uploads are limited to 20MB
- Only image files are accepted for analysis
- Rate limiting may be applied
- Business ownership is verified for database operations

## Support

For issues or questions about the Menu Agent API, please refer to the main documentation or contact the development team.