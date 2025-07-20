import { create } from 'zustand';
import type { MenuItem } from '@/types/menu-items.types';

export type CartItem = MenuItem & { quantity: number; customizations?: string[] };

interface CartState {
  items: CartItem[];
  businessId: string | null;
  setBusinessId: (id: string) => void;
  addToCart: (item: MenuItem) => void;
  updateQuantity: (id: string, change: number) => void;
  removeFromCart: (id: string) => void;
  clearCart: () => void;
}

export const useCartStore = create<CartState>((set) => ({
  items: [],
  businessId: null,
  setBusinessId: (id) => set({ businessId: id }),
  addToCart: (item) => set((state) => {
    const existing = state.items.find((i) => i.id === item.id);
    if (existing) {
      return {
        items: state.items.map((i) =>
          i.id === item.id ? { ...i, quantity: i.quantity + 1 } : i
        ),
      };
    } else {
      return { items: [...state.items, { ...item, quantity: 1 }] };
    }
  }),
  updateQuantity: (id, change) => set((state) => ({
    items: state.items
      .map((item) =>
        item.id === id
          ? { ...item, quantity: Math.max(0, item.quantity + change) }
          : item
      )
      .filter((item) => item.quantity > 0),
  })),
  removeFromCart: (id) => set((state) => ({
    items: state.items.filter((item) => item.id !== id),
  })),
  clearCart: () => set({ items: [], businessId: null }),
})); 