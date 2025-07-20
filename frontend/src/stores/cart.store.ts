import { create } from 'zustand';
import type { MenuItem } from '@/types/menu-items.types';

export type CartItem = MenuItem & { quantity: number; customizations?: string[] };

// Voice agent cart item structure
export interface VoiceCartItem {
  menu_item_id: string;
  name: string;
  quantity: number;
  unit_price: number;
  special_instructions?: string;
}

// Voice agent cart event structure
export interface VoiceCartEvent {
  type: 'cart_updated';
  action: 'add' | 'remove' | 'update' | 'clear';
  item?: VoiceCartItem;
  cart_items: VoiceCartItem[];
  cart_total: number;
  item_count: number;
}

interface CartState {
  items: CartItem[];
  businessId: string | null;
  isVoiceSync: boolean; // Flag to prevent infinite loops during voice sync
  setBusinessId: (id: string) => void;
  addToCart: (item: MenuItem) => void;
  updateQuantity: (id: string, change: number) => void;
  removeFromCart: (id: string) => void;
  clearCart: () => void;
  // Voice synchronization methods
  syncFromVoice: (voiceCartEvent: VoiceCartEvent) => void;
  setVoiceSync: (isSync: boolean) => void;
}

// Helper function to convert voice cart item to frontend cart item
const convertVoiceItemToCartItem = (voiceItem: VoiceCartItem): CartItem => ({
  id: voiceItem.menu_item_id,
  name: voiceItem.name,
  price: voiceItem.unit_price,
  description: voiceItem.special_instructions || '',
  category: 'Voice Order',
  business_id: '', // Will be set by businessId
  available: true,
  quantity: voiceItem.quantity,
  customizations: voiceItem.special_instructions ? [voiceItem.special_instructions] : undefined,
});

export const useCartStore = create<CartState>((set, get) => ({
  items: [],
  businessId: null,
  isVoiceSync: false,
  
  setBusinessId: (id) => set({ businessId: id }),
  
  setVoiceSync: (isSync) => set({ isVoiceSync: isSync }),
  
  addToCart: (item) => set((state) => {
    // Don't emit changes during voice sync to prevent loops
    if (state.isVoiceSync) {
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
    }
    
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
  
  clearCart: () => set((state) => ({
    items: [],
    businessId: state.isVoiceSync ? state.businessId : null, // Keep businessId during voice sync
  })),
  
  syncFromVoice: (voiceCartEvent: VoiceCartEvent) => {
    const state = get();
    
    // Set voice sync flag to prevent infinite loops
    set({ isVoiceSync: true });
    
    try {
      // Convert voice cart items to frontend cart items
      const convertedItems = voiceCartEvent.cart_items.map(voiceItem => ({
        ...convertVoiceItemToCartItem(voiceItem),
        business_id: state.businessId || '',
      }));
      
      // Update cart with voice agent's cart state
      set({
        items: convertedItems,
        isVoiceSync: false, // Reset sync flag
      });
      
      console.log(`Cart synced from voice: ${voiceCartEvent.action}`, {
        action: voiceCartEvent.action,
        item: voiceCartEvent.item,
        cartTotal: voiceCartEvent.cart_total,
        itemCount: voiceCartEvent.item_count,
        cartItems: convertedItems,
      });
      
    } catch (error) {
      console.error('Error syncing cart from voice:', error);
      set({ isVoiceSync: false }); // Reset sync flag on error
    }
  },
})); 