import axios from 'axios';
import type { AxiosRequestConfig } from 'axios';
import { useAuthStore } from '@/stores/auth.store';

export const API_BASE_URL = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000';

export class ApiError extends Error {
  constructor(
    message: string,
    public status: number,
    public data?: any
  ) {
    super(message);
    this.name = 'ApiError';
  }
}

const axiosInstance = axios.create({
  baseURL: API_BASE_URL,
});

interface ApiService {
  request<T>(url: string, config?: AxiosRequestConfig): Promise<T>;
  get<T>(url: string, config?: AxiosRequestConfig): Promise<T>;
  post<T>(url: string, data?: any, config?: AxiosRequestConfig): Promise<T>;
  put<T>(url: string, data?: any, config?: AxiosRequestConfig): Promise<T>;
  delete<T>(url: string, config?: AxiosRequestConfig): Promise<T>;
  withAuth(token: string): ApiService;
  // Authenticated request methods
  authGet<T>(url: string, token: string, config?: AxiosRequestConfig): Promise<T>;
  authPost<T>(url: string, token: string, data?: any, config?: AxiosRequestConfig): Promise<T>;
  authPut<T>(url: string, token: string, data?: any, config?: AxiosRequestConfig): Promise<T>;
  authDelete<T>(url: string, token: string, config?: AxiosRequestConfig): Promise<T>;
  // Helper methods to get token from auth store
  getAuthToken(): string | null;
  authGetWithStore<T>(url: string, config?: AxiosRequestConfig): Promise<T>;
  authPostWithStore<T>(url: string, data?: any, config?: AxiosRequestConfig): Promise<T>;
  authPutWithStore<T>(url: string, data?: any, config?: AxiosRequestConfig): Promise<T>;
  authDeleteWithStore<T>(url: string, config?: AxiosRequestConfig): Promise<T>;
}

export const apiService: ApiService = {
  async request<T>(url: string, config: AxiosRequestConfig = {}): Promise<T> {
    try {
      const response = await axiosInstance.request<T>({
        url,
        ...config,
      });
      return response.data;
    } catch (error) {
      if (axios.isAxiosError(error)) {
        throw new ApiError(
          error.response?.data?.detail || error.message || 'Request failed',
          error.response?.status || 500,
          error.response?.data
        );
      }
      throw error;
    }
  },

  async get<T>(url: string, config?: AxiosRequestConfig): Promise<T> {
    return this.request<T>(url, {
      ...config,
      method: 'GET',
    });
  },

  async post<T>(url: string, data?: any, config?: AxiosRequestConfig): Promise<T> {
    const isFormData = data instanceof FormData;
    const isURLSearchParams = data instanceof URLSearchParams;
    
    return this.request<T>(url, {
      ...config,
      method: 'POST',
      data,
      headers: {
        ...(!isFormData && !isURLSearchParams && { 'Content-Type': 'application/json' }),
        ...config?.headers,
      },
    });
  },

  async put<T>(url: string, data?: any, config?: AxiosRequestConfig): Promise<T> {
    return this.request<T>(url, {
      ...config,
      method: 'PUT',
      data,
      headers: {
        'Content-Type': 'application/json',
        ...config?.headers,
      },
    });
  },

  async delete<T>(url: string, config?: AxiosRequestConfig): Promise<T> {
    return this.request<T>(url, {
      ...config,
      method: 'DELETE',
    });
  },

  withAuth(token: string): ApiService {
    const authApiService = Object.create(this);
    
    authApiService.request = async <T>(url: string, config: AxiosRequestConfig = {}): Promise<T> => {
      return this.request<T>(url, {
        ...config,
        headers: {
          ...config.headers,
          'Authorization': `Bearer ${token}`,
        },
      });
    };
    
    return authApiService;
  },

  // Authenticated request methods
  async authGet<T>(url: string, token: string, config?: AxiosRequestConfig): Promise<T> {
    return this.request<T>(url, {
      ...config,
      headers: {
        ...config?.headers,
        'Authorization': `Bearer ${token}`,
      },
    });
  },

  async authPost<T>(url: string, token: string, data?: any, config?: AxiosRequestConfig): Promise<T> {
    const isFormData = data instanceof FormData;
    const isURLSearchParams = data instanceof URLSearchParams;

    return this.request<T>(url, {
      ...config,
      method: 'POST',
      data,
      headers: {
        ...(!isFormData && !isURLSearchParams && { 'Content-Type': 'application/json' }),
        ...config?.headers,
        'Authorization': `Bearer ${token}`,
      },
    });
  },

  async authPut<T>(url: string, token: string, data?: any, config?: AxiosRequestConfig): Promise<T> {
    return this.request<T>(url, {
      ...config,
      method: 'PUT',
      data,
      headers: {
        'Content-Type': 'application/json',
        ...config?.headers,
        'Authorization': `Bearer ${token}`,
      },
    });
  },

  async authDelete<T>(url: string, token: string, config?: AxiosRequestConfig): Promise<T> {
    return this.request<T>(url, {
      ...config,
      method: 'DELETE',
      headers: {
        'Authorization': `Bearer ${token}`,
      },
    });
  },

  // Helper methods to get token from auth store
  getAuthToken(): string | null {
    const authStore = useAuthStore.getState();
    return authStore.tokens?.access_token || null;
  },

  async authGetWithStore<T>(url: string, config?: AxiosRequestConfig): Promise<T> {
    const token = this.getAuthToken();
    if (!token) {
      throw new Error('No authentication token found in store.');
    }
    return this.authGet<T>(url, token, config);
  },

  async authPostWithStore<T>(url: string, data?: any, config?: AxiosRequestConfig): Promise<T> {
    const token = this.getAuthToken();
    if (!token) {
      throw new Error('No authentication token found in store.');
    }
    const isFormData = data instanceof FormData;
    const isURLSearchParams = data instanceof URLSearchParams;

    return this.authPost<T>(url, token, data, config);
  },

  async authPutWithStore<T>(url: string, data?: any, config?: AxiosRequestConfig): Promise<T> {
    const token = this.getAuthToken();
    if (!token) {
      throw new Error('No authentication token found in store.');
    }
    return this.authPut<T>(url, token, data, config);
  },

  async authDeleteWithStore<T>(url: string, config?: AxiosRequestConfig): Promise<T> {
    const token = this.getAuthToken();
    if (!token) {
      throw new Error('No authentication token found in store.');
    }
    return this.authDelete<T>(url, token, config);
  },
};