# Tably Backend

## 📚 Documentation

For comprehensive documentation about the Menu Image Analysis system, see the **[docs/](./docs/)** directory:

- **[Menu Image Analysis Overview](./docs/MENU_IMAGE_ANALYSIS_SUMMARY.md)** - Complete API reference and implementation guide
- **[AWS Setup Instructions](./docs/AWS_SETUP_INSTRUCTIONS.md)** - How to configure AWS Bedrock credentials
- **[PDF Support Features](./docs/PDF_SUPPORT_UPDATE.md)** - PDF processing capabilities and usage
- **[Amazon Nova Integration](./docs/AMAZON_NOVA_UPDATE.md)** - AI model implementation details
- **[Demo Scripts](./docs/extract_only_demo.py)** - Python examples for testing endpoints

## Overview

Tably is a multi-agent AI system that revolutionizes restaurant ordering by automating and enhancing voice-based experiences across multiple languages, channels, and dietary needs. It addresses critical bottlenecks in high-volume restaurant operations, particularly in dine-in and quick-service restaurants (QSR), where human staff are often impacted by noise, fatigue, and time constraints.

The system enables customers to place orders naturally through voice, chat, or UI while providing restaurants with intelligent menu management, real-time stock tracking, and personalized recommendations to maximize order value and customer satisfaction.

## Multi-Agent Architecture

Tably employs a sophisticated multi-agent system where specialized AI agents collaborate to deliver a seamless ordering experience:

### 1. Voice Recognition Agent
- Processes natural language inputs in multiple languages (English, Spanish, and more)
- Handles various accents and speech patterns with high accuracy
- Adapts to noisy environments common in restaurants
- Provides real-time transcription and intent understanding

### 2. Menu Intelligence Agent
- Maintains comprehensive menu knowledge including items, combos, modifiers, and prices
- Tracks allergen information and nutritional data
- Manages real-time stock availability and automatically removes out-of-stock items
- Handles complex menu hierarchies and seasonal variations

### 3. Recommendation Agent
- Personalizes upsell and cross-sell suggestions based on:
  - Order history and customer preferences
  - Time of day and seasonal trends
  - Current promotions and combo deals
- Respects dietary constraints and allergen restrictions
- Optimizes recommendations for both customer satisfaction and order value

### 4. POS Integration Agent
- Seamlessly integrates with existing restaurant POS systems
- Synchronizes orders across all channels (drive-thru, phone, kiosk, mobile app)
- Updates inventory in real-time
- Manages payment processing and order routing to kitchen systems

## Key Capabilities

- **Multi-Language Support**: Natural language processing in multiple languages with context-aware translations
- **Omni-Channel Experience**: Consistent ordering across drive-thru, phone, kiosks, and mobile apps
- **Dietary Intelligence**: Automatic handling of allergies, dietary preferences (vegetarian, vegan, gluten-free)
- **Real-Time Inventory**: Dynamic menu updates based on stock availability
- **Accessibility Features**: Support for visually and hearing-impaired customers with adaptive responses
- **Order Accuracy**: Reduces errors through intelligent confirmation and clarification
- **Time Estimation**: Provides accurate preparation time estimates and pickup windows
- **Staff Efficiency**: Reduces workload on human staff, allowing them to focus on food quality and customer service

## Requirements

- Python 3.12+
- uv (Fast Python package manager)

## Installation

1. Install uv:
```bash
# macOS/Linux
curl -LsSf https://astral.sh/uv/install.sh | sh

# Windows
powershell -ExecutionPolicy ByPass -c "irm https://astral.sh/uv/install.ps1 | iex"

# Or with pip
pip install uv
```

2. Clone the repository:
```bash
git clone https://github.com/noelabu/Tably.git
cd Tably/backend
```

3. Create a virtual environment and install dependencies:
```bash
# Create virtual environment
uv venv

# Activate virtual environment
source .venv/bin/activate  # On Windows: .venv\Scripts\activate

# Install dependencies
uv pip install -e .  # Install the package in editable mode
# OR
uv pip install -e ".[dev]"  # Include development dependencies
```

