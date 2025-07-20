'use client'

import { useAuth } from '@/hooks/use-auth'
import { Button } from '@/components/ui/button'
import { useRouter } from 'next/navigation'

interface RoleBasedNavProps {
  className?: string
}

export default function RoleBasedNav({ className }: RoleBasedNavProps) {
  const { user, logout } = useAuth()
  const router = useRouter()

  const handleLogout = async () => {
    await logout()
    router.push('/login')
  }

  if (!user) return null

  return (
    <nav className={`flex items-center space-x-4 ${className}`}>
      <div className="flex items-center space-x-2">
        <span className="text-sm text-muted-foreground">
          {user.role === 'business-owner' ? 'Business' : 'Customer'}
        </span>
        <span className="text-sm font-medium">
          {user.full_name || user.email}
        </span>
      </div>
      
      <Button
        variant="outline"
        size="sm"
        onClick={handleLogout}
        className="text-red-600 hover:text-red-700 hover:bg-red-50"
      >
        Logout
      </Button>
    </nav>
  )
}