# Tably

Tably is a comprehensive AI-powered restaurant ordering system that revolutionizes how customers interact with restaurants through advanced voice, chat, and visual interfaces. Tably combines multiple specialized AI agents to create seamless ordering experiences while empowering restaurants with intelligent menu management, real-time inventory tracking, and automated customer service.

The system addresses critical challenges in restaurant operations by reducing human workload, improving order accuracy, and providing 24/7 multilingual customer service capabilities.

## System Architecture

Tably employs a sophisticated multi-agent architecture built on modern cloud technologies, featuring:

### Backend Architecture (Python/FastAPI)
- **FastAPI Framework**: High-performance REST API with automatic documentation
- **Supabase Integration**: PostgreSQL database with real-time capabilities and Row Level Security
- **Multi-Agent AI System**: Specialized agents powered by Amazon Bedrock Nova models
- **Real-time Voice Processing**: Bidirectional streaming with Amazon Nova Sonic model
- **AWS Integration**: Comprehensive use of AWS services for AI/ML capabilities

### Frontend Architecture (Next.js/React)
- **Next.js 15**: Modern React framework with App Router
- **TypeScript**: Type-safe development environment
- **Tailwind CSS**: Utility-first styling with custom components
- **Zustand**: Lightweight state management
- **Radix UI**: Accessible component primitives

## Strands Agent Framework

Tably is built on the **Strands Agent Framework**, a powerful Python framework for creating intelligent, tool-enabled AI agents. Strands provides the core infrastructure that enables Tably's sophisticated multi-agent architecture.

### Strands Framework Features
- **Tool Integration**: Seamless integration of custom tools and functions with AI agents
- **Model Flexibility**: Support for multiple LLM providers including Amazon Bedrock, OpenAI, and Anthropic
- **Agent Orchestration**: Advanced coordination between multiple specialized agents
- **Streaming Support**: Real-time conversation and response streaming
- **Context Management**: Intelligent conversation memory and context handling
- **Swarm Intelligence**: Multi-agent collaboration and task distribution

### How Tably Uses Strands
- **Agent Definitions**: Each specialized agent is defined using Strands' `Agent` class
- **Tool Ecosystem**: Restaurant-specific tools (menu search, order management) are implemented as Strands tools
- **Model Integration**: Seamless connection to Amazon Bedrock Nova models through Strands
- **Conversation Flow**: Natural dialogue management with context persistence
- **Swarm Coordination**: Multiple agents working together through Strands orchestration

## What Tably Does

Tably transforms restaurant ordering through intelligent AI automation, addressing the core challenges restaurants face in managing high-volume customer interactions. The system operates as a comprehensive digital assistant that can handle the entire customer journey from menu exploration to order completion.

**Core Functions:**
- **Voice-First Ordering**: Customers speak naturally to place orders, ask questions, and modify requests in real-time
- **Intelligent Menu Management**: Automatically analyzes menu images, extracts structured data, and keeps inventory synchronized
- **Multi-Channel Integration**: Seamlessly handles orders across voice, chat, mobile, and web interfaces
- **Business Intelligence**: Provides restaurants with insights into customer preferences, order patterns, and operational efficiency

## AI Agent Architecture

Tably's intelligence comes from specialized AI agents powered by Strands that each handle specific aspects of the restaurant ordering experience:

### 1. Voice Ordering Agent (`voice_ordering_agent.py`)
**What It Does**: The primary customer-facing agent that handles complete voice-based ordering conversations

**Technology**: Strands Agent with Amazon Nova Sonic model for ultra-fast voice processing

**How It Works**:
- **Natural Conversation Flow**: Engages customers in friendly, human-like dialogue
- **Menu Intelligence**: Searches and retrieves menu items based on customer requests
- **Order Building**: Adds items to cart, handles quantities, modifications, and special instructions
- **Smart Clarification**: Asks intelligent follow-up questions when customer requests are ambiguous
- **Order Completion**: Collects customer information and finalizes orders

**Strands Integration**:
- Uses @tool decorators for restaurant operations (get_menu_items, add_item_to_order, etc.)
- Leverages Strands conversation memory for context preservation
- Implements model-agnostic interface allowing seamless Nova Sonic integration

**Customer Experience**: "Hi, I'd like to order a pizza" → Agent searches menu → "I found three pizzas: Margherita, Pepperoni, and Supreme. Which would you prefer?" → Continues conversation until order is complete

### 2. Menu Intelligence Agent (`menu_agent.py`)
**What It Does**: Analyzes menus and provides intelligent recommendations based on customer preferences and dietary needs

**Technology**: Strands Agent with Amazon Bedrock vision models and specialized analysis tools

