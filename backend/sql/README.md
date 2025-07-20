# Database Schema Documentation

## Overview

This directory contains the database schema for the Tably application, which uses Supabase (PostgreSQL) as the database backend.

## Schema Structure

### Authentication Integration

The `users` table is designed to work seamlessly with Supabase Auth:

- The `id` column references `auth.users(id)` as a foreign key
- When a new user signs up through Supabase Auth, a trigger automatically creates a corresponding entry in the `users` table
- Passwords are managed entirely by Supabase Auth (no `password_hash` column in our `users` table)

### Key Tables

1. **users** - Extended user profile data linked to auth.users
   - `id` (UUID) - References auth.users(id)
   - `email` (text) - User's email address
   - `full_name` (text) - User's full name
   - `role` (text) - Either 'customer' or 'business-owner'

2. **businesses** - Business profiles
3. **menu_items** - Restaurant menu items
4. **orders** - Customer orders with support for multiple ordering modes (chatbot, voice, manual)

### Row Level Security (RLS)

All tables have RLS enabled with policies that ensure:
- Users can only access their own data
- Business owners can manage their own businesses and related data
- Customers can view and create their own orders

## Files

- `schema.sql` - Main database schema file
- `migrate_users_to_auth.sql` - Migration script to update existing databases to use auth.users reference

## Setup Instructions

### For New Installations

1. Run the `schema.sql` file in your Supabase SQL editor:
   ```sql
   -- Execute the entire schema.sql file
   ```

### For Existing Installations

1. If you have an existing database that needs to be migrated to use the auth.users reference:
   ```sql
   -- Execute the migrate_users_to_auth.sql file
   ```

## Important Notes

1. **Email Verification**: The signup process is configured to work without email verification. To fully disable email verification:
   - Go to your Supabase dashboard
   - Navigate to Authentication → Settings
   - Under "Email Auth" settings, disable "Enable email confirmations"

2. **User Creation Flow**:
   - When a user signs up via Supabase Auth, the `on_auth_user_created` trigger fires
   - This automatically creates a corresponding entry in the `users` table with default role 'customer'
   - The `full_name` is extracted from the user metadata if provided during signup

3. **Role Management**: Users are assigned 'customer' role by default. To create business owners, you'll need to update the role after user creation.