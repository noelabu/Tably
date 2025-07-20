# Voice-to-Voice Ordering Assistant

A complete voice ordering system built with Strand agents, Amazon Bedrock Nova models, and Pipecat for real-time audio streaming.

## Overview

This system enables customers to place food orders through natural voice conversations. The assistant can:

- Retrieve menu items from Supabase based on business_id
- Help customers browse and search the menu
- Add/remove items from orders with quantities and special instructions  
- Calculate order totals
- Confirm and place orders
- Handle customer information collection

## Architecture

### Core Components

1. **VoiceOrderingAgent** (`app/agents/voice_ordering_agent.py`)
   - Strands agent powered by Amazon Nova Sonic model
   - Tool-enabled for menu retrieval and order management
   - Natural conversation handling

2. **VoiceStreamingService** (`app/services/voice_streaming_service.py`)
   - Pipecat integration for real-time audio streaming
   - Daily.co room management for voice sessions
   - Amazon STT/TTS services

3. **Voice API Endpoints** (`app/api/endpoints/voice_ordering.py`)
   - RESTful API for voice session management
   - Text-based ordering fallback
   - Session monitoring and cleanup

### Technology Stack

- **Strand Agents**: AI agent framework with tool capabilities
- **Amazon Bedrock Nova Sonic**: Fast, efficient model for voice applications
- **Pipecat**: Real-time audio streaming pipeline
- **Daily.co**: WebRTC infrastructure for voice sessions
- **Amazon STT/TTS**: Speech-to-text and text-to-speech services
- **Supabase**: Database for menu items and order storage

## Setup

### Dependencies

The required dependencies are already added to `pyproject.toml`:

```toml
dependencies = [
    # ... existing dependencies
    "pipecat-ai>=0.0.40",
    # ... rest
]
```

### Environment Variables

Add these to your `.env` file:

```env
# AWS Credentials (for Bedrock and STT/TTS)
AWS_ACCESS_KEY_ID=your_aws_access_key
AWS_SECRET_ACCESS_KEY=your_aws_secret_key
AWS_REGION=us-east-1

# Daily.co API (for voice sessions)
DAILY_API_KEY=your_daily_api_key
DAILY_API_URL=https://api.daily.co/v1

# Supabase (already configured)
SUPABASE_URL=your_supabase_url
SUPABASE_KEY=your_supabase_key
```

### Installation

1. Install dependencies:
```bash
cd backend
pip install -e .
```

2. Run the demo:
```bash
python app/agents/voice_demo.py [business_id]
```

## API Usage

### Create Voice Session

```bash
POST /api/v1/voice-ordering/sessions
Content-Type: application/json

{
    "business_id": "your-business-id",
    "customer_name": "John Doe"  # optional
}
```

Response:
```json
{
    "session_id": "uuid-string",
    "room_url": "https://domain.daily.co/room-name",
    "token": "daily-room-token",
    "message": "Voice ordering session created successfully"
}
```

### Text-based Ordering (Fallback)

```bash
POST /api/v1/voice-ordering/text-order
Content-Type: application/json

{
    "business_id": "your-business-id",
    "message": "I'd like to order a pizza",
    "session_id": "optional-session-id"
}
```

### Session Management

```bash
# Get session info
GET /api/v1/voice-ordering/sessions/{session_id}

# End session
DELETE /api/v1/voice-ordering/sessions/{session_id}

# List all sessions (admin)
GET /api/v1/voice-ordering/sessions

# Health check
GET /api/v1/voice-ordering/health
```

## Agent Tools

The VoiceOrderingAgent has the following built-in tools:

### Menu Tools
- `get_menu_items(category?)`: Get all menu items, optionally filtered by category
- `search_menu_items(search_term)`: Search menu items by name/description

### Order Management Tools  
- `add_item_to_order(item_name, quantity, special_instructions?)`: Add items to current order
- `remove_item_from_order(item_name, quantity?)`: Remove items from order
- `view_current_order()`: Show current order with totals
- `calculate_order_total()`: Get order total

### Order Finalization
- `confirm_order(customer_name, customer_phone?, special_requests?)`: Place the order
- `get_business_hours()`: Get restaurant hours

## Example Conversations

### Menu Browsing
```
Customer: "What do you have for appetizers?"
Assistant: "Here are our available appetizers:
- Buffalo Wings - $12.99 - Crispy chicken wings with buffalo sauce
- Mozzarella Sticks - $8.99 - Breaded mozzarella with marinara
- Nachos Supreme - $10.99 - Loaded nachos with cheese and jalapeños"
```

### Ordering Flow
```
Customer: "I'd like two buffalo wings and a pizza"
Assistant: "Great! I've added 2 Buffalo Wings to your order for $25.98. 
I found several pizzas on our menu: Margherita Pizza, Pepperoni Pizza, Supreme Pizza. 
Which pizza would you like?"

Customer: "The pepperoni pizza, large size"
Assistant: "Perfect! I've added 1 Large Pepperoni Pizza to your order for $16.99. 
Your current total is $42.97. Would you like to add anything else?"

Customer: "No, that's it. My name is John Smith"
Assistant: "Excellent! Your order has been confirmed and placed. 
Your order number is ORD-123456. Thank you, John! We'll have your order ready soon."
```

## Voice Session Flow

1. **Session Creation**: Client creates voice session via API
2. **Room Join**: Customer joins Daily.co room using provided URL and token
3. **Bot Connection**: Voice bot automatically joins room and starts conversation
4. **Audio Processing**: 
   - Customer speech → Amazon STT → Text
   - Text → VoiceOrderingAgent → Response text  
   - Response text → Amazon TTS → Audio
5. **Order Placement**: Agent uses tools to manage menu and orders
6. **Session End**: Either party can end the session

## Monitoring & Management

### Session Cleanup
- Sessions auto-expire after 1 hour
- Manual cleanup endpoint for admins
- Failed sessions are automatically cleaned up

### Error Handling
- Graceful fallback to text responses on audio issues
- Comprehensive logging for debugging
- Health check endpoints for monitoring

### Security
- Room tokens with expiration times
- Business ownership verification for orders
- Rate limiting on API endpoints

## Customization

### Adding New Tools
```python
@tool
async def get_daily_specials(self) -> str:
    """Get today's special menu items."""
    # Implementation here
    pass

# Add to agent initialization:
self.agent = Agent(
    # ... existing config
    tools=[
        # ... existing tools
        self.get_daily_specials
    ]
)
```

### Voice Configuration
```python
# In voice_streaming_service.py
tts_service = AmazonTTSService(
    # ... existing config
    voice_id="Matthew",  # Change voice
    sample_rate=16000,   # Adjust quality
    language_code="en-US"
)
```

### Conversation Personality
Update the system prompt in `VoiceOrderingAgent._get_system_prompt()` to customize the assistant's personality and behavior.

## Troubleshooting

### Common Issues

1. **Import Errors**: Ensure all dependencies are installed with `pip install -e .`
2. **AWS Permissions**: Verify Bedrock and Polly/Transcribe access
3. **Daily.co Limits**: Check API quota and room limits
4. **Database Connection**: Verify Supabase credentials and network access

### Debug Mode
Set `DEBUG=True` in environment for detailed logging.

### Testing
Use the text-based demo script to test without voice hardware:
```bash
python app/agents/voice_demo.py your-business-id
```

## Production Considerations

- Set up proper AWS IAM roles with minimal required permissions
- Configure Daily.co webhooks for session monitoring  
- Implement rate limiting and request validation
- Set up monitoring and alerting for voice session failures
- Consider implementing conversation recording (with consent)
- Scale voice bot instances based on concurrent session needs