'use client'

import { useState, useEffect } from 'react'
import { useParams, useRouter } from 'next/navigation'
import { useAuth } from '@/hooks/use-auth'
import { Button } from '@/components/ui/button'
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card'
import { Input } from '@/components/ui/input'
import { Badge } from '@/components/ui/badge'
import { Textarea } from '@/components/ui/textarea'
import { Separator } from '@/components/ui/separator'
import AuthGuard from '@/components/auth-guard'
import { businessService } from '@/services/business'
import { menuItemsService } from '@/services/menu-items'
import { ordersService } from '@/services/orders'
import { Business } from '@/types/business'
import { MenuItem } from '@/types/menu-items.types'
import { OrderCreate } from '@/types/orders'
import { 
  ArrowLeft, 
  ShoppingCart, 
  Plus, 
  Minus, 
  MapPin, 
  Clock, 
  Phone,
  Trash2,
  CheckCircle
} from 'lucide-react'
import Link from 'next/link'
import { toast } from 'sonner'

interface CartItem {
  menuItem: MenuItem
  quantity: number
  specialInstructions?: string
}

export default function BusinessMenuPage() {
  const params = useParams()
  const router = useRouter()
  const { user } = useAuth()
  const businessId = params.businessId as string
  
  const [business, setBusiness] = useState<Business | null>(null)
  const [menuItems, setMenuItems] = useState<MenuItem[]>([])
  const [loading, setLoading] = useState(true)
  const [cart, setCart] = useState<CartItem[]>([])
  const [specialInstructions, setSpecialInstructions] = useState('')
  const [isPlacingOrder, setIsPlacingOrder] = useState(false)

  useEffect(() => {
    loadBusinessAndMenu()
  }, [businessId])

  const loadBusinessAndMenu = async () => {
    try {
      setLoading(true)
      
      // Load business details
      const businessData = await businessService.getBusinessById(businessId)
      setBusiness(businessData)
      
      // Load menu items
      const menuResponse = await menuItemsService.getMenuItemsByBusiness(
        '', // token will be handled by the service
        businessId,
        { available_only: true }
      )
      setMenuItems(menuResponse.items)
    } catch (error) {
      console.error('Error loading business and menu:', error)
      toast.error('Failed to load restaurant information')
    } finally {
      setLoading(false)
    }
  }

  const addToCart = (menuItem: MenuItem) => {
    setCart(prevCart => {
      const existingItem = prevCart.find(item => item.menuItem.id === menuItem.id)
      
      if (existingItem) {
        return prevCart.map(item =>
          item.menuItem.id === menuItem.id
            ? { ...item, quantity: item.quantity + 1 }
            : item
        )
      } else {
        return [...prevCart, { menuItem, quantity: 1 }]
      }
    })
    toast.success(`${menuItem.name} added to cart`)
  }

  const removeFromCart = (menuItemId: string) => {
    setCart(prevCart => prevCart.filter(item => item.menuItem.id !== menuItemId))
    toast.success('Item removed from cart')
  }

  const updateQuantity = (menuItemId: string, newQuantity: number) => {
    if (newQuantity <= 0) {
      removeFromCart(menuItemId)
      return
    }
    
    setCart(prevCart =>
      prevCart.map(item =>
        item.menuItem.id === menuItemId
          ? { ...item, quantity: newQuantity }
          : item
      )
    )
  }

  const getCartTotal = () => {
    return cart.reduce((total, item) => total + (item.menuItem.price * item.quantity), 0)
  }

  const placeOrder = async () => {
    if (cart.length === 0) {
      toast.error('Your cart is empty')
      return
    }

    try {
      setIsPlacingOrder(true)
      
      const orderData: OrderCreate = {
        business_id: businessId,
        total_amount: getCartTotal(),
        special_instructions: specialInstructions || undefined,
        items: cart.map(item => ({
          menu_item_id: item.menuItem.id,
          quantity: item.quantity,
          special_instructions: item.specialInstructions
        }))
      }

      const order = await ordersService.createOrder(orderData)
      
      // Clear cart
      setCart([])
      setSpecialInstructions('')
      
      toast.success('Order placed successfully!')
      
      // Redirect to order tracking
      router.push(`/customer/orders/track/${order.id}`)
    } catch (error) {
      console.error('Error placing order:', error)
      toast.error('Failed to place order. Please try again.')
    } finally {
      setIsPlacingOrder(false)
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

  if (!business) {
    return (
      <AuthGuard requireAuth={true} allowedRoles={['customer']}>
        <div className="min-h-screen bg-background">
          <div className="text-center py-12">
            <h2 className="text-xl font-semibold mb-2">Restaurant not found</h2>
            <p className="text-muted-foreground mb-4">The restaurant you're looking for doesn't exist.</p>
            <Link href="/customer/orders">
              <Button>Back to Restaurants</Button>
            </Link>
          </div>
        </div>
      </AuthGuard>
    )
  }

  return (
    <AuthGuard requireAuth={true} allowedRoles={['customer']}>
      <div className="min-h-screen bg-background">
        {/* Header */}
        <header className="bg-white shadow-sm border-b sticky top-0 z-10">
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
                  <h1 className="text-xl font-semibold">{business.name}</h1>
                  <p className="text-sm text-muted-foreground">{business.cuisine_type}</p>
                </div>
              </div>
              <div className="flex items-center space-x-4">
                <Badge variant="outline" className="flex items-center gap-1">
                  <ShoppingCart className="h-3 w-3" />
                  {cart.length} items
                </Badge>
                <span className="text-sm text-muted-foreground">Welcome, {user?.full_name || user?.email}</span>
              </div>
            </div>
          </div>
        </header>

        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
          <div className="grid grid-cols-1 lg:grid-cols-3 gap-8">
            {/* Menu Section */}
            <div className="lg:col-span-2">
              {/* Restaurant Info */}
              <Card className="mb-6">
                <CardContent className="p-6">
                  <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
                    <div className="flex items-center gap-2">
                      <MapPin className="h-4 w-4 text-muted-foreground" />
                      <span className="text-sm">{business.address}, {business.city}, {business.state}</span>
                    </div>
                    <div className="flex items-center gap-2">
                      <Clock className="h-4 w-4 text-muted-foreground" />
                      <span className="text-sm">{business.open_time} - {business.close_time}</span>
                    </div>
                    <div className="flex items-center gap-2">
                      <Phone className="h-4 w-4 text-muted-foreground" />
                      <span className="text-sm">{business.phone}</span>
                    </div>
                  </div>
                </CardContent>
              </Card>

              {/* Menu Items */}
              <div className="space-y-4">
                <h2 className="text-2xl font-semibold">Menu</h2>
                {menuItems.length === 0 ? (
                  <Card>
                    <CardContent className="p-6 text-center">
                      <p className="text-muted-foreground">No menu items available at the moment.</p>
                    </CardContent>
                  </Card>
                ) : (
                  <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                    {menuItems.map((item) => (
                      <Card key={item.id} className="hover:shadow-md transition-shadow">
                        <CardContent className="p-4">
                          <div className="flex justify-between items-start mb-3">
                            <div className="flex-1">
                              <h3 className="font-semibold">{item.name}</h3>
                              {item.description && (
                                <p className="text-sm text-muted-foreground mt-1">{item.description}</p>
                              )}
                            </div>
                            <div className="text-right">
                              <p className="font-semibold">${item.price.toFixed(2)}</p>
                              {!item.available && (
                                <Badge variant="secondary" className="text-xs">Unavailable</Badge>
                              )}
                            </div>
                          </div>
                          
                          {item.available && (
                            <Button
                              onClick={() => addToCart(item)}
                              size="sm"
                              className="w-full"
                            >
                              <Plus className="h-4 w-4 mr-2" />
                              Add to Cart
                            </Button>
                          )}
                        </CardContent>
                      </Card>
                    ))}
                  </div>
                )}
              </div>
            </div>

            {/* Cart Section */}
            <div className="lg:col-span-1">
              <Card className="sticky top-24">
                <CardHeader>
                  <CardTitle className="flex items-center gap-2">
                    <ShoppingCart className="h-5 w-5" />
                    Your Order
                  </CardTitle>
                  <CardDescription>
                    {cart.length} items in cart
                  </CardDescription>
                </CardHeader>
                <CardContent className="space-y-4">
                  {cart.length === 0 ? (
                    <p className="text-center text-muted-foreground py-8">
                      Your cart is empty
                    </p>
                  ) : (
                    <>
                      {/* Cart Items */}
                      <div className="space-y-3 max-h-64 overflow-y-auto">
                        {cart.map((item) => (
                          <div key={item.menuItem.id} className="flex items-center justify-between p-3 border rounded-lg">
                            <div className="flex-1">
                              <h4 className="font-medium text-sm">{item.menuItem.name}</h4>
                              <p className="text-xs text-muted-foreground">
                                ${item.menuItem.price.toFixed(2)} × {item.quantity}
                              </p>
                            </div>
                            <div className="flex items-center gap-2">
                              <Button
                                variant="outline"
                                size="sm"
                                onClick={() => updateQuantity(item.menuItem.id, item.quantity - 1)}
                              >
                                <Minus className="h-3 w-3" />
                              </Button>
                              <span className="text-sm font-medium w-8 text-center">
                                {item.quantity}
                              </span>
                              <Button
                                variant="outline"
                                size="sm"
                                onClick={() => updateQuantity(item.menuItem.id, item.quantity + 1)}
                              >
                                <Plus className="h-3 w-3" />
                              </Button>
                              <Button
                                variant="ghost"
                                size="sm"
                                onClick={() => removeFromCart(item.menuItem.id)}
                                className="text-red-500 hover:text-red-700"
                              >
                                <Trash2 className="h-3 w-3" />
                              </Button>
                            </div>
                          </div>
                        ))}
                      </div>

                      <Separator />

                      {/* Special Instructions */}
                      <div>
                        <label className="text-sm font-medium mb-2 block">
                          Special Instructions
                        </label>
                        <Textarea
                          placeholder="Any special requests or dietary restrictions..."
                          value={specialInstructions}
                          onChange={(e) => setSpecialInstructions(e.target.value)}
                          rows={3}
                        />
                      </div>

                      {/* Total */}
                      <div className="flex justify-between items-center pt-2">
                        <span className="font-semibold">Total</span>
                        <span className="font-semibold text-lg">${getCartTotal().toFixed(2)}</span>
                      </div>

                      {/* Place Order Button */}
                      <Button
                        onClick={placeOrder}
                        disabled={isPlacingOrder || cart.length === 0}
                        className="w-full"
                        size="lg"
                      >
                        {isPlacingOrder ? (
                          <>
                            <div className="animate-spin rounded-full h-4 w-4 border-b-2 border-white mr-2"></div>
                            Placing Order...
                          </>
                        ) : (
                          <>
                            <CheckCircle className="h-4 w-4 mr-2" />
                            Place Order
                          </>
                        )}
                      </Button>
                    </>
                  )}
                </CardContent>
              </Card>
            </div>
          </div>
        </div>
      </div>
    </AuthGuard>
  )
} 