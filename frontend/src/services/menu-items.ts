import { apiService } from './api';
import {
  MenuItem,
  MenuItemCreate,
  MenuItemUpdate,
  MenuItemsListResponse,
  MenuItemDeleteResponse,
  MenuItemQueryParams
} from '@/types/menu-items.types';

export const menuItemsService = {
  // Create a new menu item
  async createMenuItem(token: string, menuItem: MenuItemCreate): Promise<MenuItem> {
    return apiService.withAuth(token).post<MenuItem>('/api/v1/menu-items/', menuItem);
  },

  // Get menu items for a specific business
  async getMenuItemsByBusiness(
    token: string, 
    businessId: string, 
    params?: MenuItemQueryParams
  ): Promise<MenuItemsListResponse> {
    const queryParams = new URLSearchParams();
    
    if (params?.page) queryParams.append('page', params.page.toString());
    if (params?.page_size) queryParams.append('page_size', params.page_size.toString());
    if (params?.available_only) queryParams.append('available_only', params.available_only.toString());
    
    const queryString = queryParams.toString();
    const url = `/api/v1/menu-items/business/${businessId}${queryString ? `?${queryString}` : ''}`;
    
    return apiService.withAuth(token).get<MenuItemsListResponse>(url);
  },

  // Get a specific menu item by ID
  async getMenuItem(token: string, menuItemId: string): Promise<MenuItem> {
    return apiService.withAuth(token).get<MenuItem>(`/api/v1/menu-items/${menuItemId}`);
  },

  // Update a menu item (partial update)
  async updateMenuItem(
    token: string, 
    menuItemId: string, 
    updates: MenuItemUpdate
  ): Promise<MenuItem> {
    return apiService.withAuth(token).patch<MenuItem>(`/api/v1/menu-items/${menuItemId}`, updates);
  },

  // Delete a menu item
  async deleteMenuItem(token: string, menuItemId: string): Promise<MenuItemDeleteResponse> {
    return apiService.withAuth(token).delete<MenuItemDeleteResponse>(`/api/v1/menu-items/${menuItemId}`);
  },

  // Toggle menu item availability (convenience method)
  async toggleMenuItemAvailability(
    token: string, 
    menuItemId: string, 
    available: boolean
  ): Promise<MenuItem> {
    return this.updateMenuItem(token, menuItemId, { available });
  },

  // Bulk update menu items availability
  async bulkUpdateAvailability(
    token: string, 
    menuItemIds: string[], 
    available: boolean
  ): Promise<MenuItem[]> {
    const promises = menuItemIds.map(id => 
      this.updateMenuItem(token, id, { available })
    );
    return Promise.all(promises);
  }
};