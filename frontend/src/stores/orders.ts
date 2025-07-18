import { create } from 'zustand';
import { ordersService } from '@/services/orders';
import { Order, OrderCreate, OrdersListResponse } from '@/types/orders';

interface OrderState {
  isLoading: boolean;
  createOrder: (order: OrderCreate) => Promise<boolean>;
  getCustomerOrders: (page: number, page_size: number, status_filter?: string) => Promise<OrdersListResponse | null>;
  getOrder: (orderId: string) => Promise<Order | null>;
  getOrdersByBusiness: (businessId: string, page?: number, page_size?: number, status_filter?: string) => Promise<OrdersListResponse | null>;
  getOrderWithItems: (orderId: string) => Promise<any | null>;
  updateOrder: (orderId: string, updates: Partial<Order>) => Promise<Order | null>;
}

export const useOrderStore = create<OrderState>(
  (set) => ({
    isLoading: false,
    createOrder: async (order: OrderCreate) => {
      set({ isLoading: true });
      try {
        const response = await ordersService.createOrder(order);
        set({ isLoading: false });
        return true;
      } catch (error) {
        console.error('Create order error:', error);
        set({ isLoading: false });
        return false;
      }
    },
    getCustomerOrders: async (page: number = 1, page_size: number = 20, status_filter?: string) => {
      set({ isLoading: true });
      try {
        const response = await ordersService.getCustomerOrders(page, page_size, status_filter);
        set({ isLoading: false });
        return response;
      } catch (error) {
        console.error('Get customer orders error:', error);
        set({ isLoading: false });
        return null;
      }
    },
    getOrder: async (orderId: string) => {
      set({ isLoading: true });
      try {
        const response = await ordersService.getOrder(orderId);
        set({ isLoading: false });
        return response;
      } catch (error) {
        console.error('Get order error:', error);
        set({ isLoading: false });
        return null;
      }
    },
    getOrdersByBusiness: async (businessId: string, page: number = 1, page_size: number = 20, status_filter?: string) => {
      set({ isLoading: true });
      try {
        const response = await ordersService.getOrdersByBusiness(businessId, page, page_size, status_filter);
        set({ isLoading: false });
        return response;
      } catch (error) {
        console.error('Get orders by business error:', error);
        set({ isLoading: false });
        return null;
      }
    },
    getOrderWithItems: async (orderId: string) => {
      set({ isLoading: true });
      try {
        const res = await fetch(`/api/v1/orders/with-items/${orderId}`);
        if (res.ok) {
          const data = await res.json();
          set({ isLoading: false });
          return data;
        } else {
          set({ isLoading: false });
          return null;
        }
      } catch (error) {
        set({ isLoading: false });
        return null;
      }
    },
    updateOrder: async (orderId: string, updates: Partial<Order>) => {
      set({ isLoading: true });
      try {
        const updatedOrder = await ordersService.updateOrder(orderId, updates);
        set({ isLoading: false });
        return updatedOrder;
      } catch (error) {
        console.error('Update order error:', error);
        set({ isLoading: false });
        return null;
      }
    },
  })
)
