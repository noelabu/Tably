import { create } from 'zustand';
import { ordersService } from '@/services/orders';
import { OrderCreate } from '@/types/orders';

interface OrderState {
  isLoading: boolean;
  createOrder: (order: OrderCreate) => Promise<boolean>;
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
    }
  })
)
