export interface OrderItem {
  id: string;
  order_id: string;
  menu_item_id: string;
  quantity: number;
  special_instructions?: string;
  created_at: string;
  menu_item?: {
    id: string;
    name: string;
    description?: string;
    price: number;
    image_url?: string;
  };
}

// Type for order item creation (frontend -> backend)
export interface OrderItemCreate {
  menu_item_id: string;
  quantity: number;
  price_at_order: number;
}

export interface Order {
  id: string;
  business_id: string;
  customer_id: string;
  status: 'pending' | 'confirmed' | 'preparing' | 'ready' | 'completed' | 'cancelled';
  total_amount: number;
  special_instructions?: string;
  pickup_time?: string;
  created_at: string;
  updated_at: string;
  items: OrderItem[];
  business?: {
    id: string;
    name: string;
    address: string;
    city: string;
    state: string;
    phone: string;
  };
}

export interface OrderCreate {
  business_id: string;
  total_amount: number;
  status?: string;
  order_items: OrderItemCreate[];
}

export interface OrderUpdate {
  status?: 'pending' | 'confirmed' | 'preparing' | 'ready' | 'completed' | 'cancelled';
  special_instructions?: string;
  pickup_time?: string;
}

export interface OrdersListResponse {
  items: Order[];
  total: number;
  page: number;
  page_size: number;
}

export interface OrderDeleteResponse {
  message: string;
  deleted_id: string;
} 