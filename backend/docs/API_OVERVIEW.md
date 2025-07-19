# Tably API Overview

This document provides an overview of all API endpoints available in the Tably backend system.

## Base URL

```
/api
```

## Authentication

All endpoints require authentication via JWT token in the Authorization header:
```
Authorization: Bearer <jwt_token>
```

## API Endpoints

### Authentication (`/api/auth`)

#### POST `/api/auth/register`
Register a new user account.

#### POST `/api/auth/login`
Authenticate user and receive JWT token.

#### POST `/api/auth/logout`
Logout user (invalidate token).

#### GET `/api/auth/me`
Get current user information.

### Menu Items (`/api/menu-items`)

#### POST `/api/menu-items/`
Create a new menu item (business owners only).

#### GET `/api/menu-items/business/{business_id}`
Get all menu items for a specific business.

#### GET `/api/menu-items/{menu_item_id}`
Get a specific menu item by ID.

#### PATCH `/api/menu-items/{menu_item_id}`
Update a specific menu item (business owners only).

#### DELETE `/api/menu-items/{menu_item_id}`
Delete a specific menu item (business owners only).

#### GET `/api/menu-items/business/{business_id}/search`
Search menu items by name or description.

### Orders (`/api/orders`)

#### POST `/api/orders/`
Create a new order.

#### GET `/api/orders/business/{business_id}`
Get all orders for a specific business (business owners only).

#### GET `/api/orders/customer/{customer_id}`
Get all orders for a specific customer (customers only).

#### GET `/api/orders/{order_id}`
Get a specific order by ID (business owners or order customer).

#### PATCH `/api/orders/{order_id}`
Update a specific order (role-based permissions).

#### DELETE `/api/orders/{order_id}`
Delete a specific order (business owners only).

## Role-Based Access Control

### Business Owners
- Can manage menu items for their businesses
- Can view and manage all orders for their businesses
- Can update order status and special instructions
- Can delete orders

### Customers
- Can view menu items for any business
- Can place orders
- Can view their own orders
- Can update pickup time and special instructions for their orders
- Cannot modify order status

## Common Response Formats

### Success Response
```json
{
  "id": "uuid",
  "created_at": "2024-01-15T17:00:00Z",
  "updated_at": "2024-01-15T17:00:00Z"
}
```

### List Response
```json
{
  "items": [...],
  "total": 50,
  "page": 1,
  "page_size": 20
}
```

### Error Response
```json
{
  "detail": "Error message"
}
```

## HTTP Status Codes

- `200 OK` - Request successful
- `201 Created` - Resource created successfully
- `400 Bad Request` - Invalid request data
- `401 Unauthorized` - Authentication required
- `403 Forbidden` - Insufficient permissions
- `404 Not Found` - Resource not found
- `500 Internal Server Error` - Server error

## Pagination

List endpoints support pagination with the following query parameters:
- `page` (optional): Page number (default: 1)
- `page_size` (optional): Items per page (default: 20, max: 100)

## Filtering

Some endpoints support filtering:
- `available_only` (menu items): Show only available items
- `status_filter` (orders): Filter by order status

## Search

Menu items support text search:
- `q` (required): Search term
- `available_only` (optional): Show only available items
- `limit` (optional): Maximum number of results

## Database Schema

The system uses the following main tables:
- `auth.users` - User accounts
- `businesses` - Business information
- `menu_items` - Menu items for businesses
- `orders` - Order information
- `order_items` - Individual items within orders

## Security Features

- JWT-based authentication
- Row Level Security (RLS) in database
- Role-based access control
- Input validation and sanitization
- Proper error handling and logging

## Development

### Interactive Documentation
When running the development server, interactive API documentation is available at:
- `/docs` - Swagger UI
- `/redoc` - ReDoc

### Testing
Use the interactive documentation to test endpoints with real data.

### Environment Variables
Required environment variables:
- `SUPABASE_URL` - Supabase project URL
- `SUPABASE_KEY` - Supabase service role key
- `JWT_SECRET` - Secret for JWT token signing 