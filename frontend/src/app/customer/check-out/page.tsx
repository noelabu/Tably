"use client";

import { Card, CardContent } from '@/components/ui/card';
import { Button } from '@/components/ui/button';
import Link from 'next/link';
import { useCartStore } from '@/stores/cart.store';
import { ShoppingCart, Minus, Plus, Trash2, ChevronRight } from 'lucide-react';
import { Badge } from '@/components/ui/badge';
import { useRouter } from 'next/navigation';
import { useOrderStore } from '@/stores/orders';
import { OrderCreate, OrderItemCreate } from '@/types/orders';

export default function CheckoutPage() {
  const cartItems = useCartStore((state) => state.items);
  const updateQuantity = useCartStore((state) => state.updateQuantity);
  const removeFromCart = useCartStore((state) => state.removeFromCart);
  const clearCart = useCartStore((state) => state.clearCart);
  const cartTotal = cartItems.reduce((total, item) => total + (Number(item.price) * item.quantity), 0);
  const cartItemCount = cartItems.reduce((total, item) => total + item.quantity, 0);
  const router = useRouter();
  const businessId = useCartStore((state) => state.businessId);
  const { createOrder, isLoading } = useOrderStore();

  const orderItems: OrderItemCreate[] = cartItems.map((item) => ({
    menu_item_id: item.id,
    quantity: item.quantity,
    price_at_order: Number(item.price),
  }));

  const order: OrderCreate = {
    business_id: businessId || '',
    total_amount: cartTotal,
    status: 'pending',
    order_items: orderItems,
  }

  const handleConfirmOrder = () => {
    createOrder(order);
  }

  return (
    <div className="min-h-screen bg-background">
      {/* Breadcrumbs */}
      <nav className="bg-white border-b">
        <div className="max-w-7xl mx-auto px-2 sm:px-4 lg:px-8 flex items-center h-12 space-x-2 text-sm">
          <Link href="/customer/dashboard" className="text-muted-foreground hover:text-primary">Dashboard</Link>
          <ChevronRight className="h-4 w-4 text-muted-foreground" />
          <Link href="/customer/orders" className="text-muted-foreground hover:text-primary">Orders</Link>
          <ChevronRight className="h-4 w-4 text-muted-foreground" />
          {businessId && <>
            <Link href={`/customer/order-form/${businessId}`} className="text-muted-foreground hover:text-primary">Order Form</Link>
            <ChevronRight className="h-4 w-4 text-muted-foreground" />
          </>}
          <span className="text-primary font-medium">Checkout</span>
        </div>
      </nav>
      <div className="max-w-7xl mx-auto px-2 sm:px-4 lg:px-8 py-8">
        <div className="max-w-2xl mx-auto">
          <div className="bg-card border border-border rounded-lg shadow-sm p-6">
            <h1 className="text-xl sm:text-2xl font-semibold text-foreground mb-4">Checkout</h1>
            <p className="text-muted-foreground mb-6">Review your order and confirm your purchase.</p>

            {/* Your Order summary */}
            <div className="mb-8">
              <div className="flex items-center justify-between mb-4">
                <h2 className="text-lg font-semibold text-foreground flex items-center gap-2">
                  <ShoppingCart className="w-5 h-5" />
                  Your Order
                </h2>
                <Badge variant="secondary">
                  {cartItemCount} items
                </Badge>
              </div>
              <div className="rounded-lg border bg-background mb-2">
                {cartItems.length === 0 ? (
                  <div className="text-center text-muted-foreground py-8">
                    <ShoppingCart className="w-12 h-12 mx-auto mb-4 opacity-50" />
                    <p>Your cart is empty</p>
                    <p className="text-sm">Add items to get started</p>
                  </div>
                ) : (
                  <div className="space-y-4">
                    {cartItems.map((item) => (
                      <Card key={item.id} className="bg-background">
                        <CardContent className="p-3">
                          <div className="flex items-start justify-between mb-2">
                            <div className="flex-1">
                              <h3 className="font-medium text-foreground text-sm">
                                {item.name}
                              </h3>
                              <p className="text-primary font-semibold">
                                ${Number(item.price).toFixed(2)}
                              </p>
                            </div>
                            <Button
                              variant="ghost"
                              size="sm"
                              onClick={() => removeFromCart(item.id)}
                              className="h-6 w-6 p-0 text-destructive hover:text-destructive"
                            >
                              <Trash2 className="w-3 h-3" />
                            </Button>
                          </div>
                          <div className="flex items-center justify-between">
                            <div className="flex items-center space-x-2">
                              <Button
                                variant="outline"
                                size="sm"
                                onClick={() => updateQuantity(item.id, -1)}
                                className="h-6 w-6 p-0"
                              >
                                <Minus className="w-3 h-3" />
                              </Button>
                              <span className="text-sm font-medium w-8 text-center">
                                {item.quantity}
                              </span>
                              <Button
                                variant="outline"
                                size="sm"
                                onClick={() => updateQuantity(item.id, 1)}
                                className="h-6 w-6 p-0"
                              >
                                <Plus className="w-3 h-3" />
                              </Button>
                            </div>
                            <div className="text-sm font-semibold text-foreground">
                              ${(Number(item.price) * item.quantity).toFixed(2)}
                            </div>
                          </div>
                        </CardContent>
                      </Card>
                    ))}
                  </div>
                )}
              </div>
            </div>
            {/* Total row always visible below order items and outside scroll area */}
            {cartItems.length > 0 && (
              <div className="flex items-center justify-between mb-6 px-2">
                <span className="font-semibold text-foreground">Total:</span>
                <span className="text-xl font-bold text-foreground">
                  ${cartTotal.toFixed(2)}
                </span>
              </div>
            )}

            {/* Placeholder for additional checkout form fields */}
            <div className="mb-6 text-muted-foreground">
              (Add delivery address, payment, etc. here)
            </div>
            <Button className="w-full bg-primary hover:bg-primary/90" size="lg" onClick={handleConfirmOrder}>
              Confirm Order
            </Button>
            <Link href="/customer/orders" className="block mt-4 text-center text-primary hover:underline">
              &larr; Back to Orders
            </Link>
          </div>
        </div>
      </div>
    </div>
  );
} 