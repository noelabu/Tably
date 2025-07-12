'use client'

import { useAuth } from '@/hooks/use-auth'
import { Button } from '@/components/ui/button'
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card'
import AuthGuard from '@/components/auth-guard'
import { ShoppingCart, MapPin, Clock, Star, Receipt } from 'lucide-react'

export default function CustomerDashboard() {
  const { user, logout } = useAuth()

  const handleLogout = async () => {
    await logout()
  }

  return (
    <AuthGuard requireAuth={true} allowedRoles={['customer']}>
      <div className="min-h-screen bg-background">
        {/* Header */}
        <header className="bg-white shadow-sm border-b">
          <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
            <div className="flex justify-between items-center h-16">
              <div className="flex items-center">
                <h1 className="text-2xl font-bold text-primary">Tably</h1>
                <span className="ml-2 text-sm text-muted-foreground">Customer</span>
              </div>
              <div className="flex items-center space-x-4">
                <span className="text-sm text-muted-foreground">Welcome, {user?.full_name || user?.email}</span>
                <Button variant="outline" onClick={handleLogout}>
                  Logout
                </Button>
              </div>
            </div>
          </div>
        </header>

        {/* Main Content */}
        <main className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
          {/* Quick Actions */}
          <div className="grid grid-cols-1 md:grid-cols-4 gap-4 mb-8">
            <Card className="hover:shadow-md transition-shadow cursor-pointer">
              <CardContent className="p-6 text-center">
                <ShoppingCart className="h-8 w-8 text-primary mx-auto mb-2" />
                <h3 className="font-semibold">Order Food</h3>
                <p className="text-sm text-muted-foreground">Browse restaurants</p>
              </CardContent>
            </Card>
            
            <Card className="hover:shadow-md transition-shadow cursor-pointer">
              <CardContent className="p-6 text-center">
                <Clock className="h-8 w-8 text-primary mx-auto mb-2" />
                <h3 className="font-semibold">Track Orders</h3>
                <p className="text-sm text-muted-foreground">Live order tracking</p>
              </CardContent>
            </Card>
            
            <Card className="hover:shadow-md transition-shadow cursor-pointer">
              <CardContent className="p-6 text-center">
                <Receipt className="h-8 w-8 text-primary mx-auto mb-2" />
                <h3 className="font-semibold">Order History</h3>
                <p className="text-sm text-muted-foreground">View past orders</p>
              </CardContent>
            </Card>
            
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
                <div className="space-y-4">
                  <div className="flex items-center justify-between p-4 border rounded-lg">
                    <div className="flex items-center space-x-4">
                      <div className="w-12 h-12 bg-orange-100 rounded-lg flex items-center justify-center">
                        <ShoppingCart className="h-6 w-6 text-orange-600" />
                      </div>
                      <div>
                        <h4 className="font-medium">Pizza Palace</h4>
                        <p className="text-sm text-muted-foreground">Delivered • 2 hours ago</p>
                      </div>
                    </div>
                    <div className="text-right">
                      <p className="font-medium">$24.99</p>
                      <p className="text-sm text-muted-foreground">Order #1234</p>
                    </div>
                  </div>
                  
                  <div className="flex items-center justify-between p-4 border rounded-lg">
                    <div className="flex items-center space-x-4">
                      <div className="w-12 h-12 bg-green-100 rounded-lg flex items-center justify-center">
                        <ShoppingCart className="h-6 w-6 text-green-600" />
                      </div>
                      <div>
                        <h4 className="font-medium">Burger Barn</h4>
                        <p className="text-sm text-muted-foreground">Delivered • Yesterday</p>
                      </div>
                    </div>
                    <div className="text-right">
                      <p className="font-medium">$18.50</p>
                      <p className="text-sm text-muted-foreground">Order #1233</p>
                    </div>
                  </div>
                </div>
                
                <Button variant="outline" className="w-full mt-4">
                  View All Orders
                </Button>
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
                  <div className="space-y-3">
                    <div className="flex items-center justify-between">
                      <div className="flex items-center space-x-3">
                        <Star className="h-4 w-4 text-yellow-500" />
                        <span className="text-sm">Pizza Palace</span>
                      </div>
                      <Button size="sm" variant="ghost">Order</Button>
                    </div>
                    <div className="flex items-center justify-between">
                      <div className="flex items-center space-x-3">
                        <Star className="h-4 w-4 text-yellow-500" />
                        <span className="text-sm">Burger Barn</span>
                      </div>
                      <Button size="sm" variant="ghost">Order</Button>
                    </div>
                    <div className="flex items-center justify-between">
                      <div className="flex items-center space-x-3">
                        <Star className="h-4 w-4 text-yellow-500" />
                        <span className="text-sm">Taco Town</span>
                      </div>
                      <Button size="sm" variant="ghost">Order</Button>
                    </div>
                  </div>
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