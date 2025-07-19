# Orders API Documentation

This document describes the Orders API endpoints for the Tably application.

## Overview

The Orders API provides endpoints for managing orders in the Tably system. It supports both business owner and customer operations with appropriate role-based access control.

## Base URL

```
/api/orders
```

## Authentication

All endpoints require authentication via JWT token in the Authorization header:
```
Authorization: Bearer <jwt_token>
```

## Order Status

Orders can have the following statuses:
- `pending` - Order has been placed but not yet confirmed
- `confirmed` - Order has been confirmed by the business
- `preparing` - Order is being prepared
- `ready` - Order is ready for pickup
- `completed` - Order has been completed
- `cancelled` - Order has been cancelled

## Endpoints

### Create Order

**POST** `/api/orders/`

Creates a new order.

**Request Body:**
```json
{
  "business_id": "uuid",
  "customer_id": "uuid",
  "items": [
    {
      "menu_item_id": "uuid",
      "quantity": 2,
      "special_instructions": "Extra cheese please"
    }
  ],
  "total_amount": "25.50",
  "special_instructions": "Please deliver to the back entrance",
  "pickup_time": "2024-01-15T18:30:00Z"
}
```

**Response:** `201 Created`
```json
{
  "id": "uuid",
  "business_id": "uuid",
  "customer_id": "uuid",
  "status": "pending",
  "total_amount": "25.50",
  "special_instructions": "Please deliver to the back entrance",
  "pickup_time": "2024-01-15T18:30:00Z",
  "items": [
    {
      "id": "uuid",
      "order_id": "uuid",
      "menu_item_id": "uuid",
      "menu_item_name": "Margherita Pizza",
      "menu_item_price": "12.75",
      "quantity": 2,
      "special_instructions": "Extra cheese please",
      "total_price": "25.50",
      "created_at": "2024-01-15T17:00:00Z"
    }
  ],
  "created_at": "2024-01-15T17:00:00Z",
  "updated_at": "2024-01-15T17:00:00Z"
}
```

### Get Orders by Business (Business Owner View)

**GET** `/api/orders/business/{business_id}`

Retrieves all orders for a specific business. Only accessible by the business owner.

**Query Parameters:**
- `page` (optional): Page number (default: 1)
- `page_size` (optional): Items per page (default: 20, max: 100)
- `status_filter` (optional): Filter by order status

**Response:** `200 OK`
```json
{
  "items": [
    {
      "id": "uuid",
      "business_id": "uuid",
      "customer_id": "uuid",
      "status": "pending",
      "total_amount": "25.50",
      "special_instructions": "Please deliver to the back entrance",
      "pickup_time": "2024-01-15T18:30:00Z",
      "items": [...],
      "created_at": "2024-01-15T17:00:00Z",
      "updated_at": "2024-01-15T17:00:00Z"
    }
  ],
  "total": 50,
  "page": 1,
  "page_size": 20
}
```

### Get Orders by Customer (Customer View)

**GET** `/api/orders/customer/{customer_id}`

Retrieves all orders for a specific customer. Only accessible by the customer themselves.

**Query Parameters:**
- `page` (optional): Page number (default: 1)
- `page_size` (optional): Items per page (default: 20, max: 100)
- `status_filter` (optional): Filter by order status

**Response:** `200 OK`
```json
{
  "items": [
    {
      "id": "uuid",
      "business_id": "uuid",
      "customer_id": "uuid",
      "status": "pending",
      "total_amount": "25.50",
      "special_instructions": "Please deliver to the back entrance",
      "pickup_time": "2024-01-15T18:30:00Z",
      "items": [...],
      "created_at": "2024-01-15T17:00:00Z",
      "updated_at": "2024-01-15T17:00:00Z"
    }
  ],
  "total": 10,
  "page": 1,
  "page_size": 20
}
```

### Get Single Order

**GET** `/api/orders/{order_id}`

Retrieves a specific order by ID. Accessible by both the business owner and the customer who placed the order.

**Response:** `200 OK`
```json
{
  "id": "uuid",
  "business_id": "uuid",
  "customer_id": "uuid",
  "status": "pending",
  "total_amount": "25.50",
  "special_instructions": "Please deliver to the back entrance",
  "pickup_time": "2024-01-15T18:30:00Z",
  "items": [...],
  "created_at": "2024-01-15T17:00:00Z",
  "updated_at": "2024-01-15T17:00:00Z"
}
```

### Update Order

**PATCH** `/api/orders/{order_id}`

Updates a specific order. Business owners can update status and special instructions. Customers can update pickup time and special instructions.

**Request Body:**
```json
{
  "status": "confirmed",
  "special_instructions": "Updated instructions",
  "pickup_time": "2024-01-15T19:00:00Z"
}
```

**Response:** `200 OK`
```json
{
  "id": "uuid",
  "business_id": "uuid",
  "customer_id": "uuid",
  "status": "confirmed",
  "total_amount": "25.50",
  "special_instructions": "Updated instructions",
  "pickup_time": "2024-01-15T19:00:00Z",
  "items": [...],
  "created_at": "2024-01-15T17:00:00Z",
  "updated_at": "2024-01-15T17:30:00Z"
}
```

### Delete Order

**DELETE** `/api/orders/{order_id}`

Deletes a specific order. Only accessible by the business owner.

**Response:** `200 OK`
```json
{
  "message": "Order deleted successfully",
  "deleted_id": "uuid"
}
```

## Error Responses

### 400 Bad Request
```json
{
  "detail": "Failed to create order"
}
```

### 403 Forbidden
```json
{
  "detail": "You don't have permission to access this business"
}
```

### 404 Not Found
```json
{
  "detail": "Order not found"
}
```

### 500 Internal Server Error
```json
{
  "detail": "An error occurred while creating the order"
}
```

## Role-Based Access Control

### Business Owners
- Can view all orders for their businesses
- Can update order status and special instructions
- Can delete orders
- Can filter orders by status

### Customers
- Can view their own orders
- Can update pickup time and special instructions
- Cannot update order status
- Cannot delete orders
- Can filter their orders by status

## Database Schema

The orders system uses two main tables:

### orders
- `id` (UUID, Primary Key)
- `business_id` (UUID, Foreign Key to businesses)
- `customer_id` (UUID, Foreign Key to auth.users)
- `status` (TEXT, Enum: pending, confirmed, preparing, ready, completed, cancelled)
- `total_amount` (DECIMAL)
- `special_instructions` (TEXT, nullable)
- `pickup_time` (TIMESTAMP, nullable)
- `created_at` (TIMESTAMP)
- `updated_at` (TIMESTAMP)

### order_items
- `id` (UUID, Primary Key)
- `order_id` (UUID, Foreign Key to orders)
- `menu_item_id` (UUID, Foreign Key to menu_items)
- `quantity` (INTEGER)
- `special_instructions` (TEXT, nullable)
- `created_at` (TIMESTAMP)

## Security Features

- Row Level Security (RLS) enabled on both tables
- JWT-based authentication required for all endpoints
- Role-based access control implemented
- Input validation and sanitization
- Proper error handling and logging 