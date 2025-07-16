'use client'

import { useState, useEffect } from 'react'
import { useAuth } from '@/hooks/use-auth'
import { Button } from '@/components/ui/button'
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card'
import { Badge } from '@/components/ui/badge'
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from '@/components/ui/select'
import AuthGuard from '@/components/auth-guard'
import { ordersService } from '@/services/orders'
import { Order } from '@/types/orders'
import { 
  ArrowLeft, 
  Clock, 
  CheckCircle, 
  ChefHat, 
  Package, 
  Receipt,
  Calendar,
  DollarSign
} from 'lucide-react'
import Link from 'next/link'

export default function OrderHistoryPage() {
  const { user } = useAuth()
  const [orders, setOrders] = useState<Order[]>([])
  const [loading, setLoading] = useState(true)
  const [currentPage, setCurrentPage] = useState(1)
  const [totalPages, setTotalPages] = useState(1)
  const [statusFilter, setStatusFilter] = useState<string>('')

  useEffect(() => {
    loadOrders()
  }, [currentPage, statusFilter])

  const loadOrders = async () => {
    try {
      setLoading(true)
      const response = await ordersService.getCustomerOrders(
        currentPage,
        10,
        statusFilter || undefined
      )
      setOrders(response.items)
      setTotalPages(Math.ceil(response.total / 10))
    } catch (error) {
      console.error('Error loading orders:', error)
    } finally {
      setLoading(false)
    }
  }

  const getStatusColor = (status: string) => {
    switch (status) {
      case 'pending':
        return 'bg-blue-100 text-blue-800'
      case 'confirmed':
        return 'bg-green-100 text-green-800'
      case 'preparing':
        return 'bg-orange-100 text-orange-800'
      case 'ready':
        return 'bg-purple-100 text-purple-800'
      case 'completed':
        return 'bg-green-100 text-green-800'
      case 'cancelled':
        return 'bg-red-100 text-red-800'
      default:
        return 'bg-gray-100 text-gray-800'
    }
  }

  const getStatusIcon = (status: string) => {
    switch (status) {
      case 'pending':
        return Clock
      case 'confirmed':
        return CheckCircle
      case 'preparing':
        return ChefHat
      case 'ready':
        return Package
      case 'completed':
        return CheckCircle
      default:
        return Clock
    }
  }

  const formatDate = (dateString: string) => {
    return new Date(dateString).toLocaleDateString('en-US', {
      year: 'numeric',
      month: 'short',
      day: 'numeric',
      hour: '2-digit',
      minute: '2-digit'
    })
  }

  return (
    <AuthGuard requireAuth={true} allowedRoles={['customer']}>
      <div className="min-h-screen bg-background">
        {/* Header */}
        <header className="bg-white shadow-sm border-b">
          <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
            <div className="flex justify-between items-center h-16">
              <div className="flex items-center space-x-4">
                <Link href="/customer/dashboard">
                  <Button variant="ghost" size="sm">
                    <ArrowLeft className="h-4 w-4 mr-2" />
                    Back
                  </Button>
                </Link>
                <div>
                  <h1 className="text-xl font-semibold">Order History</h1>
                  <p className="text-sm text-muted-foreground">Your past orders</p>
                </div>
              </div>
              <div className="flex items-center space-x-4">
                <span className="text-sm text-muted-foreground">Welcome, {user?.full_name || user?.email}</span>
              </div>
            </div>
          </div>
        </header>

        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
          {/* Filters */}
          <div className="mb-6">
            <div className="flex flex-col sm:flex-row gap-4 items-center justify-between">
              <h2 className="text-lg font-semibold">Your Orders</h2>
              <div className="flex items-center space-x-4">
                <Select value={statusFilter} onValueChange={setStatusFilter}>
                  <SelectTrigger className="w-48">
                    <SelectValue placeholder="Filter by status" />
                  </SelectTrigger>
                  <SelectContent>
                    <SelectItem value="">All Orders</SelectItem>
                    <SelectItem value="pending">Pending</SelectItem>
                    <SelectItem value="confirmed">Confirmed</SelectItem>
                    <SelectItem value="preparing">Preparing</SelectItem>
                    <SelectItem value="ready">Ready</SelectItem>
                    <SelectItem value="completed">Completed</SelectItem>
                    <SelectItem value="cancelled">Cancelled</SelectItem>
                  </SelectContent>
                </Select>
              </div>
            </div>
          </div>

          {/* Loading State */}
          {loading && (
            <div className="flex justify-center items-center py-12">
              <div className="animate-spin rounded-full h-8 w-8 border-b-2 border-primary"></div>
            </div>
          )}

          {/* Orders List */}
          {!loading && (
            <>
              {orders.length === 0 ? (
                <Card>
                  <CardContent className="p-12 text-center">
                    <Receipt className="h-12 w-12 text-muted-foreground mx-auto mb-4" />
                    <h3 className="text-lg font-medium mb-2">No orders found</h3>
                    <p className="text-muted-foreground mb-4">
                      {statusFilter ? `No ${statusFilter} orders found.` : "You haven't placed any orders yet."}
                    </p>
                    <Link href="/customer/orders">
                      <Button>Browse Restaurants</Button>
                    </Link>
                  </CardContent>
                </Card>
              ) : (
                <div className="space-y-4">
                  {orders.map((order) => {
                    const StatusIcon = getStatusIcon(order.status)
                    return (
                      <Card key={order.id} className="hover:shadow-md transition-shadow">
                        <CardContent className="p-6">
                          <div className="flex items-start justify-between">
                            <div className="flex-1">
                              <div className="flex items-center space-x-3 mb-2">
                                <StatusIcon className="h-5 w-5 text-muted-foreground" />
                                <h3 className="font-semibold">
                                  {order.business?.name || 'Restaurant'}
                                </h3>
                                <Badge className={getStatusColor(order.status)}>
                                  {order.status.charAt(0).toUpperCase() + order.status.slice(1)}
                                </Badge>
                              </div>
                              
                              <div className="grid grid-cols-1 md:grid-cols-3 gap-4 text-sm text-muted-foreground mb-3">
                                <div className="flex items-center gap-2">
                                  <Calendar className="h-4 w-4" />
                                  <span>{formatDate(order.created_at)}</span>
                                </div>
                                <div className="flex items-center gap-2">
                                  <DollarSign className="h-4 w-4" />
                                  <span>${order.total_amount.toFixed(2)}</span>
                                </div>
                                <div className="flex items-center gap-2">
                                  <Receipt className="h-4 w-4" />
                                  <span>{order.items.length} items</span>
                                </div>
                              </div>

                              {/* Order Items Preview */}
                              <div className="space-y-1">
                                {order.items.slice(0, 3).map((item) => (
                                  <div key={item.id} className="flex justify-between text-sm">
                                    <span>
                                      {item.menu_item?.name || `Item ${item.menu_item_id}`} × {item.quantity}
                                    </span>
                                    <span className="text-muted-foreground">
                                      ${((item.menu_item?.price || 0) * item.quantity).toFixed(2)}
                                    </span>
                                  </div>
                                ))}
                                {order.items.length > 3 && (
                                  <p className="text-xs text-muted-foreground">
                                    +{order.items.length - 3} more items
                                  </p>
                                )}
                              </div>
                            </div>

                            <div className="flex flex-col items-end space-y-2">
                              <Link href={`/customer/orders/track/${order.id}`}>
                                <Button variant="outline" size="sm">
                                  Track Order
                                </Button>
                              </Link>
                              <Link href={`/customer/orders/${order.business_id}`}>
                                <Button variant="ghost" size="sm">
                                  Order Again
                                </Button>
                              </Link>
                            </div>
                          </div>
                        </CardContent>
                      </Card>
                    )
                  })}
                </div>
              )}

              {/* Pagination */}
              {totalPages > 1 && (
                <div className="flex justify-center items-center space-x-2 mt-8">
                  <Button
                    variant="outline"
                    size="sm"
                    onClick={() => setCurrentPage(Math.max(1, currentPage - 1))}
                    disabled={currentPage === 1}
                  >
                    Previous
                  </Button>
                  
                  <span className="text-sm text-muted-foreground">
                    Page {currentPage} of {totalPages}
                  </span>
                  
                  <Button
                    variant="outline"
                    size="sm"
                    onClick={() => setCurrentPage(Math.min(totalPages, currentPage + 1))}
                    disabled={currentPage === totalPages}
                  >
                    Next
                  </Button>
                </div>
              )}
            </>
          )}
        </div>
      </div>
    </AuthGuard>
  )
} 