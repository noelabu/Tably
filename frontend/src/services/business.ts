import { Business, ManageRequest } from '@/types/business';
import { apiService } from './api';

export const businessService = {
  async manageBusiness(
    name: string,
    address: string,
    city: string,
    state: string,
    zip_code: string,
    phone: string,
    email: string,
    cuisine_type: string,
    open_time: string,
    close_time: string
  ): Promise<Business> {
    return apiService.authPostWithStore<Business>('/api/v1/business', {
      name,
      address,
      city,
      state,
      zip_code,
      phone,
      email,
      cuisine_type,
      open_time,
      close_time,
    });
  },

  async getBusiness(): Promise<Business> {
    return apiService.authGetWithStore<Business>('/api/v1/business/my');
  },

  async updateBusiness(id: string, name: string, address: string, city: string, state: string, zip_code: string, phone: string, email: string, cuisine_type: string, open_time: string, close_time: string): Promise<Business> {
    return apiService.authPatchWithStore<Business>(`/api/v1/business/${id}`, {
      name,
      address,
      city,
      state,
      zip_code,
      phone,
      email,
      cuisine_type,
      open_time,
      close_time,
    });
  },
};  