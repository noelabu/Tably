import { create } from 'zustand';
import { persist } from 'zustand/middleware';

export interface User {
  id: string;
  email: string;
  full_name?: string;
  role: 'customer' | 'business-owner';
  created_at?: string;
}

interface AuthTokens {
  access_token: string;
  refresh_token?: string;
  token_type: string;
  expires_in?: number;
}

interface AuthState {
  user: User | null;
  tokens: AuthTokens | null;
  isAuthenticated: boolean;
  isLoading: boolean;
  
  login: (email: string, password: string) => Promise<boolean>;
  signup: (email: string, password: string, fullName?: string, role?: 'customer' | 'business-owner') => Promise<boolean>;
  logout: () => Promise<void>;
  refreshToken: () => Promise<boolean>;
  getCurrentUser: () => Promise<User | null>;
  
  setUser: (user: User | null) => void;
  setTokens: (tokens: AuthTokens | null) => void;
  setLoading: (loading: boolean) => void;
}

const API_BASE_URL = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000';

const authApi = {
  async login(email: string, password: string) {
    const params = new URLSearchParams();
    params.append('username', email);
    params.append('password', password);
    
    const response = await fetch(`${API_BASE_URL}/api/v1/auth/login`, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/x-www-form-urlencoded',
      },
      body: params.toString(),
    });
    
    if (!response.ok) {
      const errorData = await response.json().catch(() => ({}));
      throw new Error(errorData.detail || 'Login failed');
    }
    
    return response.json();
  },

  async signup(email: string, password: string, fullName?: string, role?: 'customer' | 'business-owner') {
    const response = await fetch(`${API_BASE_URL}/api/v1/auth/signup`, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
      },
      body: JSON.stringify({
        email,
        password,
        full_name: fullName,
        role: role || 'customer',
      }),
    });
    
    if (!response.ok) {
      throw new Error('Signup failed');
    }
    
    return response.json();
  },

  async logout(token: string) {
    const response = await fetch(`${API_BASE_URL}/api/v1/auth/logout`, {
      method: 'POST',
      headers: {
        'Authorization': `Bearer ${token}`,
      },
    });
    
    if (!response.ok) {
      throw new Error('Logout failed');
    }
    
    return response.json();
  },

  async refreshToken(refreshToken: string) {
    const response = await fetch(`${API_BASE_URL}/api/v1/auth/refresh`, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
      },
      body: JSON.stringify({
        refresh_token: refreshToken,
      }),
    });
    
    if (!response.ok) {
      throw new Error('Token refresh failed');
    }
    
    return response.json();
  },

  async getCurrentUser(token: string) {
    const response = await fetch(`${API_BASE_URL}/api/v1/auth/me`, {
      method: 'GET',
      headers: {
        'Authorization': `Bearer ${token}`,
      },
    });
    
    if (!response.ok) {
      throw new Error('Failed to get current user');
    }
    
    return response.json();
  },
};

export const useAuthStore = create<AuthState>()(
  persist(
    (set, get) => ({
      user: null,
      tokens: null,
      isAuthenticated: false,
      isLoading: false,

      login: async (email: string, password: string) => {
        set({ isLoading: true });
        try {
          const response = await authApi.login(email, password);
          const tokens = {
            access_token: response.access_token,
            refresh_token: response.refresh_token,
            token_type: response.token_type,
            expires_in: response.expires_in,
          };
          
          set({ tokens, isAuthenticated: true });
          
          const user = await authApi.getCurrentUser(tokens.access_token);
          set({ user, isLoading: false });
          
          return true;
        } catch (error) {
          console.error('Login error:', error);
          set({ isLoading: false });
          return false;
        }
      },

      signup: async (email: string, password: string, fullName?: string, role?: 'customer' | 'business-owner') => {
        set({ isLoading: true });
        try {
          const response = await authApi.signup(email, password, fullName, role);
          const tokens = {
            access_token: response.access_token,
            refresh_token: response.refresh_token,
            token_type: response.token_type,
            expires_in: response.expires_in,
          };
          
          set({ 
            tokens, 
            user: response.user, 
            isAuthenticated: true, 
            isLoading: false 
          });
          
          return true;
        } catch (error) {
          console.error('Signup error:', error);
          set({ isLoading: false });
          return false;
        }
      },

      logout: async () => {
        const { tokens } = get();
        if (tokens?.access_token) {
          try {
            await authApi.logout(tokens.access_token);
          } catch (error) {
            console.error('Logout error:', error);
          }
        }
        
        set({ 
          user: null, 
          tokens: null, 
          isAuthenticated: false, 
          isLoading: false 
        });
      },

      refreshToken: async () => {
        const { tokens } = get();
        if (!tokens?.refresh_token) {
          return false;
        }
        
        try {
          const response = await authApi.refreshToken(tokens.refresh_token);
          const newTokens = {
            access_token: response.access_token,
            refresh_token: response.refresh_token,
            token_type: response.token_type,
            expires_in: response.expires_in,
          };
          
          set({ tokens: newTokens, user: response.user });
          return true;
        } catch (error) {
          console.error('Token refresh error:', error);
          set({ 
            user: null, 
            tokens: null, 
            isAuthenticated: false 
          });
          return false;
        }
      },

      getCurrentUser: async () => {
        const { tokens } = get();
        if (!tokens?.access_token) {
          return null;
        }
        
        try {
          const user = await authApi.getCurrentUser(tokens.access_token);
          set({ user });
          return user;
        } catch (error) {
          console.error('Get current user error:', error);
          return null;
        }
      },

      setUser: (user: User | null) => {
        set({ user, isAuthenticated: !!user });
      },

      setTokens: (tokens: AuthTokens | null) => {
        set({ tokens, isAuthenticated: !!tokens });
      },

      setLoading: (loading: boolean) => {
        set({ isLoading: loading });
      },
    }),
    {
      name: 'auth-storage',
      partialize: (state) => ({
        user: state.user,
        tokens: state.tokens,
        isAuthenticated: state.isAuthenticated,
      }),
    }
  )
);