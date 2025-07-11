'use client'

import { useEffect } from 'react'
import { useRouter } from 'next/navigation'
import { useAuthStore } from '@/lib/auth-store'

interface AuthGuardProps {
  children: React.ReactNode
  requireAuth?: boolean
  redirectTo?: string
  allowedRoles?: ('customer' | 'business-owner')[]
}

export default function AuthGuard({ 
  children, 
  requireAuth = true, 
  redirectTo = '/login',
  allowedRoles
}: AuthGuardProps) {
  const { isAuthenticated, isLoading, user } = useAuthStore()
  const router = useRouter()

  useEffect(() => {
    if (!isLoading) {
      if (requireAuth && !isAuthenticated) {
        router.push(redirectTo)
      } else if (!requireAuth && isAuthenticated) {
        // Redirect authenticated users to their role-specific dashboard
        if (user?.role === 'business-owner') {
          router.push('/business/dashboard')
        } else {
          router.push('/customer/dashboard')
        }
      } else if (requireAuth && isAuthenticated && allowedRoles && user?.role) {
        // Check if user has the required role
        if (!allowedRoles.includes(user.role)) {
          // Redirect to their appropriate dashboard
          if (user.role === 'business-owner') {
            router.push('/business/dashboard')
          } else {
            router.push('/customer/dashboard')
          }
        }
      }
    }
  }, [isAuthenticated, isLoading, requireAuth, redirectTo, allowedRoles, user, router])

  if (isLoading) {
    return (
      <div className="min-h-screen flex items-center justify-center">
        <div className="animate-spin rounded-full h-8 w-8 border-b-2 border-primary"></div>
      </div>
    )
  }

  if (requireAuth && !isAuthenticated) {
    return null
  }

  if (!requireAuth && isAuthenticated) {
    return null
  }

  if (requireAuth && isAuthenticated && allowedRoles && user?.role && !allowedRoles.includes(user.role)) {
    return null
  }

  return <>{children}</>
}