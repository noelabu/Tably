"use client"

import React, { useState, useEffect } from 'react'
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card'
import { Tabs, TabsList, TabsTrigger, TabsContent } from '@/components/ui/tabs'
import { Button } from '@/components/ui/button'
import { Input } from '@/components/ui/input'
import { Badge } from '@/components/ui/badge'
import { ScrollArea } from '@/components/ui/scroll-area'
import { Separator } from '@/components/ui/separator'
import { 
  MessageCircle, 
  Menu, 
  Mic, 
  Send, 
  Plus, 
  Minus, 
  ShoppingCart, 
  Trash2,
  Clock,
  Star,
  ChefHat,
  Bot,
  Send as SendIcon,
  User,
  LogOut,
  Loader2
} from 'lucide-react'
import { useAuth } from '@/hooks/use-auth'
import { useAuthStore } from '@/stores/auth.store'
import { OrderingChatService, ChatMessage } from '@/services/ordering-chat'
import OrderingChatbotTab from './ordering-chatbot-tab';
import OrderingMenuTab from './ordering-menu-tab';
import OrderingVoiceTab from './ordering-voice-tab';
import { useAuthStore } from '@/stores/auth.store';
import { menuItemsService } from '@/services/menu-items';
import type { MenuItem } from '@/types/menu-items.types';

interface OrderingSystemProps {
  onLogout?: () => void
}

// Remove the local MenuItem interface definition
// interface MenuItem {
//   id: string
//   name: string
//   description: string
//   price: number
//   category: string
//   image?: string
//   rating?: number
//   prepTime?: number
//   popular?: boolean
// }

// Remove the local CartItem interface and use the imported MenuItem type with an added quantity field

type CartItem = MenuItem & { quantity: number; customizations?: string[] };

const suggestedResponses = [
  "I'd like to see the burger menu",
  "What are your most popular items?",
  "Do you have any vegetarian options?",
  "What's the total for my order?"
]