Alternatively, you can use uv's sync command:
```bash
# This creates venv and installs dependencies in one step
uv sync
```

## Development Setup

### Environment Variables

Create a `.env` file in the backend directory:
```env
# API Configuration
PORT=8000
DEBUG=true
LOG_LEVEL=INFO

# Add other environment variables as needed
```

### Running the Server

Start the development server:
```bash
uv run python main.py
# OR if virtual environment is activated
uv run uvicorn main:app --host 0.0.0.0 --port 8000
```

The API will be available at `http://localhost:8000`

### API Documentation

Once the server is running, you can access:
- Interactive API docs: `http://localhost:8000/docs`
- Alternative API docs: `http://localhost:8000/redoc`

## Technical Architecture

### Technology Stack
- **Backend Framework**: FastAPI (Python) for high-performance async API
- **AI/ML**: LangChain for agent orchestration, OpenAI/Anthropic for LLMs
- **Voice Processing**: Azure Speech Services / Google Cloud Speech-to-Text
- **Database**: PostgreSQL with pgvector for embeddings
- **Cache**: Redis for session management and real-time data
- **Message Queue**: RabbitMQ/Kafka for agent communication
- **API Gateway**: Kong/Traefik for multi-channel routing

### Agent Communication Flow
1. **Input Processing**: Voice/text input → Voice Recognition Agent
2. **Intent Analysis**: Parsed order → Menu Intelligence Agent
3. **Enhancement**: Order details → Recommendation Agent
4. **Execution**: Final order → POS Integration Agent
5. **Response**: Confirmation → Customer via original channel

## Project Structure

```
backend/
├── app/
│   ├── __init__.py
│   ├── agents/              # Multi-agent system
│   │   ├── __init__.py
│   │   ├── voice_recognition.py
│   │   ├── menu_intelligence.py
│   │   ├── recommendation.py
│   │   └── pos_integration.py
│   ├── api/
│   │   ├── __init__.py
│   │   ├── main.py          # API router configuration
│   │   └── endpoints/       # API endpoints
│   │       ├── __init__.py
│   │       ├── auth.py      # Authentication endpoints
│   │       ├── orders.py    # Order management
│   │       ├── menu.py      # Menu operations
│   │       └── voice.py     # Voice processing
│   ├── core/
│   │   ├── __init__.py
│   │   ├── app.py           # FastAPI app factory
│   │   ├── config.py        # Configuration settings
│   │   └── ai_config.py     # AI/LLM configurations
│   ├── models/              # Data models
│   │   ├── __init__.py
│   │   ├── order.py
│   │   ├── menu.py
│   │   └── customer.py
│   └── services/            # Business logic
│       ├── __init__.py
│       ├── nlp_service.py
│       ├── menu_service.py
│       └── order_service.py
├── main.py                  # Application entry point
├── pyproject.toml          # Project dependencies and metadata
├── Dockerfile              # Docker configuration
├── docker-compose.yml      # Docker Compose configuration
└── README.md               # This file
```

## Development Commands

### Linting and Formatting

```bash
# Run linter
uv run ruff check .

# Format code
uv run ruff format .
```

### Testing

```bash
# Run all tests
uv run pytest

# Run with coverage
uv run pytest --cov=app
```

### Pre-commit Hooks

Set up pre-commit hooks for automatic code quality checks:
```bash
uv pip install pre-commit
pre-commit install
```

## Docker Development

Build and run with Docker Compose:
```bash
docker-compose up --build
```

## API Endpoints

### Authentication Service

- `GET /auth/health` - Health check endpoint
- `GET /auth/hello` - Simple greeting endpoint (accepts optional `name` parameter)

## Contributing

1. Create a feature branch: `git checkout -b feature/your-feature`
2. Commit your changes: `git commit -m 'Add some feature'`
3. Push to the branch: `git push origin feature/your-feature`
4. Submit a pull request

## License

This project is licensed under the MIT License.