# Intelligent Ordering System

The Tably ordering system provides AI-powered ordering assistance with multilingual support, personalized recommendations, and seamless order processing. Built on the Strands framework with AWS Bedrock integration.

## Overview

### Core Features
- 🤖 **AI-Powered Order Assistance**: Intelligent help with placing and modifying orders
- 🌍 **Multilingual Support**: Order in 12+ languages with automatic translation
- 🎯 **Personalized Recommendations**: Tailored suggestions based on preferences and dietary needs
- 🔄 **Real-time Chat**: Streaming responses for immediate customer support
- 🛡️ **Dietary Safety**: Comprehensive allergen and dietary restriction handling
- 📱 **API Integration**: RESTful endpoints for easy frontend integration

### Architecture
The system consists of specialized agents orchestrated through an intelligent routing system:

1. **Ordering Assistant Agent**: Handles order taking, modifications, and customer service
2. **Recommendation Agent**: Provides personalized menu suggestions
3. **Translation Agent**: Processes multilingual orders and communications
4. **Orchestrator**: Intelligently routes requests to appropriate agents

## API Endpoints

All endpoints are prefixed with `/api/ordering/` and require authentication.

### 1. Order Assistant

**POST** `/api/ordering/order-assistant`

Get assistance with placing orders, order modifications, and order-related questions.

**Request:**
```json
{
  "customer_request": "I want to order a large Margherita pizza",
  "menu_data": "optional_json_menu_data",
  "order_context": "optional_current_order_context"
}
```

**Response:**
```json
{
  "response": "I'd be happy to help you order a large Margherita pizza...",
  "request_id": "order_20240115_103000",
  "timestamp": "2024-01-15T10:30:00Z",
  "agent_type": "ordering_assistant"
}
```

### 2. Personalized Recommendations

**POST** `/api/ordering/recommendations`

Get personalized menu recommendations based on customer preferences.

**Request:**
```json
{
  "customer_preferences": "I love spicy food and seafood",
  "menu_data": "optional_json_menu_data",
  "dietary_restrictions": "vegetarian, no nuts",
  "budget_range": "under $25",
  "occasion": "casual dinner"
}
```

**Response:**
```json
{
  "response": "Based on your preferences for spicy food...",
  "request_id": "rec_20240115_103000",
  "timestamp": "2024-01-15T10:30:00Z",
  "agent_type": "recommendation"
}
```

### 3. Translation Service

**POST** `/api/ordering/translate`

Translate customer messages for order processing.

**Request:**
```json
{
  "customer_message": "Hola, quiero pedir una pizza margherita",
  "source_language": "spanish",
  "target_language": "english"
}
```

**Response:**
```json
{
  "response": "Hello, I want to order a Margherita pizza...",
  "request_id": "trans_20240115_103000",
  "timestamp": "2024-01-15T10:30:00Z",
  "agent_type": "translation"
}
```

### 4. Multilingual Order Processing

**POST** `/api/ordering/multilingual-order`

Process orders in multiple languages with integrated translation and ordering assistance.

**Request:**
```json
{
  "customer_message": "Quiero pedir pasta con pollo y una ensalada",
  "menu_data": "optional_json_menu_data",
  "source_language": "spanish"
}
```

**Response:**
```json
{
  "response": "TRANSLATION: I want to order pasta with chicken and a salad...\n\nORDER ASSISTANCE: I'd be happy to help you order...",
  "request_id": "multi_20240115_103000",
  "timestamp": "2024-01-15T10:30:00Z",
  "agent_type": "multilingual_order"
}
```

### 5. Combined Recommendation & Ordering

**POST** `/api/ordering/order-recommendation-combo`

Get recommendations and ordering assistance in one request with optional translation.

**Request:**
```json
{
  "customer_preferences": "Quiero algo picante y sabroso",
  "menu_data": "optional_json_menu_data",
  "dietary_restrictions": "vegetarian",
  "language": "spanish"
}
```

### 6. Intelligent Chat

**POST** `/api/ordering/chat`

Chat with the intelligent ordering system using orchestrated agent routing.

**Request:**
```json
{
  "message": "I need help choosing something healthy for lunch",
  "context": "optional_context"
}
```

### 7. Streaming Chat

**POST** `/api/ordering/chat/stream`

Real-time streaming chat responses for immediate customer interaction.

**Request:**
```json
{
  "message": "¿Qué recomiendan para una cena romántica?",
  "context": "optional_context"
}
```

**Response:** Server-Sent Events (SSE)
```
data: {"content": "Para una cena romántica, recomiendo...", "type": "message"}
data: {"content": "[DONE]", "type": "done"}
```

### 8. Utility Endpoints

**GET** `/api/ordering/supported-languages`
- Returns list of supported languages for translation

**GET** `/api/ordering/order-flow-help`
- Returns help information about the ordering process

**GET** `/api/ordering/health`
- Health check for all ordering agents

## Supported Languages

The system supports the following languages:

| Language | Code | Native Name |
|----------|------|-------------|
| English | en | English |
| Spanish | es | Español |
| French | fr | Français |
| Italian | it | Italiano |
| German | de | Deutsch |
| Portuguese | pt | Português |
| Chinese | zh | 中文 |
| Japanese | ja | 日本語 |
| Korean | ko | 한국어 |
| Arabic | ar | العربية |
| Hindi | hi | हिंदी |
| Filipino/Tagalog | tl | Filipino/Tagalog |

