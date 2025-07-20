-- Migration script to update users table to reference auth.users
-- WARNING: This migration assumes you're starting fresh or have already migrated user data

-- Step 1: Drop the existing trigger and function
DROP TRIGGER IF EXISTS on_auth_user_created ON auth.users;
DROP FUNCTION IF EXISTS public.handle_new_user();

-- Step 2: Drop existing foreign key constraints that reference users table
ALTER TABLE businesses DROP CONSTRAINT IF EXISTS businesses_owner_id_fkey;
ALTER TABLE customers_business_views DROP CONSTRAINT IF EXISTS customers_business_views_user_id_fkey;
ALTER TABLE orders DROP CONSTRAINT IF EXISTS orders_customer_id_fkey;
ALTER TABLE chatbot_sessions DROP CONSTRAINT IF EXISTS chatbot_sessions_user_id_fkey;

-- Step 3: Drop the existing users table
DROP TABLE IF EXISTS users CASCADE;

-- Step 4: Create new users table that references auth.users
CREATE TABLE users (
  id uuid PRIMARY KEY REFERENCES auth.users(id) ON DELETE CASCADE,
  email text NOT NULL UNIQUE,
  full_name text,
  role text NOT NULL CHECK (role IN ('customer', 'business-owner')),
  created_at timestamp with time zone DEFAULT now()
);

-- Step 5: Re-create foreign key constraints
ALTER TABLE businesses ADD CONSTRAINT businesses_owner_id_fkey 
  FOREIGN KEY (owner_id) REFERENCES users(id) ON DELETE CASCADE;

ALTER TABLE customers_business_views ADD CONSTRAINT customers_business_views_user_id_fkey 
  FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE;

ALTER TABLE orders ADD CONSTRAINT orders_customer_id_fkey 
  FOREIGN KEY (customer_id) REFERENCES users(id);

ALTER TABLE chatbot_sessions ADD CONSTRAINT chatbot_sessions_user_id_fkey 
  FOREIGN KEY (user_id) REFERENCES users(id);

-- Step 6: Enable RLS on users table
ALTER TABLE users ENABLE ROW LEVEL SECURITY;

-- Step 7: Re-create RLS policies for users table
CREATE POLICY "Users can view their own profile"
ON users FOR SELECT USING (auth.uid() = id);

CREATE POLICY "Users can update their own profile"
ON users FOR UPDATE USING (auth.uid() = id);

-- Step 8: Create updated trigger function for auto-creating users
CREATE FUNCTION public.handle_new_user()
RETURNS trigger AS $$
BEGIN
  INSERT INTO public.users (id, email, full_name, role)
  VALUES (
    new.id,
    new.email,
    coalesce(new.raw_user_meta_data->>'full_name', ''), -- Get full_name from user metadata
    coalesce(new.raw_user_meta_data->>'role', 'customer') -- Get role from user metadata, default to customer
  );
  RETURN new;
END;
$$ LANGUAGE plpgsql SECURITY DEFINER;

-- Step 9: Create trigger for new auth users
CREATE TRIGGER on_auth_user_created
AFTER INSERT ON auth.users
FOR EACH ROW EXECUTE PROCEDURE public.handle_new_user();

-- Step 10: If you have existing auth.users that need entries in the users table, run this:
-- INSERT INTO users (id, email, full_name, role)
-- SELECT 
--   id, 
--   email,
--   coalesce(raw_user_meta_data->>'full_name', ''),
--   'customer'
-- FROM auth.users
-- WHERE id NOT IN (SELECT id FROM users);