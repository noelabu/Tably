import { create } from 'zustand';
import { menuItemsService } from '@/services/menu-items';
import { MenuItem, MenuItemCreate, MenuItemUpdate, MenuItemQueryParams } from '@/types/menu-items.types';
import { useAuthStore } from '@/stores/auth.store';

interface MenuItemsState {
  isLoading: boolean;
  menuItems: MenuItem[];
  total: number;
  page: number;
  pageSize: number;
  getMenuItems: (businessId: string, params?: MenuItemQueryParams) => Promise<void>;
  createMenuItem: (menuItem: MenuItemCreate) => Promise<void>;
  updateMenuItem: (menuItemId: string, updates: MenuItemUpdate) => Promise<void>;
  deleteMenuItem: (menuItemId: string) => Promise<void>;
}

export const useMenuItemsStore = create<MenuItemsState>((set, get) => ({
  isLoading: false,
  menuItems: [],
  total: 0,
  page: 1,
  pageSize: 20,

  getMenuItems: async (businessId: string, params?: MenuItemQueryParams) => {
    set({ isLoading: true });
    try {
      const token = useAuthStore.getState().tokens?.access_token;
      if (!token) throw new Error('No auth token');
      const response = await menuItemsService.getMenuItemsByBusiness(token, businessId, params);
      set({ menuItems: response.items, total: response.total, page: response.page, pageSize: response.page_size });
    } catch (error) {
      console.error('Error fetching menu items:', error);
    } finally {
      set({ isLoading: false });
    }
  },

  createMenuItem: async (menuItem: MenuItemCreate) => {
    set({ isLoading: true });
    try {
      const token = useAuthStore.getState().tokens?.access_token;
      if (!token) throw new Error('No auth token');
      const response = await menuItemsService.createMenuItem(token, menuItem);
      set({ menuItems: [...get().menuItems, response] });
    } catch (error) {
      console.error('Error creating menu item:', error);
    } finally {
      set({ isLoading: false });
    }
  },

  updateMenuItem: async (menuItemId: string, updates: MenuItemUpdate) => {
    set({ isLoading: true });
    try {
      const token = useAuthStore.getState().tokens?.access_token;
      if (!token) throw new Error('No auth token');
      const response = await menuItemsService.updateMenuItem(token, menuItemId, updates);
      set({ menuItems: get().menuItems.map(item => item.id === menuItemId ? response : item) });
    } catch (error) {
      console.error('Error updating menu item:', error);
    } finally {
      set({ isLoading: false });
    }
  },
  deleteMenuItem: async (menuItemId: string) => {
    set({ isLoading: true });
    try {
      const token = useAuthStore.getState().tokens?.access_token;
      if (!token) throw new Error('No auth token');
      await menuItemsService.deleteMenuItem(token, menuItemId);
      set({ menuItems: get().menuItems.filter(item => item.id !== menuItemId) });
    } catch (error) {
      console.error('Error deleting menu item:', error);
    } finally {
      set({ isLoading: false });
    }
  }
}));