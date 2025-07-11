-- Enable required extension
create extension if not exists "pgcrypto";

-- USERS
-- This table extends Supabase auth.users with additional application-specific fields
create table users (
  id uuid primary key references auth.users(id) on delete cascade,
  email text not null unique,
  full_name text,
  role text not null check (role in ('customer', 'business-owner')),
  created_at timestamp with time zone default now()
);

-- BUSINESSES
create table businesses (
  id uuid primary key default gen_random_uuid(),
  owner_id uuid references users(id) on delete cascade,
  name text not null,
  description text,
  address text,
  timezone text,
  logo_url text,
  created_at timestamp with time zone default now()
);

-- BUSINESS DOCUMENTS
create table business_documents (
  id uuid primary key default gen_random_uuid(),
  business_id uuid references businesses(id) on delete cascade,
  document_type text,
  document_url text,
  uploaded_at timestamp with time zone default now()
);

-- MENU ITEMS
create table menu_items (
  id uuid primary key default gen_random_uuid(),
  business_id uuid references businesses(id) on delete cascade,
  name text not null,
  description text,
  price numeric(8,2) not null,
  image_url text,
  available boolean default true,
  created_at timestamp with time zone default now()
);

-- MODIFIERS
create table modifiers (
  id uuid primary key default gen_random_uuid(),
  menu_item_id uuid references menu_items(id) on delete cascade,
  name text,
  price_delta numeric(8,2) default 0.00,
  is_default boolean default false
);

-- STOCK LEVELS
create table stock_levels (
  id uuid primary key default gen_random_uuid(),
  menu_item_id uuid references menu_items(id) on delete cascade,
  quantity_available integer default 0,
  last_updated timestamp with time zone default now()
);

-- CUSTOMER-BUSINESS VIEWS (optional)
create table customers_business_views (
  id uuid primary key default gen_random_uuid(),
  user_id uuid references users(id) on delete cascade,
  business_id uuid references businesses(id),
  last_visited timestamp with time zone default now()
);

-- ORDERS
create table orders (
  id uuid primary key default gen_random_uuid(),
  customer_id uuid references users(id),
  business_id uuid references businesses(id),
  total_amount numeric(10,2),
  order_mode text check (order_mode in ('chatbot', 'voice', 'manual')),
  status text default 'pending',
  created_at timestamp with time zone default now()
);

-- ORDER ITEMS
create table order_items (
  id uuid primary key default gen_random_uuid(),
  order_id uuid references orders(id) on delete cascade,
  menu_item_id uuid references menu_items(id),
  quantity integer not null,
  price_at_order numeric(8,2)
);

-- ORDER ITEM MODIFIERS
create table order_item_modifiers (
  id uuid primary key default gen_random_uuid(),
  order_item_id uuid references order_items(id) on delete cascade,
  modifier_id uuid references modifiers(id)
);

-- ORDER STATUS TRACKING
create table order_status_tracking (
  id uuid primary key default gen_random_uuid(),
  order_id uuid references orders(id) on delete cascade,
  status text,
  updated_at timestamp with time zone default now()
);

-- CHATBOT SESSION
create table chatbot_sessions (
  id uuid primary key default gen_random_uuid(),
  user_id uuid references users(id),
  business_id uuid references businesses(id),
  started_at timestamp with time zone default now(),
  last_interaction timestamp with time zone default now()
);

-- VOICE ORDERS
create table voice_orders (
  id uuid primary key default gen_random_uuid(),
  order_id uuid references orders(id) on delete cascade,
  transcript text,
  confidence_score numeric(4,2),
  language_detected text,
  created_at timestamp with time zone default now()
);

-- 🔐 ENABLE RLS
alter table users enable row level security;
alter table businesses enable row level security;
alter table business_documents enable row level security;
alter table menu_items enable row level security;
alter table modifiers enable row level security;
alter table stock_levels enable row level security;
alter table orders enable row level security;
alter table order_items enable row level security;
alter table order_item_modifiers enable row level security;
alter table order_status_tracking enable row level security;
alter table chatbot_sessions enable row level security;
alter table voice_orders enable row level security;

-- ✅ POLICIES

-- USERS
create policy "Users can view their own profile"
on users for select using (auth.uid() = id);

create policy "Users can update their own profile"
on users for update using (auth.uid() = id);

-- BUSINESSES
create policy "Business owners can manage their own businesses"
on businesses for all using (auth.uid() = owner_id);

-- BUSINESS DOCUMENTS
create policy "Business owners can access their business documents"
on business_documents for all
using (
  auth.uid() in (
    select owner_id from businesses where businesses.id = business_documents.business_id
  )
);

-- MENU ITEMS
create policy "Business owners can manage their own menu items"
on menu_items for all
using (
  auth.uid() in (
    select owner_id from businesses where businesses.id = menu_items.business_id
  )
);

-- MODIFIERS
create policy "Business owners can manage their modifiers"
on modifiers for all
using (
  auth.uid() in (
    select owner_id
    from businesses
    join menu_items on menu_items.business_id = businesses.id
    where menu_items.id = modifiers.menu_item_id
  )
);

-- STOCK LEVELS
create policy "Business owners can manage their stock levels"
on stock_levels for all
using (
  auth.uid() in (
    select owner_id
    from businesses
    join menu_items on menu_items.business_id = businesses.id
    where menu_items.id = stock_levels.menu_item_id
  )
);

-- ORDERS (CUSTOMER)
create policy "Customers can view their own orders"
on orders for select using (auth.uid() = customer_id);

create policy "Customers can insert orders"
on orders for insert with check (auth.uid() = customer_id);

-- ORDERS (BUSINESS OWNER)
create policy "Business owners can view orders made to their businesses"
on orders for select
using (
  auth.uid() in (
    select owner_id from businesses where businesses.id = orders.business_id
  )
);

-- ORDER ITEMS
create policy "Allow related access to order items"
on order_items for select
using (
  auth.uid() in (
    select customer_id from orders where orders.id = order_items.order_id
  )
  or auth.uid() in (
    select owner_id from businesses
    join orders on businesses.id = orders.business_id
    where orders.id = order_items.order_id
  )
);

-- ORDER STATUS TRACKING
create policy "Allow related access to order status tracking"
on order_status_tracking for select
using (
  auth.uid() in (
    select customer_id from orders where orders.id = order_status_tracking.order_id
  )
  or auth.uid() in (
    select owner_id from businesses
    join orders on businesses.id = orders.business_id
    where orders.id = order_status_tracking.order_id
  )
);

-- CHATBOT + VOICE
create policy "Allow access to chatbot sessions"
on chatbot_sessions for select
using (auth.uid() = user_id);

create policy "Allow access to voice orders"
on voice_orders for select
using (
  auth.uid() in (
    select customer_id from orders where orders.id = voice_orders.order_id
  )
);

-- ✅ USER AUTO-CREATION ON SIGNUP
create function public.handle_new_user()
returns trigger as $$
begin
  insert into public.users (id, email, full_name, role)
  values (
    new.id,
    new.email,
    coalesce(new.raw_user_meta_data->>'full_name', ''), -- Get full_name from user metadata
    coalesce(new.raw_user_meta_data->>'role', 'customer') -- Get role from user metadata, default to customer
  );
  return new;
end;
$$ language plpgsql security definer;

create trigger on_auth_user_created
after insert on auth.users
for each row execute procedure public.handle_new_user();
