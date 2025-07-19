import { create } from 'zustand';
import { persist } from 'zustand/middleware';
import { businessService } from '@/services/business';
import { Business, ManageRequest } from '@/types/business';

interface BusinessState {
  isLoading: boolean;
  business: Business | null;
  manageBusiness: (business: ManageRequest) => Promise<boolean>;
  getBusiness: () => Promise<Business | null>;
  updateBusiness: (business: Business) => Promise<boolean>;
}

export const useBusinessStore = create<BusinessState>()(
  persist(
    (set, get) => ({
      isLoading: false,
      business: null,

      manageBusiness: async (business: ManageRequest) => {
        set({ isLoading: true });
        try {
          const response = await businessService.manageBusiness(business);
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
          set({ isLoading: false, business: business });
          return business;
        } catch (error) {
          console.error('Get business error:', error);
          set({ isLoading: false });
          return null;
        }
      },

      updateBusiness: async (business: Business) => {
        set({ isLoading: true });
        try {
          const response = await businessService.updateBusiness(business);
          set({ isLoading: false });
          return true;
        } catch (error) {
          console.error('Update business error:', error);
          set({ isLoading: false });
          return false;
        }
      }
    }),
    {
      name: 'business-store',
      partialize: (state) => ({
        business: state.business,
      }),
    }
  )
);
