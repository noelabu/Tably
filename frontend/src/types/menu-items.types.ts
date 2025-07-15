export interface MenuItem {
  id: string;
  business_id: string;
  name: string;
  description?: string;
  price: number;
  image_url?: string;
  available: boolean;
  created_at: string;
  quantity?: number;
  stock_level?: {
    quantity_available: number;
    total_quantity: number;
  };
}

export interface MenuItemCreate {
  business_id: string;
  name: string;
  description?: string;
  price: number;
  image_url?: string;
  available?: boolean;
  quantity?: number;
  stock_level?: {
    quantity_available: number;
    total_quantity: number;
  }
}

export interface MenuItemUpdate {
  name?: string;
  description?: string;
  price?: number;
  image_url?: string;
  available?: boolean;
  quantity?: number;
}

export interface MenuItemsListResponse {
  items: MenuItem[];
  total: number;
  page: number;
  page_size: number;
}

export interface MenuItemDeleteResponse {
  message: string;
  deleted_id: string;
}

export interface MenuItemQueryParams {
  page?: number;
  page_size?: number;
  available_only?: boolean;
}