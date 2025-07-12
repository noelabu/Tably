import { Business, ManageRequest } from '@/types/business';
import { apiService } from './api';

export const businessService = {
  async manage(name: string, address: string, city: string, state: string, zip_code: string, phone: string, email: string, cuisine_type: string, open_time: string, close_time: string): Promise<ManageRequest> {
    return apiService.post<ManageRequest>('/api/v1/business/manage', {
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