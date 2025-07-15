import { create } from 'zustand';
import { businessService } from '@/services/business';

interface BusinessState {
  isLoading: boolean;
  manageBusiness: (name: string, address: string, city: string, state: string, zip_code: string, phone: string, email: string, cuisine_type: string, open_time: string, close_time: string) => Promise<boolean>;
  getBusiness: () => Promise<import('@/types/business').Business | null>;
  updateBusiness: (id: string, name: string, address: string, city: string, state: string, zip_code: string, phone: string, email: string, cuisine_type: string, open_time: string, close_time: string) => Promise<boolean>;
}

export const useBusinessStore = create<BusinessState>(
  (set) => ({
    isLoading: false,

    manageBusiness: async (name: string, address: string, city: string, state: string, zip_code: string, phone: string, email: string, cuisine_type: string, open_time: string, close_time: string) => {
      set({ isLoading: true });
      
      try {
        const response = await businessService.manageBusiness(name, address, city, state, zip_code, phone, email, cuisine_type, open_time, close_time);
        set({ isLoading: false });
        return true;
      } catch (error) {
        console.error('Manage error:', error);
        set({ isLoading: false });
        return false;
      }
    },

    getBusiness: async () => {
      set({ isLoading: true });
      try {
        const business = await businessService.getBusiness();
        set({ isLoading: false });
        return business;
      } catch (error) {
        console.error('Get business error:', error);
        set({ isLoading: false });
        return null;
      }
    },

    updateBusiness: async (id: string, name: string, address: string, city: string, state: string, zip_code: string, phone: string, email: string, cuisine_type: string, open_time: string, close_time: string) => {
      set({ isLoading: true });
      try {
        const response = await businessService.updateBusiness(id, name, address, city, state, zip_code, phone, email, cuisine_type, open_time, close_time);
        set({ isLoading: false });
        return true;
      } catch (error) {
        console.error('Update business error:', error);
        set({ isLoading: false });
        return false;
      }
    }
  })
);
