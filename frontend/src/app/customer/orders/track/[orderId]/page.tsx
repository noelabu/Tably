'use client'

import { useState, useEffect } from 'react'
import { useParams, useRouter } from 'next/navigation'
import { useAuth } from '@/hooks/use-auth'
import { Button } from '@/components/ui/button'
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card'
import { Badge } from '@/components/ui/badge'
import { Separator } from '@/components/ui/separator'
import AuthGuard from '@/components/auth-guard'
import { ordersService } from '@/services/orders'
import { Order } from '@/types/orders'
import { 
  ArrowLeft, 
  Clock, 
  CheckCircle, 
  ChefHat, 
  Package, 
  Truck,
  MapPin,
  Phone,
  Receipt
} from 'lucide-react'
import Link from 'next/link'

const statusSteps = [
  { key: 'pending', label: 'Order Placed', icon: Clock, color: 'text-blue-600' },
  { key: 'confirmed', label: 'Order Confirmed', icon: CheckCircle, color: 'text-green-600' },
  { key: 'preparing', label: 'Preparing', icon: ChefHat, color: 'text-orange-600' },
  { key: 'ready', label: 'Ready for Pickup', icon: Package, color: 'text-purple-600' },
  { key: 'completed', label: 'Completed', icon: CheckCircle, color: 'text-green-600' }
]

