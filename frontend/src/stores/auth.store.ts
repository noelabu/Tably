import { create } from 'zustand';
import { persist } from 'zustand/middleware';
import { authService } from '@/services/auth';
import { User, AuthTokens } from '@/types/auth.types';

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
          const response = await authService.login(email, password);
          const tokens = {
            access_token: response.access_token,
            refresh_token: response.refresh_token,
            token_type: response.token_type,
            expires_in: response.expires_in,
          };
          
          set({ tokens, isAuthenticated: true });
          
          const user = await authService.getCurrentUser(tokens.access_token);
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
          const response = await authService.signup(email, password, fullName, role);
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
            await authService.logout(tokens.access_token);
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
          const response = await authService.refreshToken(tokens.refresh_token);
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
          const user = await authService.getCurrentUser(tokens.access_token);
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