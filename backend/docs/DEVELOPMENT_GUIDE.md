# Development Guide

This guide explains how to develop and maintain the Tably backend API.

## Project Structure

```
backend/
├── app/
│   ├── api/
│   │   ├── dependencies/     # Authentication and other dependencies
│   │   ├── endpoints/        # API endpoint modules
│   │   └── main.py          # Main API router
│   ├── core/                # Core configuration
│   ├── db/                  # Database connection modules
│   └── models/              # Pydantic models
├── docs/                    # Documentation files
├── sql/                     # Database schema files
└── main.py                  # Application entry point
```

## Adding New Endpoints

### 1. Create Models

Create Pydantic models in `app/models/`:

```python
# app/models/example.py
from pydantic import BaseModel, Field
from typing import Optional
from datetime import datetime

class ExampleBase(BaseModel):
    name: str = Field(..., description="Name of the example")
    description: Optional[str] = Field(None, description="Description")

class ExampleCreate(ExampleBase):
    pass

class ExampleUpdate(BaseModel):
    name: Optional[str] = Field(None, description="Name of the example")
    description: Optional[str] = Field(None, description="Description")

class ExampleResponse(ExampleBase):
    id: str
    created_at: datetime
    
    class Config:
        from_attributes = True
```

### 2. Create Database Connection

Create database operations in `app/db/`:

```python
# app/db/example.py
import logging
from supabase import Client, create_client
from typing import Dict, Any

from app.core.config import settings

logger = logging.getLogger(__name__)

class ExampleConnection:
    def __init__(self):
        self.supabase: Client = create_client(
            settings.SUPABASE_URL, settings.SUPABASE_KEY
        )

    async def create_example(self, example_data: Dict[str, Any]):
        """Create a new example"""
        try:
            response = (
                self.supabase.table("examples")
                .insert(example_data)
                .execute()
            )
            return response.data[0] if response.data else None
        except Exception as e:
            logger.error(f"Error creating example: {str(e)}")
            return None

    # Add other CRUD operations...
```

### 3. Create Endpoints

Create API endpoints in `app/api/endpoints/`:

```python
# app/api/endpoints/example.py
from fastapi import APIRouter, HTTPException, Depends, status
import logging
from app.core.config import settings
from app.api.dependencies.auth import get_current_user
from app.models.auth import UserResponse
from app.models.example import ExampleCreate, ExampleResponse
from app.db.example import ExampleConnection

logger = logging.getLogger(__name__)
router = APIRouter()

def get_example_db() -> ExampleConnection:
    return ExampleConnection()

@router.post("/", response_model=ExampleResponse, status_code=status.HTTP_201_CREATED)
async def create_example(
    example: ExampleCreate,
    current_user: UserResponse = Depends(get_current_user),
    example_db: ExampleConnection = Depends(get_example_db)
):
    """Create a new example"""
    try:
        # Add your business logic here
        result = await example_db.create_example(example.model_dump())
        
        if not result:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Failed to create example"
            )
        
        return ExampleResponse(**result)
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error creating example: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="An error occurred while creating the example"
        )
```

### 4. Register Endpoints

Update `app/api/main.py` to include your new endpoints:

```python
from app.api.endpoints import auth, menu_items, orders, example

api_router.include_router(example.router, prefix="/example", tags=["example"])
```

### 5. Update Documentation

Add documentation for your new endpoints:

1. Update `docs/API_OVERVIEW.md` with endpoint descriptions
2. Create detailed documentation in `docs/` if needed
3. Update `docs/README.md` to reference new documentation

### 6. Create Database Schema

If needed, create SQL schema in `sql/`:

```sql
-- sql/example_schema.sql
CREATE TABLE IF NOT EXISTS examples (
    id UUID DEFAULT gen_random_uuid() PRIMARY KEY,
    name TEXT NOT NULL,
    description TEXT,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- Enable RLS
ALTER TABLE examples ENABLE ROW LEVEL SECURITY;

-- Add RLS policies as needed
```

## Best Practices

### Authentication & Authorization

- Always use `get_current_user` dependency for protected endpoints
- Implement proper ownership verification for business-specific operations
- Use role-based access control where appropriate

### Error Handling

- Use specific HTTP status codes
- Provide meaningful error messages
- Log errors appropriately
- Don't expose sensitive information in error responses

### Database Operations

- Use async/await for database operations
- Implement proper error handling
- Use transactions when multiple operations need to be atomic
- Implement proper ownership verification

### Input Validation

- Use Pydantic models for request/response validation
- Add field constraints where appropriate
- Validate business logic in endpoint handlers

### Logging

- Use structured logging
- Log important operations and errors
- Don't log sensitive information

## Testing

### Manual Testing

1. Start the development server
2. Use the interactive docs at `/docs`
3. Test with real data
4. Verify error conditions

### Automated Testing

Create tests in a `tests/` directory:

```python
# tests/test_example.py
import pytest
from fastapi.testclient import TestClient
from app.main import app

client = TestClient(app)

def test_create_example():
    response = client.post("/api/example/", json={
        "name": "Test Example",
        "description": "Test Description"
    })
    assert response.status_code == 201
    data = response.json()
    assert data["name"] == "Test Example"
```

## Deployment

### Environment Variables

Required environment variables:
- `SUPABASE_URL` - Supabase project URL
- `SUPABASE_KEY` - Supabase service role key
- `JWT_SECRET` - Secret for JWT token signing
- `LOG_LEVEL` - Logging level (default: INFO)

### Docker

Use the provided Dockerfile and docker-compose.yml for containerized deployment.

### Database Migrations

Run SQL schema files in your Supabase project:
1. Go to Supabase Dashboard
2. Navigate to SQL Editor
3. Run the schema files from `sql/`

## Monitoring

### Logs

Monitor application logs for:
- Error rates
- Performance issues
- Security events

### Metrics

Track important metrics:
- API response times
- Error rates by endpoint
- Database connection health

## Security Considerations

### Authentication

- Use secure JWT tokens
- Implement proper token expiration
- Validate tokens on every request

### Authorization

- Implement role-based access control
- Verify ownership for business operations
- Use Row Level Security in database

### Input Validation

- Validate all input data
- Sanitize user inputs
- Prevent SQL injection

### Data Protection

- Don't log sensitive data
- Use HTTPS in production
- Implement proper CORS policies 