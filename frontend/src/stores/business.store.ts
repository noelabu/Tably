import { create } from 'zustand';
import { businessService } from '@/services/business';
import { ManageRequest } from '@/types/business';

interface BusinessState {
  isLoading: boolean;
  manage: (name: string, address: string, city: string, state: string, zip_code: string, phone: string, email: string, cuisine_type: string, open_time: string, close_time: string) => Promise<boolean>;
}

export const useBusinessStore = create<BusinessState>(
  (set) => ({
    isLoading: false,

    manage: async (name: string, address: string, city: string, state: string, zip_code: string, phone: string, email: string, cuisine_type: string, open_time: string, close_time: string) => {
      set({ isLoading: true });
      
      try {
        const response = await businessService.manage(name, address, city, state, zip_code, phone, email, cuisine_type, open_time, close_time);
        set({ isLoading: false });
        return true;
      } catch (error) {
        console.error('Manage error:', error);
        set({ isLoading: false });
        return false;
      }
    }
  })
);