**How It Works**:
- **Menu Image Processing**: Automatically extracts menu items, prices, descriptions from photos or PDFs
- **Dietary Analysis**: Identifies allergens, nutritional information, and dietary compatibility
- **Smart Recommendations**: Suggests items based on customer preferences, restrictions, and order history
- **Menu Search**: Provides advanced search capabilities across menu categories and ingredients

**Strands Integration**:
- Multiple specialized tools for different analysis functions
- Context-aware processing that understands customer dietary needs
- Tool chaining for complex menu analysis operations

**Business Value**: Restaurants can upload menu images and instantly have structured, searchable menu data with automatic dietary categorization

### 3. Restaurant Voice Agent (`restaurant_voice_agent.py`)
**What It Does**: Handles advanced real-time voice processing with bidirectional streaming for enterprise-grade voice experiences

**Technology**: Custom implementation using AWS SDK Bedrock Runtime with real-time audio processing

**How It Works**:
- **Real-Time Audio Streaming**: Processes voice input and output simultaneously for natural conversation flow
- **Session Management**: Manages complete voice session lifecycle from greeting to order completion
- **Cart Synchronization**: Updates order cart in real-time with WebSocket events for live UI updates
- **Tool Integration**: Coordinates with restaurant operations while maintaining voice conversation

**Integration with Strands**: Works alongside Strands agents for tool processing while handling the complex audio streaming infrastructure

**Technical Excellence**: Enables interruption-free conversations where customers can speak naturally without waiting for responses to complete

### 4. Swarm Orchestrator (`swarm_orchestrator.py`)
**What It Does**: Coordinates multiple specialized agents working together as intelligent swarms for complex ordering scenarios

**Technology**: Strands framework with advanced multi-agent coordination

**How It Works**:
- **Agent Swarm Management**: Coordinates specialized agents (Order Coordinator, Menu Specialist, Language Specialist, Dietary Specialist)
- **Parallel Processing**: Multiple agents work simultaneously on different aspects of customer requests
- **Context Sharing**: Ensures all agents have access to relevant conversation context and customer preferences
- **Dynamic Routing**: Intelligently routes specific tasks to the most appropriate specialist agent

**Strands Integration**:
- Advanced swarm coordination using Strands multi-agent capabilities
- Inter-agent communication and context passing
- Dynamic tool routing based on request complexity

**Use Case Example**: Customer asks "I need something vegetarian for my gluten-free friend" → Language Specialist interprets request → Dietary Specialist identifies restrictions → Menu Specialist finds compatible items → Order Coordinator presents options

### 5. Ordering Agents (`ordering_agents.py`)
**What It Does**: Provides specialized ordering agents for different scenarios (multilingual, dietary restrictions, complex orders)

**Technology**: Multiple coordinated Strands Agents with specialized roles

**How It Works**:
- **Order Coordinator**: Manages overall ordering process and conversation flow
- **Menu Specialist**: Deep menu knowledge with strict item availability enforcement
- **Language Specialist**: Handles multilingual conversations and cultural context
- **Dietary Specialist**: Expert in allergies, dietary restrictions, and nutritional needs
- **Order Validator**: Ensures order completeness and accuracy before finalization

**Strands Integration**:
- Each specialist is a dedicated Strands Agent with focused capabilities
- Tool sharing and context passing between agents
- Coordinated responses that feel like single conversation

**Business Impact**: Handles complex customer scenarios that would typically require multiple staff members or result in order errors

## System Intelligence

**Menu Enforcement**: All agents strictly adhere to available menu items, preventing recommendations of unavailable products and ensuring accurate pricing

**Context Awareness**: The system maintains conversation context across agent handoffs, remembering customer preferences, dietary restrictions, and order history

**Real-Time Coordination**: Agents work together seamlessly, with inventory updates, cart changes, and menu modifications instantly reflected across all customer touchpoints

**Learning Capability**: The system improves over time by analyzing successful interactions and common customer patterns to enhance future conversations

## Operational Impact

**For Customers**: Natural, efficient ordering experience that feels like talking to a knowledgeable restaurant staff member who never forgets preferences or makes mistakes

**For Restaurants**: Reduced staff workload, increased order accuracy, 24/7 availability, and detailed analytics on customer preferences and ordering patterns

**For Business Growth**: Consistent service quality, multilingual support, and the ability to handle multiple customers simultaneously during peak hours

## Technology Stack

### Backend Technologies
- **Framework**: FastAPI (Python 3.12+)
- **Database**: Supabase (PostgreSQL)
- **AI/ML**: Amazon Bedrock (Nova Sonic, Nova models)
- **Agent Framework**: Strands Agents (core multi-agent orchestration)
- **Real-time Processing**: AWS SDK Bedrock Runtime
- **Audio Processing**: PyAudio, AWS Polly/Transcribe
- **Image Processing**: Pillow, PDF2Image
- **Authentication**: JWT with Supabase Auth

