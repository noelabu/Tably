import { useAuthStore } from '@/lib/auth-store'

export const useAuth = () => {
  const store = useAuthStore()
  
  return {
    user: store.user,
    isAuthenticated: store.isAuthenticated,
    isLoading: store.isLoading,
    login: store.login,
    signup: store.signup,
    logout: store.logout,
    refreshToken: store.refreshToken,
    getCurrentUser: store.getCurrentUser,
  }
}