import { apiService } from './api';
import {
  Order,
  OrderCreate,
  OrderUpdate,
  OrdersListResponse,
  OrderDeleteResponse
} from '@/types/orders';

export const ordersService = {
  // Create a new order
  async createOrder(order: OrderCreate): Promise<Order> {
    return apiService.authPostWithStore<Order>('/api/v1/orders/', order);
  },

  // Get orders for the current customer
  async getCustomerOrders(
    page: number = 1,
    page_size: number = 20,
    status_filter?: string
  ): Promise<OrdersListResponse> {
    const queryParams = new URLSearchParams();
    queryParams.append('page', page.toString());
    queryParams.append('page_size', page_size.toString());
    if (status_filter) {
      queryParams.append('status_filter', status_filter);
    }
    
    const queryString = queryParams.toString();
    const url = `/api/v1/orders/customer/me${queryString ? `?${queryString}` : ''}`;
    
    return apiService.authGetWithStore<OrdersListResponse>(url);
  },

  // Get a specific order by ID
  async getOrder(orderId: string): Promise<Order> {
    return apiService.authGetWithStore<Order>(`/api/v1/orders/${orderId}`);
  },

  // Update an order
  async updateOrder(orderId: string, updates: OrderUpdate): Promise<Order> {
    return apiService.authPatchWithStore<Order>(`/api/v1/orders/${orderId}`, updates);
  },

  // Delete an order
  async deleteOrder(orderId: string): Promise<OrderDeleteResponse> {
    return apiService.authDeleteWithStore<OrderDeleteResponse>(`/api/v1/orders/${orderId}`);
  }
}; 