### Strands Agent Implementation
- **Core Agent Classes**: Strands `Agent` with custom system prompts and tool integration
- **Tool Ecosystem**: Custom @tool decorators for restaurant operations (menu search, order management, etc.)
- **Model Integration**: Seamless connection to Amazon Bedrock Nova models through Strands
- **Swarm Coordination**: Multi-agent collaboration using Strands swarm tools
- **Conversation Management**: Built-in context handling and conversation flow
- **Streaming Support**: Real-time conversation streaming with Strands async capabilities

### Frontend Technologies
- **Framework**: Next.js 15 with React 19
- **Language**: TypeScript
- **Styling**: Tailwind CSS 4 with custom components
- **UI Components**: Radix UI primitives
- **State Management**: Zustand
- **Animations**: Motion (Framer Motion)
- **Charts**: Recharts
- **3D Graphics**: Three.js with React Three Fiber

### Infrastructure & Services
- **Database**: Supabase PostgreSQL with real-time subscriptions
- **AI Services**: Amazon Bedrock (Nova Sonic, Claude models)
- **Voice Services**: Amazon Polly (TTS), Amazon Transcribe (STT)
- **Image Analysis**: Amazon Textract, Bedrock Vision models
- **Authentication**: Supabase Auth with JWT
- **Deployment**: Docker containers

## Key Features & Capabilities

### Multi-Modal Ordering
- **Voice Ordering**: Real-time voice conversations with natural language processing
- **Chat Interface**: Text-based ordering with intelligent conversation flow
- **Visual Menu**: Image-based menu analysis and item selection
- **Mobile Interface**: Responsive design for all device types

### AI-Powered Intelligence
- **Menu Analysis**: Automatic extraction of menu data from images/PDFs
- **Smart Recommendations**: Personalized suggestions based on preferences and context
- **Dietary Intelligence**: Automatic handling of allergies and dietary restrictions
- **Multilingual Support**: Natural language processing in multiple languages

### Business Management
- **Real-time Inventory**: Dynamic menu updates based on stock availability
- **Order Tracking**: Comprehensive order management and status updates
- **Analytics Dashboard**: Business insights and performance metrics
- **Staff Tools**: Efficient order management and customer service tools

### Technical Features
- **Real-time Updates**: Live order status and inventory synchronization
- **Security**: Row Level Security (RLS), JWT authentication, input validation
- **Scalability**: Modular architecture with microservice-ready design
- **Performance**: Optimized database queries and caching strategies

## API Architecture

### Authentication System
- JWT-based authentication with Supabase
- Role-based access control (Business owners, Customers)
- Secure API endpoints with proper authorization

### Core API Endpoints
- **Authentication**: `/api/auth/*` - User registration, login, profile management
- **Menu Management**: `/api/menu-items/*` - Menu CRUD operations, search, analysis
- **Order Processing**: `/api/orders/*` - Order creation, management, tracking
- **Voice Integration**: `/api/voice-ordering/*` - Voice session management
- **Business Operations**: `/api/business/*` - Business management and analytics

## Voice Integration Details

### Real-time Voice Processing
- **Amazon Nova Sonic**: Ultra-fast voice model for real-time conversations
- **Bidirectional Streaming**: Simultaneous input/output audio processing
- **Voice Session Management**: Complete session lifecycle management
- **Error Handling**: Graceful fallback and recovery mechanisms

### Voice Technologies
- **Speech-to-Text**: Amazon Transcribe with real-time streaming
- **Text-to-Speech**: Amazon Polly with natural voice synthesis
- **Audio Processing**: PyAudio for real-time audio capture and playback
- **WebSocket Integration**: Real-time communication for voice sessions

## Development Setup

### Prerequisites
- Python 3.12+
- Node.js 18+
- Supabase account
- AWS account with Bedrock access

### Backend Setup
```bash
cd backend
pip install -e .
cp .env.example .env  # Configure environment variables
python main.py
```

### Frontend Setup
```bash
cd frontend
npm install
cp .env.example .env.local  # Configure environment variables
npm run dev
```

## Security & Compliance

- **Data Protection**: End-to-end encryption for sensitive data
- **Privacy**: GDPR-compliant data handling
- **Authentication**: Multi-factor authentication support
- **Access Control**: Fine-grained permissions and role management
- **Audit Logging**: Comprehensive activity tracking

## Performance & Scalability

- **Database Optimization**: Efficient indexing and query optimization
- **Caching Strategy**: Multi-layer caching for improved response times
- **Load Balancing**: Horizontal scaling capabilities
- **CDN Integration**: Global content delivery for optimal performance

## Future Roadmap

- **POS Integration**: Direct integration with major POS systems
- **Payment Processing**: Integrated payment gateway support
- **Analytics Enhancement**: Advanced business intelligence features
- **Mobile Apps**: Native iOS and Android applications
- **Multi-tenant Architecture**: Support for restaurant chains and franchises