export default function OrderTrackingPage() {
  const params = useParams()
  const router = useRouter()
  const { user } = useAuth()
  const orderId = params.orderId as string
  
  const [order, setOrder] = useState<Order | null>(null)
  const [loading, setLoading] = useState(true)

  useEffect(() => {
    loadOrder()
    // Poll for updates every 30 seconds
    const interval = setInterval(loadOrder, 30000)
    return () => clearInterval(interval)
  }, [orderId])

  const loadOrder = async () => {
    try {
      setLoading(true)
      const orderData = await ordersService.getOrder(orderId)
      setOrder(orderData)
    } catch (error) {
      console.error('Error loading order:', error)
    } finally {
      setLoading(false)
    }
  }

  const getStatusStep = (status: string) => {
    return statusSteps.findIndex(step => step.key === status)
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

  if (loading) {
    return (
      <AuthGuard requireAuth={true} allowedRoles={['customer']}>
        <div className="min-h-screen bg-background">
          <div className="flex justify-center items-center py-12">
            <div className="animate-spin rounded-full h-8 w-8 border-b-2 border-primary"></div>
          </div>
        </div>
      </AuthGuard>
    )
  }

  if (!order) {
    return (
      <AuthGuard requireAuth={true} allowedRoles={['customer']}>
        <div className="min-h-screen bg-background">
          <div className="text-center py-12">
            <h2 className="text-xl font-semibold mb-2">Order not found</h2>
            <p className="text-muted-foreground mb-4">The order you're looking for doesn't exist.</p>
            <Link href="/customer/orders">
              <Button>Back to Orders</Button>
            </Link>
          </div>
        </div>
      </AuthGuard>
    )
  }

  const currentStep = getStatusStep(order.status)

  return (
    <AuthGuard requireAuth={true} allowedRoles={['customer']}>
      <div className="min-h-screen bg-background">
        {/* Header */}
        <header className="bg-white shadow-sm border-b">
          <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
            <div className="flex justify-between items-center h-16">
              <div className="flex items-center space-x-4">
                <Link href="/customer/orders">
                  <Button variant="ghost" size="sm">
                    <ArrowLeft className="h-4 w-4 mr-2" />
                    Back
                  </Button>
                </Link>
                <div>
                  <h1 className="text-xl font-semibold">Order #{order.id.slice(0, 8)}</h1>
                  <p className="text-sm text-muted-foreground">
                    {order.business?.name || 'Restaurant'}
                  </p>
                </div>
              </div>
              <div className="flex items-center space-x-4">
                <Badge className={getStatusColor(order.status)}>
                  {order.status.charAt(0).toUpperCase() + order.status.slice(1)}
                </Badge>
                <span className="text-sm text-muted-foreground">Welcome, {user?.full_name || user?.email}</span>
              </div>
            </div>
          </div>
        </header>

        <div className="max-w-4xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
          <div className="grid grid-cols-1 lg:grid-cols-3 gap-8">
            {/* Order Status */}
            <div className="lg:col-span-2">
              <Card>
                <CardHeader>
                  <CardTitle>Order Status</CardTitle>
                  <CardDescription>
                    Track your order progress
                  </CardDescription>
                </CardHeader>
                <CardContent>
                  <div className="space-y-6">
                    {/* Status Steps */}
                    <div className="relative">
                      {statusSteps.map((step, index) => {
                        const Icon = step.icon
                        const isCompleted = index <= currentStep
                        const isCurrent = index === currentStep
                        
                        return (
                          <div key={step.key} className="flex items-center mb-6">
                            <div className={`flex items-center justify-center w-10 h-10 rounded-full border-2 ${
                              isCompleted 
                                ? 'bg-primary border-primary text-white' 
                                : 'bg-gray-100 border-gray-300 text-gray-400'
                            }`}>
                              <Icon className="h-5 w-5" />
                            </div>
                            <div className="ml-4 flex-1">
                              <h3 className={`font-medium ${
                                isCompleted ? 'text-gray-900' : 'text-gray-500'
                              }`}>
                                {step.label}
                              </h3>
                              {isCurrent && (
                                <p className="text-sm text-muted-foreground mt-1">
                                  Your order is currently being processed
                                </p>
                              )}
                            </div>
                            {index < statusSteps.length - 1 && (
                              <div className={`w-0.5 h-12 ml-5 ${
                                isCompleted ? 'bg-primary' : 'bg-gray-200'
                              }`} />
                            )}
                          </div>
                        )
                      })}
                    </div>

                    {/* Order Details */}
                    <Separator />
                    <div className="space-y-4">
                      <h3 className="font-semibold">Order Details</h3>
                      <div className="grid grid-cols-2 gap-4 text-sm">
                        <div>
                          <span className="text-muted-foreground">Order ID:</span>
                          <p className="font-medium">{order.id}</p>
                        </div>
                        <div>
                          <span className="text-muted-foreground">Order Date:</span>
                          <p className="font-medium">
                            {new Date(order.created_at).toLocaleDateString()}
                          </p>
                        </div>
                        <div>
                          <span className="text-muted-foreground">Total Amount:</span>
                          <p className="font-medium">${order.total_amount.toFixed(2)}</p>
                        </div>
                        <div>
                          <span className="text-muted-foreground">Status:</span>
                          <p className="font-medium capitalize">{order.status}</p>
                        </div>
                      </div>
                    </div>
                  </div>
                </CardContent>
              </Card>
            </div>

            {/* Order Summary */}
            <div className="lg:col-span-1">
              <Card>
                <CardHeader>
                  <CardTitle className="flex items-center gap-2">
                    <Receipt className="h-5 w-5" />
                    Order Summary
                  </CardTitle>
                </CardHeader>
                <CardContent className="space-y-4">
                  {/* Restaurant Info */}
                  {order.business && (
                    <div className="space-y-3">
                      <h4 className="font-medium">Restaurant</h4>
                      <div className="space-y-2">
                        <div className="flex items-center gap-2">
                          <MapPin className="h-4 w-4 text-muted-foreground" />
                          <span className="text-sm">
                            {order.business.address}, {order.business.city}
                          </span>
                        </div>
                        <div className="flex items-center gap-2">
                          <Phone className="h-4 w-4 text-muted-foreground" />
                          <span className="text-sm">{order.business.phone}</span>
                        </div>
                      </div>
                    </div>
                  )}

                  <Separator />

                  {/* Order Items */}
                  <div className="space-y-3">
                    <h4 className="font-medium">Items</h4>
                    <div className="space-y-2">
                      {order.items.map((item) => (
                        <div key={item.id} className="flex justify-between items-center">
                          <div className="flex-1">
                            <p className="text-sm font-medium">
                              {item.menu_item?.name || `Item ${item.menu_item_id}`}
                            </p>
                            <p className="text-xs text-muted-foreground">
                              Qty: {item.quantity}
                            </p>
                          </div>
                          <p className="text-sm font-medium">
                            ${((item.menu_item?.price || 0) * item.quantity).toFixed(2)}
                          </p>
                        </div>
                      ))}
                    </div>
                  </div>

                  <Separator />

                  {/* Special Instructions */}
                  {order.special_instructions && (
                    <div className="space-y-2">
                      <h4 className="font-medium">Special Instructions</h4>
                      <p className="text-sm text-muted-foreground">
                        {order.special_instructions}
                      </p>
                    </div>
                  )}

                  {/* Total */}
                  <div className="flex justify-between items-center pt-2">
                    <span className="font-semibold">Total</span>
                    <span className="font-semibold text-lg">${order.total_amount.toFixed(2)}</span>
                  </div>

                  {/* Actions */}
                  <div className="space-y-2 pt-4">
                    <Link href="/customer/orders" className="w-full">
                      <Button variant="outline" className="w-full">
                        Order Again
                      </Button>
                    </Link>
                    <Link href="/customer/dashboard" className="w-full">
                      <Button variant="ghost" className="w-full">
                        Back to Dashboard
                      </Button>
                    </Link>
                  </div>
                </CardContent>
              </Card>
            </div>
          </div>
        </div>
      </div>
    </AuthGuard>
  )
} 