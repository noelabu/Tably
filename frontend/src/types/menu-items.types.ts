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
  category?: string;
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
  };
  category?: string;
}

export interface MenuItemUpdate {
  name?: string;
  description?: string;
  price?: number;
  image_url?: string;
  available?: boolean;
  quantity?: number;
  category?: string;
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

export interface ExtractedMenuItem {
  name: string;
  description?: string;
  price?: number;
  category?: string;
  allergens?: string[];
  ingredients?: string[];
  modifiers?: any[];
  combos?: any[];
  sizes?: any[];
  quantity?: number;
}

export interface MenuImageAnalysisResult {
  restaurant_info?: {
    restaurant_name?: string;
    cuisine_type?: string;
  };
  menu_items: ExtractedMenuItem[];
  total_items: number;
  analysis_confidence?: number;
}