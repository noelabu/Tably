import { User, LoginResponse, SignupResponse, RefreshTokenResponse } from '@/types/auth.types';
import { apiService } from './api';

export const authService = {
  async login(email: string, password: string): Promise<LoginResponse> {
    const params = new URLSearchParams();
    params.append('username', email);
    params.append('password', password);
    
    return apiService.post<LoginResponse>('/api/v1/auth/login', params, {
      headers: {
        'Content-Type': 'application/x-www-form-urlencoded',
      },
    });
  },

  async signup(email: string, password: string, fullName?: string, role?: 'customer' | 'business-owner'): Promise<SignupResponse> {
    return apiService.post<SignupResponse>('/api/v1/auth/signup', {
      email,
      password,
      full_name: fullName,
      role: role || 'customer',
    });
  },

  async logout(token: string): Promise<void> {
    return apiService.withAuth(token).post<void>('/api/v1/auth/logout');
  },

  async refreshToken(refreshToken: string): Promise<RefreshTokenResponse> {
    return apiService.post<RefreshTokenResponse>('/api/v1/auth/refresh', {
      refresh_token: refreshToken,
    });
  },

  async getCurrentUser(token: string): Promise<User> {
    return apiService.withAuth(token).get<User>('/api/v1/auth/me');
  },
};