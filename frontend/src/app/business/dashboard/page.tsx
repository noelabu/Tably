'use client'

import { useBusinessStore } from '@/stores/business.store';
import { useEffect, useState } from 'react'
import { useAuth } from '@/hooks/use-auth'
import { Button } from '@/components/ui/button'
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card'
import AuthGuard from '@/components/auth-guard'
import BusinessManage from '@/components/business-manage'
import { Store, TrendingUp, Users, Package, DollarSign, Clock, Bell, Settings, Loader2, Eye, Wrench, Check } from 'lucide-react'
import type { Business } from '@/types/business';
import dynamic from 'next/dynamic';
import { useRouter } from 'next/navigation';
import Link from 'next/link';
import { useOrderStore } from '@/stores/orders';
import { Order } from '@/types/orders';
import { Table, TableBody, TableCell, TableHead, TableHeader, TableRow } from '@/components/ui/table';
import { Badge } from '@/components/ui/badge';
import { Tooltip, TooltipContent, TooltipProvider, TooltipTrigger } from '@/components/ui/tooltip';
import { Dialog, DialogContent, DialogHeader, DialogTitle, DialogDescription } from '@/components/ui/dialog';

const MenuList = dynamic(() => import('@/components/menu-list'), { ssr: false });

export default function BusinessDashboard() {
  const { user, logout } = useAuth()
  const [isManageModalOpen, setIsManageModalOpen] = useState(false)
  const [business, setBusiness] = useState<Business | null>(null);
  const [isLoading, setIsLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [orders, setOrders] = useState<Order[]>([]);
  const [ordersLoading, setOrdersLoading] = useState(false);
  const [ordersError, setOrdersError] = useState<string | null>(null);
  const [ordersPage, setOrdersPage] = useState(1);
  const [ordersPageSize] = useState(7);
  const [ordersTotal, setOrdersTotal] = useState(0);
  const [selectedOrder, setSelectedOrder] = useState<Order | null>(null);
  const [isOrderModalOpen, setIsOrderModalOpen] = useState(false);
  const [orderModalLoading, setOrderModalLoading] = useState(false);
  const getBusiness = useBusinessStore((state) => state.getBusiness);
  const orderStore = useOrderStore();
  const router = useRouter();

  useEffect(() => {
    setIsLoading(true);
    setError(null);
    getBusiness()
      .then(setBusiness)
      .catch((err) => setError('Failed to load business info.'))
      .finally(() => setIsLoading(false));
  }, [getBusiness]);

  useEffect(() => {
    if (!business || !business.id) return;
    async function fetchOrders() {
      setOrdersLoading(true);
      setOrdersError(null);
      try {
        if (!business || !business.id) {
          setOrders([]);
          setOrdersTotal(0);
          return;
        }
        const response = await orderStore.getOrdersByBusiness(business.id, ordersPage, ordersPageSize);
        if (response) {
          setOrders(response.items);
          setOrdersTotal(response.total);
        } else {
          setOrders([]);
          setOrdersTotal(0);
        }
      } catch (err) {
        setOrdersError('Failed to load recent orders.');
      } finally {
        setOrdersLoading(false);
      }
    }
    fetchOrders();
  }, [business, ordersPage, ordersPageSize]);

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

  const handleViewOrders = () => {
    router.push('/business/orders');
  };

  // Handler for updating order status from modal
  const handleUpdateOrderStatus = async (status: 'preparing' | 'completed') => {
    if (!selectedOrder) return;
    setOrderModalLoading(true);
    try {
      const updated = await orderStore.updateOrder(selectedOrder.id, { status });
      if (updated) {
        setSelectedOrder(updated);
        setIsOrderModalOpen(false);
        // Refresh orders
        if (business?.id) {
          setOrdersLoading(true);
          const response = await orderStore.getOrdersByBusiness(business.id, ordersPage, ordersPageSize);
          setOrders(response?.items || []);
          setOrdersTotal(response?.total || 0);
          setOrdersLoading(false);
        }
      }
    } finally {
      setOrderModalLoading(false);
    }
  };

  return (
    <AuthGuard requireAuth={true} allowedRoles={['business-owner']}>
      <div className="min-h-screen bg-background">
        {/* Navigation Bar */}
        <nav className="bg-white border-b">
          <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 flex items-center h-12">
            <Link href="/business/dashboard" className="text-sm font-medium text-primary mr-6">Dashboard</Link>
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
                
                <Card className="hover:shadow-md transition-shadow cursor-pointer" onClick={handleViewOrders}>
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
                    {ordersLoading ? (
                      <div>Loading...</div>
                    ) : ordersError ? (
                      <div className="text-destructive text-sm">{ordersError}</div>
                    ) : orders.length === 0 ? (
                      <div className="text-muted-foreground text-sm">No orders found.</div>
                    ) : (
                      <Table>
                        <TableHeader>
                          <TableRow>
                            <TableHead>Order ID</TableHead>
                            <TableHead>Status</TableHead>
                            <TableHead>Total</TableHead>
                            <TableHead>Created</TableHead>
                            <TableHead>Actions</TableHead>
                          </TableRow>
                        </TableHeader>
                        <TableBody>
                          {orders.map((order) => (
                            <TableRow key={order.id}>
                              <TableCell>{order.id}</TableCell>
                              <TableCell>
                                <Badge
                                  className={
                                    order.status === 'preparing'
                                      ? 'bg-amber-100 text-amber-700 border-amber-200'
                                      : order.status === 'completed'
                                      ? 'bg-green-100 text-green-700 border-green-200'
                                      : ''
                                  }
                                >
                                  {order.status.charAt(0).toUpperCase() + order.status.slice(1)}
                                </Badge>
                              </TableCell>
                              <TableCell>${Number(order.total_amount).toFixed(2)}</TableCell>
                              <TableCell>{new Date(order.created_at).toLocaleString()}</TableCell>
                              <TableCell className="space-x-2">
                                <TooltipProvider>
                                  <Tooltip>
                                    <TooltipTrigger asChild>
                                      <Button size="icon" variant="outline" className="border-gray-300" onClick={async () => {
                                        setOrderModalLoading(true);
                                        setIsOrderModalOpen(true);
                                        try {
                                          const details = await orderStore.getOrder(order.id);
                                          if (details) setSelectedOrder(details);
                                        } finally {
                                          setOrderModalLoading(false);
                                        }
                                      }}>
                                        <Eye className="w-4 h-4" />
                                      </Button>
                                    </TooltipTrigger>
                                    <TooltipContent>View</TooltipContent>
                                  </Tooltip>
                                  {order.status !== 'completed' && (
                                    <>
                                      <Tooltip>
                                        <TooltipTrigger asChild>
                                          <Button
                                            size="icon"
                                            variant="secondary"
                                            className="bg-amber-100 text-amber-700 hover:bg-amber-200 border-amber-200"
                                            onClick={async () => {
                                              await orderStore.updateOrder(order.id, { status: 'preparing' });
                                              if (business?.id) {
                                                const response = await orderStore.getOrdersByBusiness(business.id, ordersPage, ordersPageSize);
                                                setOrders(response?.items || []);
                                                setOrdersTotal(response?.total || 0);
                                              }
                                            }}
                                          >
                                            <Wrench className="w-4 h-4" />
                                          </Button>
                                        </TooltipTrigger>
                                        <TooltipContent>Mark as Preparing</TooltipContent>
                                      </Tooltip>
                                      <Tooltip>
                                        <TooltipTrigger asChild>
                                          <Button
                                            size="icon"
                                            variant="secondary"
                                            className="bg-green-100 text-green-700 hover:bg-green-200 border-green-200"
                                            onClick={async () => {
                                              await orderStore.updateOrder(order.id, { status: 'completed' });
                                              if (business?.id) {
                                                const response = await orderStore.getOrdersByBusiness(business.id, ordersPage, ordersPageSize);
                                                setOrders(response?.items || []);
                                                setOrdersTotal(response?.total || 0);
                                              }
                                            }}
                                          >
                                            <Check className="w-4 h-4" />
                                          </Button>
                                        </TooltipTrigger>
                                        <TooltipContent>Mark as Complete</TooltipContent>
                                      </Tooltip>
                                    </>
                                  )}
                                </TooltipProvider>
                              </TableCell>
                            </TableRow>
                          ))}
                        </TableBody>
                      </Table>
                    )}
                    {/* Pagination controls */}
                    <div className="flex justify-between items-center mt-4">
                      <Button
                        variant="outline"
                        disabled={ordersPage === 1}
                        onClick={() => setOrdersPage((p) => Math.max(1, p - 1))}
                      >
                        Previous
                      </Button>
                      <span>
                        Page {ordersPage} of {Math.ceil(ordersTotal / ordersPageSize) || 1}
                      </span>
                      <Button
                        variant="outline"
                        disabled={ordersPage * ordersPageSize >= ordersTotal}
                        onClick={() => setOrdersPage((p) => p + 1)}
                      >
                        Next
                      </Button>
                    </div>
                    <Button variant="outline" className="w-full mt-4" onClick={handleViewOrders}>
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

              {/* Order Details Modal */}
              <Dialog open={isOrderModalOpen} onOpenChange={setIsOrderModalOpen}>
                <DialogContent className="w-full max-w-2xl p-0">
                  <DialogTitle asChild>
                    <div className="flex items-center gap-2 text-lg font-semibold px-6 pt-2 pb-2 border-b">
                      <Eye className="h-5 w-5" />
                      Order Details
                    </div>
                  </DialogTitle>
                  <Card className="border-none shadow-none">
                    <CardContent className="pt-2">
                      {orderModalLoading ? (
                        <div className="flex items-center justify-center py-8"><Loader2 className="h-6 w-6 animate-spin text-primary" /></div>
                      ) : selectedOrder ? (
                        <div className="space-y-6">
                          <div className="grid grid-cols-2 gap-4">
                            <div>
                              <div className="text-xs text-muted-foreground">Order ID</div>
                              <div className="font-semibold break-all">{selectedOrder.id}</div>
                            </div>
                            <div>
                              <div className="text-xs text-muted-foreground">Status</div>
                              <Badge
                                className={
                                  selectedOrder.status === 'preparing'
                                    ? 'bg-amber-100 text-amber-700 border-amber-200'
                                    : selectedOrder.status === 'completed'
                                    ? 'bg-green-100 text-green-700 border-green-200'
                                    : ''
                                }
                              >
                                {selectedOrder.status.charAt(0).toUpperCase() + selectedOrder.status.slice(1)}
                              </Badge>
                            </div>
                            <div>
                              <div className="text-xs text-muted-foreground">Total</div>
                              <div className="font-semibold">${Number(selectedOrder.total_amount).toFixed(2)}</div>
                            </div>
                            <div>
                              <div className="text-xs text-muted-foreground">Created</div>
                              <div>{new Date(selectedOrder.created_at).toLocaleString()}</div>
                            </div>
                          </div>
                          {/* Menu Items Section */}
                          <div>
                            <div className="font-semibold mb-2">Menu Items</div>
                            {selectedOrder.order_items && selectedOrder.order_items.length > 0 ? (
                              <div className="rounded-md border bg-card">
                                <Table>
                                  <TableHeader>
                                    <TableRow>
                                      <TableHead>Item Name</TableHead>
                                      <TableHead>Quantity</TableHead>
                                      <TableHead>Price at Order</TableHead>
                                    </TableRow>
                                  </TableHeader>
                                  <TableBody>
                                    {selectedOrder.order_items.map(item => (
                                      <TableRow key={item.id}>
                                        <TableCell>{item.name}</TableCell>
                                        <TableCell>{item.quantity}</TableCell>
                                        <TableCell>${Number(item.price_at_order).toFixed(2)}</TableCell>
                                      </TableRow>
                                    ))}
                                  </TableBody>
                                </Table>
                              </div>
                            ) : (
                              <div className="text-muted-foreground text-sm">No order items found for this order.</div>
                            )}
                          </div>
                          {/* Action Buttons */}
                          {selectedOrder.status !== 'completed' && (
                            <div className="flex gap-2 pt-2">
                              <Button
                                variant="outline"
                                className="text-yellow-600 border-yellow-600 hover:bg-yellow-50"
                                disabled={orderModalLoading}
                                onClick={() => handleUpdateOrderStatus('preparing')}
                              >
                                {orderModalLoading ? 'Updating...' : 'Mark as Preparing'}
                              </Button>
                              <Button
                                variant="default"
                                className="bg-green-600 hover:bg-green-700"
                                disabled={orderModalLoading}
                                onClick={() => handleUpdateOrderStatus('completed')}
                              >
                                {orderModalLoading ? 'Updating...' : 'Mark as Complete'}
                              </Button>
                            </div>
                          )}
                        </div>
                      ) : (
                        <div>No order selected.</div>
                      )}
                    </CardContent>
                  </Card>
                </DialogContent>
              </Dialog>
            </>
          )}
        </main>
      </div>
    </AuthGuard>
  )
}