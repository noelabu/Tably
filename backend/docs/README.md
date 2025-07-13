# Tably Backend Documentation

This directory contains documentation for the Tably backend API and related components.

## API Documentation

### [API Overview](./API_OVERVIEW.md)
Complete overview of all API endpoints in the system, including:
- Authentication endpoints
- Menu items endpoints
- Orders endpoints
- Common response formats
- HTTP status codes
- Pagination and filtering

### [Orders API](./ORDERS_API.md)
Detailed documentation for the Orders API endpoints, including:
- Authentication requirements
- Endpoint descriptions and examples
- Request/response schemas
- Role-based access control
- Error handling
- Database schema

### Menu Items API
Documentation for the Menu Items API (to be added)

### Auth API
Documentation for the Authentication API (to be added)

## Database Schema

### [Orders Schema](../sql/orders_schema.sql)
SQL schema for the orders and order_items tables including:
- Table definitions
- Foreign key relationships
- Row Level Security (RLS) policies
- Indexes for performance
- Triggers for automatic updates

### [Main Schema](../sql/schema.sql)
Main database schema for the application

## Development

### [Development Guide](./DEVELOPMENT_GUIDE.md)
Comprehensive guide for developing and maintaining the API, including:
- Project structure overview
- Step-by-step guide for adding new endpoints
- Best practices for authentication, error handling, and database operations
- Testing strategies
- Deployment instructions
- Security considerations

### Setup
1. Install dependencies: `pip install -r requirements.txt`
2. Set up environment variables
3. Run database migrations
4. Start the development server

### Testing
- API endpoints can be tested using the interactive docs at `/docs`
- Use the provided example requests in the API documentation

### Deployment
- Docker configuration available in `Dockerfile`
- Docker Compose setup in `docker-compose.yml`

## Contributing

When adding new API endpoints:
1. Create models in `app/models/`
2. Create database connection in `app/db/`
3. Create endpoints in `app/api/endpoints/`
4. Update this documentation
5. Add SQL schema if needed 