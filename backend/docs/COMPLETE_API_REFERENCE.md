# Complete Tably API Reference

This document provides a comprehensive reference for all Tably API endpoints, organized by functionality.

## Base URL

All API endpoints are accessible at: `https://api.tably.com` (or `http://localhost:8000` for development)

## Authentication

All endpoints require authentication unless otherwise specified. Include the JWT token in the Authorization header:

```
Authorization: Bearer <your_jwt_token>
```

## Table of Contents

1. [Authentication Endpoints](#authentication-endpoints)
2. [Menu Agent Endpoints](#menu-agent-endpoints)
3. [Ordering Agents Endpoints](#ordering-agents-endpoints)
4. [Order Management Endpoints](#order-management-endpoints)
5. [Customer Preferences Endpoints](#customer-preferences-endpoints)
6. [Order Tracking Endpoints](#order-tracking-endpoints)
7. [Menu Analysis Endpoints](#menu-analysis-endpoints)
8. [WebSocket Endpoints](#websocket-endpoints)
9. [Utility Endpoints](#utility-endpoints)

---

## Authentication Endpoints

### Base Path: `/api/auth/`

#### Login
- **POST** `/login`
- **Request Body:**
  ```json
  {
    "email": "user@example.com",
    "password": "password123"
  }
  ```
- **Response:**
  ```json
  {
    "access_token": "jwt_token_here",
    "token_type": "bearer",
    "user": {
      "id": "user_id",
      "email": "user@example.com",
      "name": "User Name"
    }
  }
  ```

#### Register
- **POST** `/register`
- **Request Body:**
  ```json
  {
    "email": "user@example.com",
    "password": "password123",
    "name": "User Name"
  }
  ```

---

## Menu Agent Endpoints

### Base Path: `/api/menu-agent/`

#### Health Check
- **GET** `/health`
- **Response:**
  ```json
  {
    "status": "healthy",
    "timestamp": "2024-01-15T10:30:00Z",
    "agent_available": true
  }
  ```

#### Chat with Menu Agent
- **POST** `/chat`
- **Request Body:**
  ```json
  {
    "query": "What vegetarian options do you have?",
    "menu_data": "optional_json_menu_data"
  }
  ```
- **Response:**
  ```json
  {
    "response": "Based on our menu, here are the vegetarian options...",
    "query_id": "query_20240115_103000",
    "timestamp": "2024-01-15T10:30:00Z"
  }
  ```

#### Streaming Chat
- **POST** `/chat/stream`
- **Request Body:**
  ```json
  {
    "message": "Tell me about your pasta dishes",
    "menu_data": "optional_json_menu_data"
  }
  ```
- **Response:** Server-Sent Events (SSE)

#### Analyze Menu Image
- **POST** `/analyze-image`
- **Request:** `multipart/form-data`
  - `image`: Image file (max 20MB)
- **Response:**
  ```json
  {
    "analysis_status": "success",
    "restaurant_info": {},
    "menu_items": [],
    "total_items": 15,
    "confidence_score": 0.95
  }
  ```

#### Get Menu Recommendations
- **POST** `/recommendations`
- **Request Body:**
  ```json
  {
    "dietary_preferences": "vegetarian, gluten-free",
    "menu_data": "optional_json_menu_data"
  }
  ```

#### Search Menu Items
- **POST** `/search`
- **Request Body:**
  ```json
  {
    "search_term": "pizza",
    "menu_data": "optional_json_menu_data"
  }
  ```

#### Get Allergen Information
- **POST** `/allergen-info`
- **Request Body:**
  ```json
  {
    "allergen": "dairy",
    "menu_data": "optional_json_menu_data"
  }
  ```

#### Analyze and Chat
- **POST** `/analyze-and-chat`
- **Request:** `multipart/form-data`
  - `image`: Menu image file
  - `query`: Question about the menu

---

## Ordering Agents Endpoints

### Base Path: `/api/ordering/`

#### Order Assistant
- **POST** `/order-assistant`
- **Request Body:**
  ```json
  {
    "customer_request": "I want to order a large pizza",
    "menu_data": "optional_json_menu_data",
    "order_context": "optional_current_order_context"
  }
  ```
- **Response:**
  ```json
  {
    "response": "I'd be happy to help you order a large pizza...",
    "request_id": "order_20240115_103000",
    "timestamp": "2024-01-15T10:30:00Z",
    "agent_type": "ordering_assistant"
  }
  ```

#### Get Recommendations
- **POST** `/recommendations`
- **Request Body:**
  ```json
  {
    "customer_preferences": "I love spicy food",
    "dietary_restrictions": "vegetarian",
    "budget_range": "under $25",
    "occasion": "casual dinner"
  }
  ```

#### Translate Message
- **POST** `/translate`
- **Request Body:**
  ```json
  {
    "customer_message": "Hola, quiero pedir una pizza",
    "source_language": "spanish",
    "target_language": "english"
  }
  ```

#### Process Multilingual Order
- **POST** `/multilingual-order`
- **Request Body:**
  ```json
  {
    "customer_message": "Quiero pedir pasta con pollo",
    "menu_data": "optional_json_menu_data",
    "source_language": "spanish"
  }
  ```

#### Combined Order & Recommendations
- **POST** `/order-recommendation-combo`
- **Request Body:**
  ```json
  {
    "customer_preferences": "Quiero algo picante",
    "dietary_restrictions": "vegetarian",
    "language": "spanish"
  }
  ```

#### Chat with Ordering System
- **POST** `/chat`
- **Request Body:**
  ```json
  {
    "message": "I need help choosing lunch",
    "context": "optional_context"
  }
  ```

#### Streaming Chat
- **POST** `/chat/stream`
- **Request Body:**
  ```json
  {
    "message": "¿Qué recomiendan para una cena romántica?",
    "context": "optional_context"
  }
  ```

#### Get Supported Languages
- **GET** `/supported-languages`
- **Response:**
  ```json
  {
    "supported_languages": [
      {"code": "en", "name": "English", "native": "English"},
      {"code": "es", "name": "Spanish", "native": "Español"}
    ]
  }
  ```

#### Get Order Flow Help
- **GET** `/order-flow-help`

#### Health Check
- **GET** `/health`

---

## Order Management Endpoints

### Base Path: `/api/orders/`

#### Create Order
- **POST** `/create`
- **Request Body:**
  ```json
  {
    "business_id": "business_123",
    "customer_info": {
      "user_id": "user_123",
      "name": "John Doe",
      "email": "john@example.com",
      "preferred_language": "english"
    },
    "order_type": "dine_in",
    "items": [
      {
        "menu_item_id": "item_1",
        "name": "Pizza Margherita",
        "quantity": 1,
        "unit_price": 18.99,
        "total_price": 18.99
      }
    ],
    "delivery_info": {
      "address": "123 Main St",
      "city": "New York",
      "postal_code": "10001"
    }
  }
  ```
- **Response:**
  ```json
  {
    "order": {
      "id": "order_123",
      "status": "pending",
      "total_amount": 20.51,
      "created_at": "2024-01-15T10:30:00Z"
    },
    "agent_response": "Your order has been placed successfully...",
    "recommendations": []
  }
  ```

#### List Orders
- **GET** `/list`
- **Query Parameters:**
  - `status`: Filter by order status
  - `order_type`: Filter by order type
  - `page`: Page number (default: 1)
  - `per_page`: Items per page (default: 10)
- **Response:**
  ```json
  {
    "orders": [],
    "total_count": 25,
    "page": 1,
    "per_page": 10
  }
  ```

#### Get Order
- **GET** `/{order_id}`
- **Response:**
  ```json
  {
    "order": {
      "id": "order_123",
      "status": "confirmed",
      "items": [],
      "total_amount": 20.51
    },
    "agent_response": "Your order is being prepared..."
  }
  ```

#### Update Order
- **PUT** `/{order_id}`
- **Request Body:**
  ```json
  {
    "status": "confirmed",
    "items": [],
    "special_instructions": "Extra cheese"
  }
  ```

#### Cancel Order
- **DELETE** `/{order_id}`
- **Response:**
  ```json
  {
    "message": "Order cancelled successfully",
    "agent_response": "Your order has been cancelled..."
  }
  ```

#### Chat About Order
- **POST** `/{order_id}/chat`
- **Request Body:**
  ```json
  {
    "message": "When will my order be ready?"
  }
  ```

#### Track Order
- **GET** `/{order_id}/track`
- **Response:**
  ```json
  {
    "tracking_info": {
      "order_id": "order_123",
      "status": "preparing",
      "progress": 50,
      "timeline": [],
      "next_update": "2024-01-15T10:45:00Z"
    },
    "agent_message": "Your order is currently being prepared..."
  }
  ```

### Shopping Cart Endpoints

#### Add to Cart
- **POST** `/cart/add`
- **Query Parameters:**
  - `session_id`: Cart session ID
- **Request Body:**
  ```json
  {
    "menu_item_id": "item_1",
    "name": "Pizza Margherita",
    "quantity": 1,
    "unit_price": 18.99,
    "modifications": []
  }
  ```

#### Get Cart
- **GET** `/cart/{session_id}`
- **Response:**
  ```json
  {
    "cart": {
      "session_id": "cart_123",
      "items": [],
      "total_quantity": 3
    },
    "subtotal": 45.97,
    "item_count": 2
  }
  ```

#### Checkout Cart
- **POST** `/cart/{session_id}/checkout`
- **Request Body:**
  ```json
  {
    "order_type": "delivery"
  }
  ```

#### Get Order Analytics
- **GET** `/analytics/summary`
- **Query Parameters:**
  - `start_date`: Start date for analytics
  - `end_date`: End date for analytics
- **Response:**
  ```json
  {
    "total_orders": 25,
    "total_revenue": 512.75,
    "average_order_value": 20.51,
    "popular_items": [],
    "customer_satisfaction": 4.2
  }
  ```

---

## Customer Preferences Endpoints

### Base Path: `/api/customer/`

#### Get Customer Preferences
- **GET** `/preferences`
- **Response:**
  ```json
  {
    "user_id": "user_123",
    "favorite_items": ["item_1", "item_2"],
    "dietary_restrictions": ["vegetarian", "gluten_free"],
    "preferred_language": "english",
    "spice_level": "medium",
    "budget_range": "$15-25"
  }
  ```

#### Update Customer Preferences
- **PUT** `/preferences`
- **Request Body:**
  ```json
  {
    "favorite_items": ["item_1", "item_3"],
    "dietary_restrictions": ["vegetarian"],
    "preferred_language": "spanish",
    "spice_level": "hot",
    "budget_range": "$20-30"
  }
  ```

#### Add Favorite Item
- **POST** `/preferences/favorite/{item_id}`
- **Response:**
  ```json
  {
    "message": "Item added to favorites",
    "favorite_items": ["item_1", "item_2", "item_3"],
    "agent_response": "Great choice! This item has been added to your favorites..."
  }
  ```

#### Remove Favorite Item
- **DELETE** `/preferences/favorite/{item_id}`

#### Get Personalized Recommendations
- **GET** `/preferences/recommendations`
- **Query Parameters:**
  - `menu_data`: Optional menu data
  - `occasion`: Special occasion context
- **Response:**
  ```json
  {
    "recommendations": "Based on your preferences...",
    "based_on": {
      "dietary_restrictions": ["vegetarian"],
      "spice_level": "medium",
      "favorite_items_count": 3
    }
  }
  ```

#### Update Dietary Restrictions
- **POST** `/preferences/dietary-restrictions`
- **Request Body:**
  ```json
  {
    "dietary_restrictions": ["vegetarian", "gluten_free", "nut_free"]
  }
  ```

#### Update Preferred Language
- **POST** `/preferences/language`
- **Request Body:**
  ```json
  {
    "language": "spanish"
  }
  ```

### Agent Session Endpoints

#### Get Agent Sessions
- **GET** `/agent-sessions`
- **Query Parameters:**
  - `limit`: Number of sessions to retrieve (default: 10)

#### Create Agent Session
- **POST** `/agent-sessions`
- **Request Body:**
  ```json
  {
    "business_id": "business_123",
    "language": "english"
  }
  ```

#### Interact with Agent
- **POST** `/agent-sessions/{session_id}/interact`
- **Request Body:**
  ```json
  {
    "message": "I need help with my order"
  }
  ```

#### Get Agent Session
- **GET** `/agent-sessions/{session_id}`

#### Close Agent Session
- **DELETE** `/agent-sessions/{session_id}`

#### Get Preferences Summary
- **GET** `/preferences/summary`
- **Response:**
  ```json
  {
    "preferences": {},
    "activity_summary": {
      "total_sessions": 5,
      "total_interactions": 23,
      "favorite_items_count": 3,
      "dietary_restrictions_count": 2
    }
  }
  ```

---

## Order Tracking Endpoints

### Base Path: `/api/tracking/`

#### Get Order Status
- **GET** `/orders/{order_id}/status`
- **Response:**
  ```json
  {
    "order_id": "order_123",
    "status": "preparing",
    "progress_percentage": 50,
    "estimated_ready_time": "2024-01-15T10:45:00Z",
    "agent_update": "Your order is currently being prepared...",
    "timeline": []
  }
  ```

#### Get Detailed Tracking
- **GET** `/orders/{order_id}/tracking`
- **Query Parameters:**
  - `include_predictions`: Include AI predictions (default: false)
- **Response:**
  ```json
  {
    "order_id": "order_123",
    "current_status": "preparing",
    "progress_percentage": 50,
    "timeline": [],
    "estimated_times": {
      "ready_time": "2024-01-15T10:45:00Z",
      "completion_time": "2024-01-15T11:00:00Z"
    },
    "items_status": [],
    "ai_predictions": "Based on current kitchen load..."
  }
  ```

#### Update Order Status
- **POST** `/orders/{order_id}/update-status`
- **Request Body:**
  ```json
  {
    "order_id": "order_123",
    "status": "ready",
    "message": "Order is ready for pickup",
    "estimated_ready_time": "2024-01-15T10:45:00Z"
  }
  ```

#### Get Delivery Tracking
- **GET** `/orders/{order_id}/delivery-tracking`
- **Response:**
  ```json
  {
    "order_id": "order_123",
    "delivery_status": "out_for_delivery",
    "delivery_address": "123 Main St",
    "driver_info": {
      "name": "John Doe",
      "phone": "+1-555-0199",
      "vehicle": "Honda Civic - ABC 123"
    },
    "location_updates": []
  }
  ```

#### Get Order Notifications
- **GET** `/orders/{order_id}/notifications`
- **Response:**
  ```json
  {
    "order_id": "order_123",
    "notifications": [
      {
        "id": "notif_1",
        "type": "order_confirmed",
        "message": "Your order has been confirmed",
        "timestamp": "2024-01-15T10:32:00Z",
        "read": true
      }
    ],
    "unread_count": 1
  }
  ```

#### Submit Order Feedback
- **POST** `/orders/{order_id}/feedback`
- **Query Parameters:**
  - `rating`: Rating from 1 to 5
  - `comment`: Optional feedback comment
- **Response:**
  ```json
  {
    "message": "Feedback submitted successfully",
    "feedback": {
      "order_id": "order_123",
      "rating": 5,
      "comment": "Great food!",
      "timestamp": "2024-01-15T11:00:00Z"
    },
    "agent_response": "Thank you for your feedback..."
  }
  ```

---

## Menu Analysis Endpoints

### Base Path: `/api/menu-image-analysis/`

#### Extract Menu Items Only
- **POST** `/extract-only`
- **Request:** `multipart/form-data`
  - `image`: Menu image file
- **Response:**
  ```json
  {
    "restaurant_info": {},
    "menu_items": [],
    "total_items": 15,
    "analysis_confidence": 0.9
  }
  ```

#### Analyze Menu Image
- **POST** `/analyze`
- **Request:** `multipart/form-data`
  - `image`: Menu image file
  - `business_id`: Business ID
  - `auto_create_items`: Boolean (default: true)
- **Response:**
  ```json
  {
    "analysis_id": "analysis_123",
    "business_id": "business_123",
    "result": {},
    "created_items": ["item_1", "item_2"],
    "status": "completed"
  }
  ```

#### Extract with Intelligence
- **POST** `/extract-with-intelligence`
- **Request:** `multipart/form-data`
  - `image`: Menu image file
  - `query`: Optional question about the menu

#### Analyze with Recommendations
- **POST** `/analyze-with-recommendations`
- **Request:** `multipart/form-data`
  - `image`: Menu image file
  - `business_id`: Business ID
  - `dietary_preferences`: Optional dietary preferences
  - `auto_create_items`: Boolean (default: true)

#### Bulk Extract Only
- **POST** `/bulk-extract-only`
- **Request:** `multipart/form-data`
  - `images`: Multiple image files (max 10)

#### Bulk Analyze
- **POST** `/bulk-analyze`
- **Request:** `multipart/form-data`
  - `images`: Multiple image files (max 10)
  - `business_id`: Business ID
  - `auto_create_items`: Boolean (default: true)

#### Get Supported Formats
- **GET** `/supported-formats`
- **Response:**
  ```json
  {
    "supported_formats": ["JPEG", "PNG", "WEBP", "GIF", "BMP"],
    "max_file_size": "20MB",
    "max_dimensions": "2048x2048",
    "recommended_formats": ["JPEG", "PNG"]
  }
  ```

---

## WebSocket Endpoints

### Real-time Order Tracking
- **WebSocket** `/api/tracking/orders/{order_id}/track-live`
- **Connection:** `ws://localhost:8000/api/tracking/orders/order_123/track-live`
- **Messages:**
  ```json
  {
    "type": "status_update",
    "order_id": "order_123",
    "status": "preparing",
    "progress": 50,
    "timestamp": "2024-01-15T10:30:00Z"
  }
  ```

---

## Utility Endpoints

### Health Check
- **GET** `/health`
- **Response:**
  ```json
  {
    "status": "healthy",
    "timestamp": "2024-01-15T10:30:00Z",
    "version": "1.0.0"
  }
  ```

### API Documentation
- **GET** `/docs`
- Interactive API documentation (Swagger UI)

### API Schema
- **GET** `/openapi.json`
- OpenAPI schema definition

---

## Error Responses

All endpoints return consistent error responses:

```json
{
  "detail": "Error message describing what went wrong"
}
```

### Common HTTP Status Codes

- **200**: Success
- **201**: Created
- **400**: Bad Request
- **401**: Unauthorized
- **403**: Forbidden
- **404**: Not Found
- **422**: Validation Error
- **500**: Internal Server Error

---

## Rate Limiting

API endpoints are rate-limited to prevent abuse:

- **Authentication endpoints**: 5 requests per minute
- **General endpoints**: 100 requests per minute
- **Streaming endpoints**: 10 connections per user

---

## SDKs and Libraries

### Python SDK
```python
from tably_sdk import TablyClient

client = TablyClient(api_key="your_api_key")
order = client.orders.create(order_data)
```

### JavaScript SDK
```javascript
import { TablyClient } from 'tably-sdk';

const client = new TablyClient({ apiKey: 'your_api_key' });
const order = await client.orders.create(orderData);
```

---

## Support

- **Documentation**: https://docs.tably.com
- **Support Email**: support@tably.com
- **GitHub Issues**: https://github.com/tably/api/issues
- **Status Page**: https://status.tably.com

---

## Changelog

### Version 1.0.0 (Current)
- Initial release with full ordering system
- Multi-language support
- AI-powered recommendations
- Real-time tracking
- WebSocket support

For the latest updates, check the [API Changelog](https://docs.tably.com/changelog).