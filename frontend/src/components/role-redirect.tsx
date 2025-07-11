'use client'

import { useEffect } from 'react'
import { useRouter } from 'next/navigation'
import { useAuth } from '@/hooks/use-auth'

export default function RoleRedirect() {
  const { user, isAuthenticated, isLoading } = useAuth()
  const router = useRouter()

  useEffect(() => {
    if (!isLoading && isAuthenticated && user) {
      if (user.role === 'business-owner') {
        router.push('/business/dashboard')
      } else {
        router.push('/customer/dashboard')
      }
    } else if (!isLoading && !isAuthenticated) {
      router.push('/login')
    }
  }, [user, isAuthenticated, isLoading, router])

  if (isLoading) {
    return (
      <div className="min-h-screen flex items-center justify-center">
        <div className="animate-spin rounded-full h-8 w-8 border-b-2 border-primary"></div>
      </div>
    )
  }

  return null
}