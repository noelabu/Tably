# Tably Backend

## 📚 Documentation

For comprehensive documentation about the Menu Image Analysis system, see the **[docs/](./docs/)** directory:

- **[Menu Image Analysis Overview](./docs/MENU_IMAGE_ANALYSIS_SUMMARY.md)** - Complete API reference and implementation guide
- **[AWS Setup Instructions](./docs/AWS_SETUP_INSTRUCTIONS.md)** - How to configure AWS Bedrock credentials
- **[PDF Support Features](./docs/PDF_SUPPORT_UPDATE.md)** - PDF processing capabilities and usage
- **[Amazon Nova Integration](./docs/AMAZON_NOVA_UPDATE.md)** - AI model implementation details
- **[Demo Scripts](./docs/extract_only_demo.py)** - Python examples for testing endpoints

## Backend Overview

This is the FastAPI backend for the Tably multi-agent AI restaurant ordering system. It provides RESTful APIs for menu management, order processing, user authentication, and AI-powered menu image analysis.

### Key Features

- **Menu Image Analysis**: Advanced AI-powered extraction of menu data from single or multiple menu images (PDF support is currently disabled)
- **Authentication System**: JWT-based authentication with role-based access control
- **Menu Management**: CRUD operations for menu items with business ownership validation
- **Database Integration**: Supabase integration for data persistence
- **Multi-image Support**: Process both single and multiple image files for menu analysis
- **Bulk Processing**: Handle multiple image files simultaneously

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

## Dependency Installation (with uv)

This project uses [uv](https://github.com/astral-sh/uv) as the package manager for Python dependencies.

### 1. Install uv

Follow the instructions at https://github.com/astral-sh/uv to install uv for your platform.

### 2. Install Python dependencies

From the backend directory, run:

```
uv pip install -r pyproject.toml
```

This will install all required dependencies, including:
- `pillow` (image processing)

### 3. Install a Package Manager (if needed)

#### Windows: Install Chocolatey

Open **PowerShell as Administrator** and run:

```powershell
Set-ExecutionPolicy Bypass -Scope Process -Force; `
[System.Net.ServicePointManager]::SecurityProtocol = [System.Net.ServicePointManager]::SecurityProtocol -bor 3072; `
iex ((New-Object System.Net.WebClient).DownloadString('https://community.chocolatey.org/install.ps1'))
```

#### macOS: Install Homebrew

Open the Terminal and run:

```sh
/bin/bash -c "$(curl -fsSL https://raw.githubusercontent.com/Homebrew/install/HEAD/install.sh)"
```

---

### 4. Install Poppler (system dependency for pdf2image)

**Poppler is required for PDF-to-image conversion. If you get an error like `Unable to get page count. Is poppler installed and in PATH?`, you must install Poppler:**

> **Note:** PDF support is currently disabled in the menu image analysis endpoints. You do not need Poppler unless you plan to enable PDF support in the future.

#### Windows (choose one method):

- **With Chocolatey (admin PowerShell):**
  ```powershell
  choco install poppler
  ```
- **With Scoop (user PowerShell):**
  1. Install Scoop (if not already installed):
     ```powershell
     irm get.scoop.sh | iex
     ```
  2. Install Poppler:
     ```powershell
     scoop install poppler
     ```

#### macOS:
```sh
brew install poppler
```

#### Linux (Debian/Ubuntu):
```sh
sudo apt-get install poppler-utils
```

After installing Poppler, restart your terminal and backend server.

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

## Menu Image Analysis Endpoints

The backend provides endpoints for analyzing menu images and extracting menu items. PDF support is currently disabled due to system dependency issues.

### Single Image Menu Analysis

- **Endpoint:** `POST /api/v1/menu-image-analysis/extract-only`
- **Description:** Upload a single menu image (JPG, PNG, etc.) to extract menu items.
- **Request:**
  - `file`: The image file (form-data)
- **Response:**
  - Extracted menu items and restaurant info

### Multi-Image Menu Analysis

- **Endpoint:** `POST /api/v1/menu-image-analysis/bulk-extract-only`
- **Description:** Upload multiple menu images to extract menu items from each image.
- **Request:**
  - `files`: List of image files (form-data)
- **Response:**
  - List of extracted menu items for each image

> **Note:** PDF files are not currently supported. Please use image files only.

## Contributing

1. Create a feature branch: `