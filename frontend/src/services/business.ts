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

  // Get all businesses for customers to browse
  async getAllBusinesses(
    page: number = 1,
    page_size: number = 20
  ): Promise<{ items: Business[]; total: number; page: number; page_size: number }> {
    const queryParams = new URLSearchParams();
    queryParams.append('page', page.toString());
    queryParams.append('page_size', page_size.toString());
    
    const queryString = queryParams.toString();
    const url = `/api/v1/business${queryString ? `?${queryString}` : ''}`;
    
    return apiService.authGetWithStore<{ items: Business[]; total: number; page: number; page_size: number }>(url);
  },

  // Get a business by its ID (for customer browsing)
  async getBusinessById(id: string): Promise<Business> {
    return apiService.authGetWithStore<Business>(`/api/v1/business/${id}`);
  },
};  