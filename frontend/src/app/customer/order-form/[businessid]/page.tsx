"use client";

import React, { useState, useEffect } from 'react';
import { Card, CardContent } from '@/components/ui/card';
import { Tabs, TabsList, TabsTrigger, TabsContent } from '@/components/ui/tabs';
import { Button } from '@/components/ui/button';
import { Badge } from '@/components/ui/badge';
import { ScrollArea } from '@/components/ui/scroll-area';
import { MessageCircle, Menu, Mic, Plus, Minus, ShoppingCart, Trash2, ChevronRight } from 'lucide-react';
import OrderingChatbotTab from '@/components/ordering-chatbot-tab';
import OrderingMenuTab from '@/components/ordering-menu-tab';
import OrderingVoiceTab from '@/components/ordering-voice-tab';
import { useAuthStore } from '@/stores/auth.store';
import { menuItemsService } from '@/services/menu-items';
import type { MenuItem } from '@/types/menu-items.types';
import Link from 'next/link';
import { useParams, useRouter } from 'next/navigation';
import { Dialog, DialogContent, DialogTitle } from '@/components/ui/dialog';
import { useCartStore } from '@/stores/cart.store';

// Remove the local CartItem interface and use the imported MenuItem type with an added quantity field

type CartItem = MenuItem & { quantity: number; customizations?: string[] };

const suggestedResponses = [
  "I'd like to see the burger menu",
  "What are your most popular items?",
  "Do you have any vegetarian options?",
  "What's the total for my order?"
];

