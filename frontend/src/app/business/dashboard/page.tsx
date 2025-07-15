'use client'

import { useBusinessStore } from '@/stores/business.store';
import { useEffect, useState } from 'react'
import { useAuth } from '@/hooks/use-auth'
import { Button } from '@/components/ui/button'
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card'
import AuthGuard from '@/components/auth-guard'
import BusinessManage from '@/components/business-manage'
import { Store, TrendingUp, Users, Package, DollarSign, Clock, Bell, Settings, Loader2 } from 'lucide-react'
import type { Business } from '@/types/business';
import dynamic from 'next/dynamic';
import { useRouter } from 'next/navigation';
import Link from 'next/link';

const MenuList = dynamic(() => import('@/components/menu-list'), { ssr: false });

export default function BusinessDashboard() {
  const { user, logout } = useAuth()
  const [isManageModalOpen, setIsManageModalOpen] = useState(false)
  const [business, setBusiness] = useState<Business | null>(null);
  const [isLoading, setIsLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const getBusiness = useBusinessStore((state) => state.getBusiness);
  const router = useRouter();

  useEffect(() => {
    setIsLoading(true);
    setError(null);
    getBusiness()
      .then(setBusiness)
      .catch((err) => setError('Failed to load business info.'))
      .finally(() => setIsLoading(false));
  }, [getBusiness]);

  const handleLogout = async () => {
    await logout()
  }

  const handleManageRestaurant = () => {
    setIsManageModalOpen(false); // Close menu modal if open
    setIsManageModalOpen(true);
  };

  const handleCloseManageModal = () => {
    setIsManageModalOpen(false)
  }

  const handleManageMenu = () => {
    setIsManageModalOpen(false); // Close business modal if open
    // Navigate to the menu management page
    if (business?.id) {
      router.push('/business/menu');
    }
  };

  return (
    <AuthGuard requireAuth={true} allowedRoles={['business-owner']}>
      <div className="min-h-screen bg-background">
        {/* Navigation Bar */}
        <nav className="bg-white border-b">
          <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 flex items-center h-12">
            <Link href="/business/dashboard" className="text-sm font-medium text-primary mr-6">Dashboard</Link>
            <Link href="/business/menu" className="text-sm font-medium text-muted-foreground hover:text-primary">Menu</Link>
            <span className="ml-auto text-xs text-muted-foreground">/ Dashboard</span>
          </div>
        </nav>
        {/* Main Content */}
        <main className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
          {isLoading ? (
            <div className="flex flex-col items-center justify-center py-16">
              <Loader2 className="h-10 w-10 animate-spin text-emerald-600 mb-4" />
              <span className="text-muted-foreground">Loading business info...</span>
            </div>
          ) : error ? (
            <div className="flex flex-col items-center justify-center py-16">
              <span className="text-destructive font-semibold mb-2">{error}</span>
              <Button variant="outline" onClick={() => window.location.reload()}>Retry</Button>
            </div>
          ) : (
            <>
              {/* Stats Overview */}
              <div className="grid grid-cols-1 md:grid-cols-4 gap-6 mb-8">
                <Card>
                  <CardContent className="p-6">
                    <div className="flex items-center justify-between">
                      <div>
                        <p className="text-sm font-medium text-muted-foreground">Total Revenue</p>
                        <p className="text-2xl font-bold">--</p>
                        <p className="text-sm text-green-600">&nbsp;</p>
                      </div>
                      <DollarSign className="h-8 w-8 text-green-600" />
                    </div>
                  </CardContent>
                </Card>
                
                <Card>
                  <CardContent className="p-6">
                    <div className="flex items-center justify-between">
                      <div>
                        <p className="text-sm font-medium text-muted-foreground">Orders Today</p>
                        <p className="text-2xl font-bold">--</p>
                        <p className="text-sm text-blue-600">&nbsp;</p>
                      </div>
                      <Package className="h-8 w-8 text-blue-600" />
                    </div>
                  </CardContent>
                </Card>
                
                <Card>
                  <CardContent className="p-6">
                    <div className="flex items-center justify-between">
                      <div>
                        <p className="text-sm font-medium text-muted-foreground">Total Customers</p>
                        <p className="text-2xl font-bold">--</p>
                        <p className="text-sm text-purple-600">&nbsp;</p>
                      </div>
                      <Users className="h-8 w-8 text-purple-600" />
                    </div>
                  </CardContent>
                </Card>
                
                <Card>
                  <CardContent className="p-6">
                    <div className="flex items-center justify-between">
                      <div>
                        <p className="text-sm font-medium text-muted-foreground">Avg Order Value</p>
                        <p className="text-2xl font-bold">--</p>
                        <p className="text-sm text-orange-600">&nbsp;</p>
                      </div>
                      <TrendingUp className="h-8 w-8 text-orange-600" />
                    </div>
                  </CardContent>
                </Card>
              </div>

              {/* Quick Actions */}
              <div className="grid grid-cols-1 md:grid-cols-4 gap-4 mb-8">
                <Card className="hover:shadow-md transition-shadow cursor-pointer" onClick={handleManageMenu}>
                  <CardContent className="p-6 text-center">
                    <Store className="h-8 w-8 text-primary mx-auto mb-2" />
                    <h3 className="font-semibold">Manage Menu</h3>
                    <p className="text-sm text-muted-foreground">Update dishes & prices</p>
                  </CardContent>
                </Card>
                
                <Card className="hover:shadow-md transition-shadow cursor-pointer">
                  <CardContent className="p-6 text-center">
                    <Package className="h-8 w-8 text-primary mx-auto mb-2" />
                    <h3 className="font-semibold">View Orders</h3>
                    <p className="text-sm text-muted-foreground">Manage incoming orders</p>
                  </CardContent>
                </Card>
                
                <Card className="hover:shadow-md transition-shadow cursor-pointer">
                  <CardContent className="p-6 text-center">
                    <TrendingUp className="h-8 w-8 text-primary mx-auto mb-2" />
                    <h3 className="font-semibold">Analytics</h3>
                    <p className="text-sm text-muted-foreground">View reports & insights</p>
                  </CardContent>
                </Card>
                
                <Card className="hover:shadow-md transition-shadow cursor-pointer">
                  <CardContent className="p-6 text-center">
                    <Settings className="h-8 w-8 text-primary mx-auto mb-2" />
                    <h3 className="font-semibold">Settings</h3>
                    <p className="text-sm text-muted-foreground">Restaurant settings</p>
                  </CardContent>
                </Card>
              </div>

              <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
                {/* Recent Orders */}
                <Card className="lg:col-span-2">
                  <CardHeader>
                    <CardTitle>Recent Orders</CardTitle>
                    <CardDescription>Latest customer orders</CardDescription>
                  </CardHeader>
                  <CardContent>
                    <div className="space-y-4">
                      {/* No test orders, leave empty or add dynamic rendering here */}
                    </div>
                    
                    <Button variant="outline" className="w-full mt-4">
                      View All Orders
                    </Button>
                  </CardContent>
                </Card>

                {/* Business Info & Quick Stats */}
                <div className="space-y-6">
                  <Card>
                    <CardHeader>
                      <CardTitle>Restaurant Status</CardTitle>
                      <CardDescription>Current operating status</CardDescription>
                    </CardHeader>
                    <CardContent>
                      <div className="space-y-4">
                        <div className="flex items-center justify-between">
                          <span className="text-sm font-medium">Status</span>
                          <span className="inline-flex items-center px-2.5 py-0.5 rounded-full text-xs font-medium bg-green-100 text-green-800">
                            Open
                          </span>
                        </div>
                        <div className="flex items-center justify-between">
                          <span className="text-sm font-medium">Orders Queue</span>
                          <span className="text-sm text-muted-foreground">3 pending</span>
                        </div>
                        <div className="flex items-center justify-between">
                          <span className="text-sm font-medium">Avg Prep Time</span>
                          <span className="text-sm text-muted-foreground">15 min</span>
                        </div>
                        {/* Removed Manage Restaurant button */}
                      </div>
                    </CardContent>
                  </Card>

                  <Card>
                    <CardHeader>
                      <CardTitle>Business Profile</CardTitle>
                      <CardDescription>Account information</CardDescription>
                    </CardHeader>
                    <CardContent>
                      <div className="space-y-3">
                        <div>
                          <p className="text-sm font-medium">Business Email</p>
                          <p className="text-sm text-muted-foreground">{user?.email}</p>
                        </div>
                        <div>
                          <p className="text-sm font-medium">Owner Name</p>
                          <p className="text-sm text-muted-foreground">{user?.full_name || 'Not set'}</p>
                        </div>
                        <div>
                          <p className="text-sm font-medium">Account Type</p>
                          <p className="text-sm text-muted-foreground capitalize">{user?.role}</p>
                        </div>
                      </div>
                      <Button variant="outline" className="w-full mt-4" onClick={handleManageRestaurant}>
                        Edit Profile
                      </Button>
                    </CardContent>
                  </Card>
                </div>
              </div>

              {/* BusinessManage Modal */}
              <BusinessManage 
                isOpen={isManageModalOpen} 
                onClose={handleCloseManageModal} 
                business={business}
              />
            </>
          )}
        </main>
      </div>
    </AuthGuard>
  )
}