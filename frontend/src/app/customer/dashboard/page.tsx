'use client'

import { useAuth } from '@/hooks/use-auth'
import { Button } from '@/components/ui/button'
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card'
import AuthGuard from '@/components/auth-guard'
import { ShoppingCart, MapPin, Clock, Star, Receipt } from 'lucide-react'
import Link from 'next/link'
import { useEffect, useState } from 'react';
import { Order } from '@/types/orders';
import { useOrderStore } from '@/stores/orders';

export default function CustomerDashboard() {
  const { user, logout } = useAuth()

  const handleLogout = async () => {
    await logout()
  }

  const [orders, setOrders] = useState<Order[]>([]);
  const [loadingOrders, setLoadingOrders] = useState(false);
  const [ordersError, setOrdersError] = useState<string | null>(null);
  const { getCustomerOrders, isLoading } = useOrderStore();

  useEffect(() => {
    async function fetchOrders() {
      setLoadingOrders(true);
      setOrdersError(null);
      try {
        const response = await getCustomerOrders(1, 5);
        setOrders(response?.items || []);
      } catch (err) {
        setOrdersError('Failed to load recent orders.');
      } finally {
        setLoadingOrders(false);
      }
    }
    fetchOrders();
  }, []);

  return (
    <AuthGuard requireAuth={true} allowedRoles={['customer']}>
      <div className="min-h-screen bg-background">
        {/* Navigation Bar */}
        <nav className="bg-white border-b">
          <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 flex items-center h-12">
            <Link href="/customer/dashboard" className="text-sm font-medium text-primary mr-6">Dashboard</Link>
            <Link href="/customer/orders" className="text-sm font-medium text-muted-foreground hover:text-primary">Orders</Link>
            <span className="ml-auto text-xs text-muted-foreground">/ Dashboard</span>
          </div>
        </nav>
        <main className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
          {/* Quick Actions */}
          <div className="grid grid-cols-1 md:grid-cols-4 gap-4 mb-8">
            <Link href="/customer/orders">
              <Card className="hover:shadow-md transition-shadow cursor-pointer">
                <CardContent className="p-6 text-center">
                  <ShoppingCart className="h-8 w-8 text-primary mx-auto mb-2" />
                  <h3 className="font-semibold">Order Food</h3>
                  <p className="text-sm text-muted-foreground">Browse restaurants</p>
                </CardContent>
              </Card>
            </Link>
            
            <Card className="hover:shadow-md transition-shadow cursor-pointer">
              <CardContent className="p-6 text-center">
                <Clock className="h-8 w-8 text-primary mx-auto mb-2" />
                <h3 className="font-semibold">Track Orders</h3>
                <p className="text-sm text-muted-foreground">Live order tracking</p>
              </CardContent>
            </Card>
            
            <Link href="/customer/orders/history">
              <Card className="hover:shadow-md transition-shadow cursor-pointer">
                <CardContent className="p-6 text-center">
                  <Receipt className="h-8 w-8 text-primary mx-auto mb-2" />
                  <h3 className="font-semibold">Order History</h3>
                  <p className="text-sm text-muted-foreground">View past orders</p>
                </CardContent>
              </Card>
            </Link>
            
            <Card className="hover:shadow-md transition-shadow cursor-pointer">
              <CardContent className="p-6 text-center">
                <MapPin className="h-8 w-8 text-primary mx-auto mb-2" />
                <h3 className="font-semibold">Addresses</h3>
                <p className="text-sm text-muted-foreground">Manage delivery</p>
              </CardContent>
            </Card>
          </div>

          <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
            {/* Recent Orders */}
            <Card className="lg:col-span-2">
              <CardHeader>
                <CardTitle>Recent Orders</CardTitle>
                <CardDescription>Your latest food orders</CardDescription>
              </CardHeader>
              <CardContent>
                {loadingOrders ? (
                  <div>Loading...</div>
                ) : ordersError ? (
                  <div className="text-destructive text-sm">{ordersError}</div>
                ) : orders.length === 0 ? (
                  <div className="text-muted-foreground text-sm">No recent orders found.</div>
                ) : (
                  <div className="space-y-4">
                    {orders.map((order) => (
                      <div key={order.id} className="flex items-center justify-between p-4 border rounded-lg">
                        <div className="flex items-center space-x-4">
                          <div className="w-12 h-12 bg-orange-100 rounded-lg flex items-center justify-center">
                            <ShoppingCart className="h-6 w-6 text-orange-600" />
                          </div>
                          <div>
                            <h4 className="font-medium">{order.business?.name || 'Restaurant'}</h4>
                            <p className="text-sm text-muted-foreground">{order.status.charAt(0).toUpperCase() + order.status.slice(1)} • {new Date(order.created_at).toLocaleString()}</p>
                          </div>
                        </div>
                        <div className="text-right">
                          <p className="font-medium">${Number(order.total_amount).toFixed(2)}</p>
                          <p className="text-sm text-muted-foreground">Order #{order.id.slice(-4)}</p>
                        </div>
                      </div>
                    ))}
                  </div>
                )}
                <Link href="/customer/orders/history" className="w-full">
                  <Button variant="outline" className="w-full mt-4">
                    View All Orders
                  </Button>
                </Link>
              </CardContent>
            </Card>

            {/* Favorites & Profile */}
            <div className="space-y-6">
              <Card>
                <CardHeader>
                  <CardTitle>Favorite Restaurants</CardTitle>
                  <CardDescription>Your go-to places</CardDescription>
                </CardHeader>
                <CardContent>
                  {/* TODO: Replace with dynamic favorite restaurants when API is available */}
                  <div className="text-muted-foreground text-sm">No favorite restaurants to display.</div>
                </CardContent>
              </Card>

              <Card>
                <CardHeader>
                  <CardTitle>Profile</CardTitle>
                  <CardDescription>Account information</CardDescription>
                </CardHeader>
                <CardContent>
                  <div className="space-y-3">
                    <div>
                      <p className="text-sm font-medium">Email</p>
                      <p className="text-sm text-muted-foreground">{user?.email}</p>
                    </div>
                    <div>
                      <p className="text-sm font-medium">Name</p>
                      <p className="text-sm text-muted-foreground">{user?.full_name || 'Not set'}</p>
                    </div>
                    <div>
                      <p className="text-sm font-medium">Role</p>
                      <p className="text-sm text-muted-foreground capitalize">{user?.role}</p>
                    </div>
                  </div>
                  <Button variant="outline" className="w-full mt-4">
                    Edit Profile
                  </Button>
                </CardContent>
              </Card>
            </div>
          </div>
        </main>
      </div>
    </AuthGuard>
  )
}