export default function OrderFormPage() {
  const [activeMode, setActiveMode] = useState('chatbot');
  const [selectedCategory, setSelectedCategory] = useState('All');
  // Remove local cartItems state and use cart store
  const cartItems = useCartStore((state) => state.items);
  const addToCart = useCartStore((state) => state.addToCart);
  const updateQuantity = useCartStore((state) => state.updateQuantity);
  const removeFromCart = useCartStore((state) => state.removeFromCart);
  const clearCart = useCartStore((state) => state.clearCart);
  const [chatMessages, setChatMessages] = useState([
    {
      id: '1',
      type: 'bot',
      content: "Hi! I'm here to help you order. What can I get for you today?",
      timestamp: new Date(),
    },
  ]);
  const [inputMessage, setInputMessage] = useState('');
  const [isListening, setIsListening] = useState(false);
  const [transcribedText, setTranscribedText] = useState('');
  const [menuItems, setMenuItems] = useState<MenuItem[]>([]);
  const [categories, setCategories] = useState<string[]>(['All']);
  const [loadingMenu, setLoadingMenu] = useState(false);
  const [menuError, setMenuError] = useState<string | null>(null);
  const [showCartModal, setShowCartModal] = useState(false);

  const params = useParams();
  const businessId = params.businessid as string;
  const token = useAuthStore((state) => state.tokens?.access_token || '');
  const router = useRouter();

  useEffect(() => {
    if (businessId) {
      useCartStore.getState().setBusinessId(businessId);
    }
    async function fetchMenu() {
      setLoadingMenu(true);
      setMenuError(null);
      try {
        const response = await menuItemsService.getMenuItemsByBusiness(token, businessId);
        setMenuItems(response.items);
        // Extract unique categories from menu items
        const uniqueCategories = Array.from(
          new Set(
            response.items
              .map((item) => item.category)
              .filter((cat): cat is string => !!cat && cat.trim() !== '')
          )
        );
        setCategories(['All', ...uniqueCategories]);
      } catch (err) {
        setMenuError('Failed to load menu items.');
      } finally {
        setLoadingMenu(false);
      }
    }
    if (token && businessId) fetchMenu();
  }, [token, businessId]);

  // Remove all setCartItems and cartItems state logic, use the store methods instead

  const sendMessage = () => {
    if (!inputMessage.trim()) return;

    const newMessage = {
      id: Date.now().toString(),
      type: 'user',
      content: inputMessage,
      timestamp: new Date(),
    };

    setChatMessages([...chatMessages, newMessage]);
    setInputMessage('');

    // Simulate bot response
    setTimeout(() => {
      const botResponse = {
        id: (Date.now() + 1).toString(),
        type: 'bot',
        content: "I'd be happy to help! Let me check our menu for you.",
        timestamp: new Date(),
      };
      setChatMessages(prev => [...prev, botResponse]);
    }, 1000);
  };

  const handleSuggestedResponse = (response: string) => {
    setInputMessage(response);
  };

  const toggleVoiceListening = () => {
    setIsListening(!isListening);
    if (!isListening) {
      setTranscribedText("Listening... say something like 'I want a burger'");
    } else {
      setTranscribedText("I want a classic burger with extra cheese");
    }
  };

  const filteredItems = selectedCategory === 'All'
    ? menuItems
    : menuItems.filter(item => item.category === selectedCategory);

  const cartTotal = cartItems.reduce((total, item) => total + (Number(item.price) * item.quantity), 0);
  const cartItemCount = cartItems.reduce((total, item) => total + item.quantity, 0);

  return (
    <div className="min-h-screen bg-background">
      {/* Breadcrumbs */}
      <nav className="bg-white border-b">
        <div className="max-w-7xl mx-auto px-2 sm:px-4 lg:px-8 flex items-center h-12 space-x-2 text-sm">
          <Link href="/customer/dashboard" className="text-muted-foreground hover:text-primary">Dashboard</Link>
          <ChevronRight className="h-4 w-4 text-muted-foreground" />
          <Link href="/customer/orders" className="text-muted-foreground hover:text-primary">Orders</Link>
          <ChevronRight className="h-4 w-4 text-muted-foreground" />
          <span className="text-primary font-medium">Order Form</span>
        </div>
      </nav>
      <div className="max-w-7xl mx-auto px-2 sm:px-4 lg:px-8 flex flex-col md:flex-row h-auto md:h-screen gap-0 md:gap-6">
        {/* Main Content */}
        <div className="flex-1 flex flex-col min-w-0">
          {/* Header */}
          <div className="bg-card border-b border-border px-4 sm:px-6 py-4">
            <h1 className="text-xl sm:text-2xl font-semibold text-foreground mb-4">Place Your Order</h1>
            <Tabs value={activeMode} onValueChange={setActiveMode} className="w-full">
              <TabsList className="grid w-full max-w-md grid-cols-3">
                <TabsTrigger value="chatbot" className="flex items-center gap-2">
                  <MessageCircle className="w-4 h-4" />
                  Chat Bot
                </TabsTrigger>
                <TabsTrigger value="menu" className="flex items-center gap-2">
                  <Menu className="w-4 h-4" />
                  Menu
                </TabsTrigger>
                <TabsTrigger value="voice" className="flex items-center gap-2">
                  <Mic className="w-4 h-4" />
                  Voice
                </TabsTrigger>
              </TabsList>
            </Tabs>
          </div>

          {/* Content Area */}
          <div className="flex-1 p-2 sm:p-6 overflow-auto">
            {loadingMenu ? (
              <div className="flex justify-center items-center h-64">
                <div className="animate-spin rounded-full h-10 w-10 border-b-2 border-primary"></div>
              </div>
            ) : (
              <Tabs value={activeMode} className="h-full">
                {/* Chatbot Mode */}
                <TabsContent value="chatbot" className="h-full flex flex-col">
                  <OrderingChatbotTab
                    chatMessages={chatMessages}
                    inputMessage={inputMessage}
                    onInputChange={(e) => setInputMessage(e.target.value)}
                    onSendMessage={sendMessage}
                    onSuggestedResponse={handleSuggestedResponse}
                    suggestedResponses={suggestedResponses}
                  />
                </TabsContent>

                {/* Menu Mode */}
                <TabsContent value="menu" className="h-full">
                  <OrderingMenuTab
                    categories={categories}
                    selectedCategory={selectedCategory}
                    setSelectedCategory={setSelectedCategory}
                    filteredItems={filteredItems}
                    addToCart={addToCart}
                  />
                </TabsContent>

                {/* Voice Mode */}
                <TabsContent value="voice" className="h-full">
                  <OrderingVoiceTab
                    isListening={isListening}
                    transcribedText={transcribedText}
                    toggleVoiceListening={toggleVoiceListening}
                  />
                </TabsContent>
              </Tabs>
            )}
          </div>
        </div>

        {/* Cart Sidebar (desktop only) */}
        <div className="hidden md:flex w-80 bg-card border-t md:border-t-0 md:border-l border-border flex-col min-h-[200px] md:min-h-0">
          <div className="p-4 border-b border-border">
            <div className="flex items-center justify-between">
              <h2 className="text-lg font-semibold text-foreground flex items-center gap-2">
                <ShoppingCart className="w-5 h-5" />
                Your Order
              </h2>
              <Badge variant="secondary">
                {cartItemCount} items
              </Badge>
            </div>
          </div>

          <ScrollArea className="flex-1 p-4">
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
          </ScrollArea>

          {cartItems.length > 0 && (
            <div className="p-4 border-t border-border space-y-4">
              <div className="flex items-center justify-between">
                <span className="font-semibold text-foreground">Total:</span>
                <span className="text-xl font-bold text-foreground">
                  ${cartTotal.toFixed(2)}
                </span>
              </div>
              
              <Button className="w-full bg-primary hover:bg-primary/90" onClick={() => router.push('/customer/check-out')}>
                Proceed to Checkout
              </Button>
            </div>
          )}
        </div>

        {/* Mobile Cart Button */}
        <div className="md:hidden fixed bottom-0 left-0 right-0 z-30 bg-white border-t border-border p-2 flex justify-center shadow-lg">
          <Button
            className="w-full max-w-xs flex items-center gap-2"
            onClick={() => setShowCartModal(true)}
            disabled={cartItems.length === 0}
          >
            <ShoppingCart className="w-5 h-5" />
            View Cart
            {cartItems.length > 0 && (
              <Badge variant="secondary" className="ml-2">
                {cartItemCount}
              </Badge>
            )}
          </Button>
        </div>

        {/* Mobile Cart Modal */}
        <Dialog open={showCartModal} onOpenChange={setShowCartModal}>
          <DialogContent className="w-full max-w-md mx-auto p-0">
            <DialogTitle asChild>
              <div className="p-4 border-b border-border flex items-center justify-between">
                <h2 className="text-lg font-semibold text-foreground flex items-center gap-2">
                  <ShoppingCart className="w-5 h-5" />
                  Your Order
                </h2>
                <Badge variant="secondary">
                  {cartItemCount} items
                </Badge>
              </div>
            </DialogTitle>
            <ScrollArea className="flex-1 p-4 max-h-[60vh]">
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
            </ScrollArea>
            {cartItems.length > 0 && (
              <div className="p-4 border-t border-border space-y-4">
                <div className="flex items-center justify-between">
                  <span className="font-semibold text-foreground">Total:</span>
                  <span className="text-xl font-bold text-foreground">
                    ${cartTotal.toFixed(2)}
                  </span>
                </div>
                <Button className="w-full bg-primary hover:bg-primary/90" onClick={() => router.push('/customer/check-out')}>
                  Proceed to Checkout
                </Button>
              </div>
            )}
          </DialogContent>
        </Dialog>
      </div>
    </div>
  );
} 