## Agent Capabilities

### Ordering Assistant Agent
- **Order Taking**: Help customers select items, quantities, and customizations
- **Order Validation**: Ensure all necessary details are captured
- **Order Modification**: Handle changes, cancellations, and additions
- **Customer Service**: Answer questions and resolve issues
- **Upselling**: Suggest complementary items appropriately

### Recommendation Agent
- **Preference Analysis**: Understand customer tastes and preferences
- **Dietary Accommodation**: Handle vegetarian, vegan, gluten-free, and other needs
- **Occasion Matching**: Suggest appropriate items for different dining contexts
- **Budget Considerations**: Provide options within specified price ranges
- **Pairing Suggestions**: Recommend complete meal combinations

### Translation Agent
- **Language Detection**: Automatically identify source language
- **Accurate Translation**: Preserve meaning and context
- **Cultural Sensitivity**: Understand cultural dining preferences
- **Dietary Translation**: Accurately translate restrictions and allergies
- **Order Confirmation**: Ensure translation accuracy

## Usage Examples

### Basic Order (English)
```bash
curl -X POST "/api/ordering/order-assistant" \
  -H "Authorization: Bearer YOUR_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "customer_request": "I want to order a large pepperoni pizza and a Coke"
  }'
```

### Multilingual Order (Spanish)
```bash
curl -X POST "/api/ordering/multilingual-order" \
  -H "Authorization: Bearer YOUR_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "customer_message": "Hola, quiero pedir una pizza margherita grande y una coca cola",
    "source_language": "spanish"
  }'
```

### Personalized Recommendations
```bash
curl -X POST "/api/ordering/recommendations" \
  -H "Authorization: Bearer YOUR_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "customer_preferences": "I love spicy food and am vegetarian",
    "dietary_restrictions": "vegetarian, no nuts",
    "budget_range": "under $25"
  }'
```

### Streaming Chat
```bash
curl -X POST "/api/ordering/chat/stream" \
  -H "Authorization: Bearer YOUR_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "message": "What do you recommend for a romantic dinner?"
  }'
```

## Menu Data Format

The system accepts menu data in the following JSON format:

```json
{
  "restaurant_info": {
    "name": "Restaurant Name",
    "cuisine_type": "Italian",
    "location": "Downtown"
  },
  "menu_categories": ["Appetizers", "Pasta", "Pizza", "Salads"],
  "menu_items": [
    {
      "name": "Margherita Pizza",
      "category": "Pizza",
      "price": 18.99,
      "description": "Fresh tomato sauce, mozzarella, basil",
      "sizes": ["Medium", "Large"],
      "allergens": ["dairy", "gluten"],
      "dietary_info": ["vegetarian"],
      "ingredients": ["tomato sauce", "mozzarella", "basil"]
    }
  ]
}
```

## Error Handling

The system provides comprehensive error handling:

- **400 Bad Request**: Invalid request parameters
- **401 Unauthorized**: Missing or invalid authentication
- **500 Internal Server Error**: Agent processing errors

All errors include descriptive messages to help with debugging.

## Integration Guide

### Frontend Integration

1. **Initialize Authentication**
```javascript
const token = await getAuthToken();
const headers = {
  'Authorization': `Bearer ${token}`,
  'Content-Type': 'application/json'
};
```

2. **Simple Order Taking**
```javascript
const response = await fetch('/api/ordering/order-assistant', {
  method: 'POST',
  headers,
  body: JSON.stringify({
    customer_request: 'I want to order a pizza',
    menu_data: JSON.stringify(menuData)
  })
});
```

3. **Multilingual Support**
```javascript
const response = await fetch('/api/ordering/multilingual-order', {
  method: 'POST',
  headers,
  body: JSON.stringify({
    customer_message: 'Hola, quiero pedir una pizza',
    source_language: 'spanish'
  })
});
```

4. **Streaming Chat**
```javascript
const eventSource = new EventSource('/api/ordering/chat/stream');
eventSource.onmessage = (event) => {
  const data = JSON.parse(event.data);
  if (data.type === 'message') {
    displayMessage(data.content);
  }
};
```

### Mobile Integration

The API is designed to work seamlessly with mobile applications:

- **Voice Input**: Convert speech to text and send to appropriate endpoints
- **Offline Support**: Cache menu data for offline browsing
- **Push Notifications**: Integrate with order status updates

## Performance Considerations

- **Response Times**: Typical response times are 1-3 seconds
- **Rate Limiting**: Implemented to prevent abuse
- **Caching**: Menu data and common responses are cached
- **Scaling**: Built on AWS infrastructure for high availability

## Security Features

- **Authentication Required**: All endpoints require valid JWT tokens
- **Data Validation**: Input validation and sanitization
- **Error Handling**: Secure error messages without sensitive data
- **Audit Logging**: Complete logging for security monitoring

## Testing

Run the comprehensive test suite:

```bash
python app/agents/test_ordering_system.py
```

The test suite covers:
- Order taking in multiple languages
- Recommendation generation
- Translation accuracy
- Error handling
- Performance benchmarks

## Support

For technical support or feature requests:
1. Check the API documentation at `/docs`
2. Review the health check endpoint: `/api/ordering/health`
3. Contact the development team for advanced integrations

The ordering system is designed to provide a seamless, intelligent, and multilingual ordering experience that enhances customer satisfaction while reducing operational complexity.