export default function OrderingSystem({ onLogout }: OrderingSystemProps) {
  const { user } = useAuth()
  const [activeMode, setActiveMode] = useState('chatbot')
  const [selectedCategory, setSelectedCategory] = useState('All')
  const [cartItems, setCartItems] = useState<CartItem[]>([])
  const [chatMessages, setChatMessages] = useState<ChatMessage[]>([
    {
      id: '1',
      type: 'bot',
      content: "Hi! I'm here to help you order. What can I get for you today?",
      timestamp: new Date()
    }
  ])
  const [inputMessage, setInputMessage] = useState('')
  const [isListening, setIsListening] = useState(false)
  const [transcribedText, setTranscribedText] = useState('')
  const [isLoading, setIsLoading] = useState(false)
  const [chatService, setChatService] = useState<OrderingChatService | null>(null)
  const [useStreaming, setUseStreaming] = useState(true)

  // Initialize chat service when user is available
  useEffect(() => {
    if (user) {
      // Get the token from the auth store
      const authStore = useAuthStore.getState()
      const token = authStore.tokens?.access_token
      if (token) {
        setChatService(new OrderingChatService(token))
      }
    }
  }, [user])

  // New state for menu items and categories
  const [menuItems, setMenuItems] = useState<MenuItem[]>([]);
  const [categories, setCategories] = useState<string[]>(['All']);
  const [loadingMenu, setLoadingMenu] = useState(false);
  const [menuError, setMenuError] = useState<string | null>(null);

  const businessId = '5f5234da-631e-4196-b9d0-fab5901d483d';
  const token = useAuthStore((state) => state.tokens?.access_token || '');

  useEffect(() => {
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
    fetchMenu();
  }, [token, businessId]);

  const addToCart = (item: MenuItem) => {
    const existingItem = cartItems.find(cartItem => cartItem.id === item.id)
    if (existingItem) {
      setCartItems(cartItems.map(cartItem => 
        cartItem.id === item.id 
          ? { ...cartItem, quantity: cartItem.quantity + 1 }
          : cartItem
      ))
    } else {
      setCartItems([...cartItems, { ...item, quantity: 1 }])
    }
  }

  const updateQuantity = (id: string, change: number) => {
    setCartItems(cartItems.map(item => {
      if (item.id === id) {
        const newQuantity = Math.max(0, item.quantity + change)
        return newQuantity === 0 ? null : { ...item, quantity: newQuantity }
      }
      return item
    }).filter(Boolean) as CartItem[])
  }

  const removeFromCart = (id: string) => {
    setCartItems(cartItems.filter(item => item.id !== id))
  }

  const sendMessage = async () => {
    if (!inputMessage.trim() || isLoading) return
    
    const newMessage: ChatMessage = {
      id: Date.now().toString(),
      type: 'user',
      content: inputMessage,
      timestamp: new Date()
    }
    
    setChatMessages(prev => [...prev, newMessage])
    const currentMessage = inputMessage
    setInputMessage('')
    setIsLoading(true)
    
    try {
      // Only use orchestrator for customers
      if (user?.role === 'customer' && chatService) {
        // Build context from recent messages and cart
        const context = buildChatContext()
        
        if (useStreaming) {
          // Handle streaming response
          const botMessage: ChatMessage = {
            id: (Date.now() + 1).toString(),
            type: 'bot',
            content: '',
            timestamp: new Date()
          }
          setChatMessages(prev => [...prev, botMessage])
          
          try {
            for await (const chunk of chatService.streamMessage(currentMessage, context)) {
              if (chunk.type === 'message') {
                setChatMessages(prev => 
                  prev.map(msg => 
                    msg.id === botMessage.id 
                      ? { ...msg, content: msg.content + chunk.content }
                      : msg
                  )
                )
              } else if (chunk.type === 'error') {
                setChatMessages(prev => 
                  prev.map(msg => 
                    msg.id === botMessage.id 
                      ? { ...msg, content: "Sorry, there was an error processing your request." }
                      : msg
                  )
                )
                break
              }
            }
          } catch (error) {
            setChatMessages(prev => 
              prev.map(msg => 
                msg.id === botMessage.id 
                  ? { ...msg, content: "Sorry, there was an error processing your request." }
                  : msg
              )
            )
          }
        } else {
          // Handle non-streaming response
          const response = await chatService.sendMessage(currentMessage, context)
          const botResponse: ChatMessage = {
            id: (Date.now() + 1).toString(),
            type: 'bot',
            content: response.response,
            timestamp: new Date()
          }
          setChatMessages(prev => [...prev, botResponse])
        }
      } else {
        // Fallback for non-customers or when service not available
        setTimeout(() => {
          const botResponse: ChatMessage = {
            id: (Date.now() + 1).toString(),
            type: 'bot',
            content: "I'd be happy to help! Let me check our menu for you.",
            timestamp: new Date()
          }
          setChatMessages(prev => [...prev, botResponse])
        }, 1000)
      }
    } catch (error) {
      console.error('Error sending message:', error)
      const errorResponse: ChatMessage = {
        id: (Date.now() + 1).toString(),
        type: 'bot',
        content: "Sorry, there was an error processing your request. Please try again.",
        timestamp: new Date()
      }
      setChatMessages(prev => [...prev, errorResponse])
    } finally {
      setIsLoading(false)
    }
  }

  const buildChatContext = (): string => {
    const recentMessages = chatMessages.slice(-5).map(msg => 
      `${msg.type}: ${msg.content}`
    ).join('\n')
    
    const cartContext = cartItems.length > 0 
      ? `Current cart: ${cartItems.map(item => `${item.name} x${item.quantity}`).join(', ')}`
      : 'Cart is empty'
    
    return `Recent conversation:\n${recentMessages}\n\n${cartContext}`
  }

  const handleSuggestedResponse = (response: string) => {
    setInputMessage(response)
  }

  const toggleVoiceListening = () => {
    setIsListening(!isListening)
    if (!isListening) {
      setTranscribedText("Listening... say something like 'I want a burger'")
    } else {
      setTranscribedText("I want a classic burger with extra cheese")
    }
  }

  const filteredItems = selectedCategory === 'All' 
    ? menuItems 
    : menuItems.filter(item => item.category === selectedCategory)

  const cartTotal = cartItems.reduce((total, item) => total + (item.price * item.quantity), 0)
  const cartItemCount = cartItems.reduce((total, item) => total + item.quantity, 0)

  return (
    <div className="min-h-screen bg-background">
      {/* Section Header (not sticky) */}
      <section className="bg-card border-b px-6 py-4">
        <div className="max-w-7xl mx-auto flex items-center justify-between">
          <div>
            <h1 className="text-2xl font-bold text-foreground">Bella Vista Italiana</h1>
            <p className="text-muted-foreground">Authentic Italian cuisine</p>
          </div>
          <div className="flex items-center gap-4">
            <div className="relative">
              <Button variant="outline" size="sm" className="gap-2">
                <ShoppingCart className="h-4 w-4" />
                Cart ({cartItems.reduce((sum, item) => sum + item.quantity, 0)})
              </Button>
            </div>
            {onLogout && (
              <Button
                variant="outline"
                size="sm"
                onClick={onLogout}
                className="text-red-600 hover:text-red-700 hover:bg-red-50"
              >
                <LogOut className="h-4 w-4 mr-1" />
                Logout
              </Button>
            )}
          </div>
        </div>
      </section>

      <div className="flex h-screen">
        {/* Main Content */}
        <div className="flex-1 flex flex-col">
          {/* Header */}
          <div className="bg-card border-b border-border px-6 py-4">
            <h1 className="text-2xl font-semibold text-foreground mb-4">Place Your Order</h1>
            
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
          <div className="flex-1 p-6 overflow-hidden">
            <Tabs value={activeMode} className="h-full">
              {/* Chatbot Mode */}
              <TabsContent value="chatbot" className="h-full flex flex-col">
                <div className="flex-1 flex flex-col space-y-4">
                  {/* AI Assistant Status */}
                  {user?.role === 'customer' && chatService && (
                    <div className="flex items-center gap-2 text-sm text-muted-foreground bg-muted/50 rounded-lg p-2">
                      <Bot className="w-4 h-4" />
                      AI Ordering Assistant Active
                      <Badge variant="secondary" className="ml-auto">
                        {useStreaming ? 'Streaming' : 'Standard'}
                      </Badge>
                    </div>
                  )}
                  
                  {/* Chat Messages */}
                  <ScrollArea className="flex-1 bg-muted rounded-lg p-4">
                    <div className="space-y-4">
                      {chatMessages.map((message) => (
                        <div
                          key={message.id}
                          className={`flex ${message.type === 'user' ? 'justify-end' : 'justify-start'}`}
                        >
                          <div
                            className={`max-w-xs lg:max-w-md px-4 py-2 rounded-lg ${
                              message.type === 'user'
                                ? 'bg-primary text-primary-foreground'
                                : 'bg-card text-card-foreground border border-border'
                            }`}
                          >
                            {message.content}
                          </div>
                        </div>
                      ))}
                    </div>
                  </ScrollArea>

                  {/* Suggested Responses */}
                  <div className="flex flex-wrap gap-2">
                    {suggestedResponses.map((response, index) => (
                      <Button
                        key={index}
                        variant="outline"
                        size="sm"
                        onClick={() => handleSuggestedResponse(response)}
                        className="text-sm"
                      >
                        {response}
                      </Button>
                    ))}
                  </div>

                  {/* Message Input */}
                  <div className="flex gap-2">
                    <Input
                      value={inputMessage}
                      onChange={(e) => setInputMessage(e.target.value)}
                      placeholder={isLoading ? "Waiting for response..." : "Type your message..."}
                      onKeyPress={(e) => e.key === 'Enter' && !isLoading && sendMessage()}
                      disabled={isLoading}
                      className="flex-1"
                    />
                    <Button 
                      onClick={sendMessage} 
                      disabled={isLoading || !inputMessage.trim()}
                      className="bg-primary hover:bg-primary/90"
                    >
                      {isLoading ? (
                        <Loader2 className="w-4 h-4 animate-spin" />
                      ) : (
                        <SendIcon className="w-4 h-4" />
                      )}
                    </Button>
                  </div>
                </div>
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
          </div>
        </div>

        {/* Cart Sidebar */}
        <div className="w-80 bg-card border-l border-border flex flex-col">
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
                            ${item.price.toFixed(2)}
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
                          ${(item.price * item.quantity).toFixed(2)}
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
              
              <Button className="w-full bg-primary hover:bg-primary/90">
                Proceed to Checkout
              </Button>
            </div>
          )}
        </div>
      </div>
    </div>
  )
}