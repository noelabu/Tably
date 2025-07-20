"use client"

import React, { useState, useEffect, useRef } from 'react'
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card'
import { Button } from '@/components/ui/button'
import { Input } from '@/components/ui/input'
import { ScrollArea } from '@/components/ui/scroll-area'
import { Badge } from '@/components/ui/badge'
import { Separator } from '@/components/ui/separator'
import { 
  MessageCircle, 
  Send, 
  Bot, 
  User, 
  Loader2,
  Settings,
  Play,
  Pause
} from 'lucide-react'
import { useAuth } from '@/hooks/use-auth'
import { useAuthStore } from '@/stores/auth.store'
import { OrderingChatService, ChatMessage } from '@/services/ordering-chat'

export default function ChatExamplePage() {
  const { user, isAuthenticated } = useAuth()
  const businessId = '5eff8f12-7d43-4b0d-b3f7-e762a7903a82' // Fixed business ID for testing
  
  const [chatMessages, setChatMessages] = useState<ChatMessage[]>([
    {
      id: '1',
      type: 'bot',
      content: "Hello! I'm the AI ordering assistant for this restaurant. I have access to our full menu. Try asking me about our pizzas, recommendations, or place an order!",
      timestamp: new Date()
    }
  ])
  const [inputMessage, setInputMessage] = useState('')
  const [isLoading, setIsLoading] = useState(false)
  const [chatService, setChatService] = useState<OrderingChatService | null>(null)
  const [useStreaming, setUseStreaming] = useState(false)
  const [connectionStatus, setConnectionStatus] = useState<'disconnected' | 'connecting' | 'connected' | 'error'>('disconnected')
  const messagesEndRef = useRef<HTMLDivElement>(null)

  // Initialize chat service when user is available
  useEffect(() => {
    if (user && isAuthenticated) {
      const authStore = useAuthStore.getState()
      const token = authStore.tokens?.access_token
      console.log('Auth state:', { user, isAuthenticated, hasToken: !!token })
      
      if (token) {
        setChatService(new OrderingChatService(token))
        setConnectionStatus('connected')
      } else {
        console.error('No access token found in auth store')
        setConnectionStatus('error')
      }
    } else {
      setConnectionStatus('disconnected')
    }
  }, [user, isAuthenticated])

  // Auto-scroll to bottom
  useEffect(() => {
    messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' })
  }, [chatMessages])

  const buildChatContext = (): string => {
    const recentMessages = chatMessages.slice(-5).map(msg => 
      `${msg.type}: ${msg.content}`
    ).join('\n')
    
    return `Recent conversation:\n${recentMessages}\n\nTest Environment: This is a demo chat interface for testing the orchestrator endpoint.`
  }

  const sendMessage = async () => {
    if (!inputMessage.trim() || isLoading || !chatService) return
    
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
    setConnectionStatus('connecting')
    
    try {
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
        setConnectionStatus('connected')
        
        try {
          for await (const chunk of chatService.streamMessage(currentMessage, context, businessId)) {
            if (chunk.type === 'message') {
              setChatMessages(prev => 
                prev.map(msg => 
                  msg.id === botMessage.id 
                    ? { ...msg, content: msg.content + chunk.content }
                    : msg
                )
              )
            } else if (chunk.type === 'error') {
              setConnectionStatus('error')
              setChatMessages(prev => 
                prev.map(msg => 
                  msg.id === botMessage.id 
                    ? { ...msg, content: chunk.error || "Sorry, there was an error processing your request." }
                    : msg
                )
              )
              break
            } else if (chunk.type === 'done') {
              break
            }
          }
        } catch (error) {
          setConnectionStatus('error')
          setChatMessages(prev => 
            prev.map(msg => 
              msg.id === botMessage.id 
                ? { ...msg, content: "Sorry, there was an error with the streaming connection." }
                : msg
            )
          )
        }
      } else {
        // Handle non-streaming response
        const response = await chatService.sendMessage(currentMessage, context, businessId)
        const botResponse: ChatMessage = {
          id: (Date.now() + 1).toString(),
          type: 'bot',
          content: response.response,
          timestamp: new Date()
        }
        setChatMessages(prev => [...prev, botResponse])
        setConnectionStatus('connected')
      }
    } catch (error) {
      console.error('Error sending message:', error)
      setConnectionStatus('error')
      
      let errorMessage = "Sorry, there was an error processing your request."
      if (error instanceof Error && error.message.includes('401')) {
        errorMessage = "Authentication error. Please log in again."
      } else if (error instanceof Error && error.message.includes('403')) {
        errorMessage = "Access denied. Please check your permissions."
      }
      
      const errorResponse: ChatMessage = {
        id: (Date.now() + 1).toString(),
        type: 'bot',
        content: errorMessage,
        timestamp: new Date()
      }
      setChatMessages(prev => [...prev, errorResponse])
    } finally {
      setIsLoading(false)
    }
  }

  const clearChat = () => {
    setChatMessages([
      {
        id: '1',
        type: 'bot',
        content: "Chat cleared! I'm ready to help you again.",
        timestamp: new Date()
      }
    ])
  }

  const getConnectionStatusBadge = () => {
    const statusMap = {
      disconnected: { variant: 'destructive' as const, text: 'Disconnected' },
      connecting: { variant: 'secondary' as const, text: 'Connecting...' },
      connected: { variant: 'default' as const, text: 'Connected' },
      error: { variant: 'destructive' as const, text: 'Error' }
    }
    return statusMap[connectionStatus]
  }

  if (!isAuthenticated || !user) {
    return (
      <div className="min-h-screen bg-background flex items-center justify-center">
        <Card className="w-full max-w-md">
          <CardHeader>
            <CardTitle className="text-center">Authentication Required</CardTitle>
          </CardHeader>
          <CardContent className="text-center">
            <p className="text-muted-foreground mb-4">
              Please log in to test the chat streaming functionality.
            </p>
            <div className="space-y-2">
              <Button asChild className="w-full">
                <a href="/login">Go to Login</a>
              </Button>
              <div className="text-xs text-muted-foreground">
                Current state: {isAuthenticated ? 'authenticated' : 'not authenticated'}, 
                User: {user ? 'loaded' : 'not loaded'}
              </div>
            </div>
          </CardContent>
        </Card>
      </div>
    )
  }

  return (
    <div className="min-h-screen bg-background">
      {/* Header */}
      <div className="bg-card border-b px-6 py-4">
        <div className="max-w-4xl mx-auto flex items-center justify-between">
          <div>
            <h1 className="text-2xl font-bold text-foreground">Chat Streaming Example</h1>
            <p className="text-muted-foreground">Test the AI ordering assistant streaming endpoint</p>
          </div>
          <div className="flex items-center gap-4">
            <Badge {...getConnectionStatusBadge()} className="flex items-center gap-1">
              <div className={`w-2 h-2 rounded-full ${
                connectionStatus === 'connected' ? 'bg-green-400' :
                connectionStatus === 'connecting' ? 'bg-yellow-400 animate-pulse' :
                'bg-red-400'
              }`} />
              {getConnectionStatusBadge().text}
            </Badge>
            <Button asChild variant="outline" size="sm">
              <a href="/customer/dashboard">Back to Dashboard</a>
            </Button>
          </div>
        </div>
      </div>

      <div className="w-full p-4">
        <div className="grid grid-cols-1 lg:grid-cols-3 gap-4 max-w-7xl mx-auto">
          {/* Chat Interface */}
          <div className="lg:col-span-2">
            <Card className="h-[800px] flex flex-col">
              <CardHeader className="pb-3">
                <div className="flex items-center justify-between">
                  <CardTitle className="flex items-center gap-2">
                    <MessageCircle className="w-5 h-5" />
                    AI Chat Assistant
                  </CardTitle>
                  <div className="flex items-center gap-2">
                    <Button
                      variant="outline"
                      size="sm"
                      onClick={() => setUseStreaming(!useStreaming)}
                      className="flex items-center gap-1"
                    >
                      {useStreaming ? <Pause className="w-3 h-3" /> : <Play className="w-3 h-3" />}
                      {useStreaming ? 'Streaming' : 'Standard'}
                    </Button>
                    <Button
                      variant="outline"
                      size="sm"
                      onClick={clearChat}
                    >
                      Clear
                    </Button>
                  </div>
                </div>
              </CardHeader>
              
              <CardContent className="flex-1 flex flex-col p-0 min-h-0">
                {/* Messages */}
                <div className="flex-1 overflow-y-auto overflow-x-hidden">
                  <div className="space-y-3 p-4">
                    {chatMessages.map((message) => (
                      <div
                        key={message.id}
                        className={`flex ${message.type === 'user' ? 'justify-end' : 'justify-start'}`}
                      >
                        <div
                          className={`max-w-[85%] lg:max-w-[75%] rounded-lg p-3 ${
                            message.type === 'user'
                              ? 'bg-primary text-primary-foreground'
                              : 'bg-muted'
                          }`}
                        >
                          <div className="flex items-start gap-2">
                            {message.type === 'bot' && <Bot className="w-4 h-4 mt-0.5 flex-shrink-0" />}
                            {message.type === 'user' && <User className="w-4 h-4 mt-0.5 flex-shrink-0" />}
                            <div className="flex-1 min-w-0">
                              <p className="text-sm whitespace-pre-wrap break-words">{message.content}</p>
                              <p className="text-xs opacity-60 mt-1">
                                {message.timestamp.toLocaleTimeString()}
                              </p>
                            </div>
                          </div>
                        </div>
                      </div>
                    ))}
                    {isLoading && (
                      <div className="flex justify-start">
                        <div className="max-w-[85%] lg:max-w-[75%] bg-muted rounded-lg p-3 flex items-center gap-2">
                          <Bot className="w-4 h-4 flex-shrink-0" />
                          <Loader2 className="w-4 h-4 animate-spin flex-shrink-0" />
                          <span className="text-sm">Typing...</span>
                        </div>
                      </div>
                    )}
                    <div ref={messagesEndRef} />
                  </div>
                </div>

                {/* Input */}
                <div className="p-4 border-t">
                  <div className="flex gap-2">
                    <Input
                      value={inputMessage}
                      onChange={(e) => setInputMessage(e.target.value)}
                      placeholder={isLoading ? "Waiting for response..." : "Type your message..."}
                      onKeyDown={(e) => e.key === 'Enter' && !isLoading && sendMessage()}
                      disabled={isLoading || !chatService}
                      className="flex-1"
                    />
                    <Button 
                      onClick={sendMessage} 
                      disabled={isLoading || !inputMessage.trim() || !chatService}
                      className="bg-primary hover:bg-primary/90"
                    >
                      {isLoading ? (
                        <Loader2 className="w-4 h-4 animate-spin" />
                      ) : (
                        <Send className="w-4 h-4" />
                      )}
                    </Button>
                  </div>
                </div>
              </CardContent>
            </Card>
          </div>

          {/* Info Panel */}
          <div className="space-y-4">
            <Card>
              <CardHeader>
                <CardTitle className="text-lg flex items-center gap-2">
                  <Settings className="w-4 h-4" />
                  Settings
                </CardTitle>
              </CardHeader>
              <CardContent className="space-y-3">
                <div className="flex items-center justify-between">
                  <span className="text-sm">Mode:</span>
                  <Badge variant={useStreaming ? 'default' : 'secondary'}>
                    {useStreaming ? 'Streaming' : 'Standard'}
                  </Badge>
                </div>
                <div className="flex items-center justify-between">
                  <span className="text-sm">User:</span>
                  <Badge variant="outline">{user?.role || 'Unknown'}</Badge>
                </div>
                <div className="flex items-center justify-between">
                  <span className="text-sm">Status:</span>
                  <Badge {...getConnectionStatusBadge()} />
                </div>
                <Separator className="my-2" />
                <div className="space-y-1">
                  <p className="text-xs font-medium">Business ID:</p>
                  <code className="text-xs bg-muted p-1 rounded block break-all">
                    {businessId}
                  </code>
                </div>
                <Separator className="my-2" />
                <div className="space-y-1">
                  <p className="text-xs font-medium">Debug Info:</p>
                  <div className="text-xs bg-muted p-2 rounded">
                    <div>Auth: {isAuthenticated ? '✓' : '✗'}</div>
                    <div>User: {user ? '✓' : '✗'}</div>
                    <div>Service: {chatService ? '✓' : '✗'}</div>
                    <div>Token: {useAuthStore.getState().tokens?.access_token ? '✓' : '✗'}</div>
                  </div>
                </div>
              </CardContent>
            </Card>

            <Card>
              <CardHeader>
                <CardTitle className="text-lg">Test Examples</CardTitle>
              </CardHeader>
              <CardContent>
                <div className="space-y-2">
                  <Button
                    variant="outline"
                    size="sm"
                    className="w-full justify-start text-left"
                    onClick={() => setInputMessage("What pizzas do you have on the menu?")}
                  >
                    "What pizzas do you have on the menu?"
                  </Button>
                  <Button
                    variant="outline"
                    size="sm"
                    className="w-full justify-start text-left"
                    onClick={() => setInputMessage("I want to order a large Margherita pizza")}
                  >
                    "I want to order a large Margherita pizza"
                  </Button>
                  <Button
                    variant="outline"
                    size="sm"
                    className="w-full justify-start text-left"
                    onClick={() => setInputMessage("Show me your vegetarian options with prices")}
                  >
                    "Show me your vegetarian options with prices"
                  </Button>
                  <Button
                    variant="outline"
                    size="sm"
                    className="w-full justify-start text-left"
                    onClick={() => setInputMessage("Hola, quiero ver el menú de pizzas")}
                  >
                    "Hola, quiero ver el menú de pizzas"
                  </Button>
                </div>
              </CardContent>
            </Card>

            <Card>
              <CardHeader>
                <CardTitle className="text-lg">Endpoint Info</CardTitle>
              </CardHeader>
              <CardContent className="space-y-2">
                <div className="text-sm">
                  <span className="font-medium">URL:</span>
                  <code className="ml-2 text-xs bg-muted p-1 rounded">
                    /api/v1/ordering/chat/stream
                  </code>
                </div>
                <div className="text-sm">
                  <span className="font-medium">Method:</span>
                  <code className="ml-2 text-xs bg-muted p-1 rounded">
                    POST
                  </code>
                </div>
                <div className="text-sm">
                  <span className="font-medium">Auth:</span>
                  <code className="ml-2 text-xs bg-muted p-1 rounded">
                    Bearer Token
                  </code>
                </div>
              </CardContent>
            </Card>
          </div>
        </div>
      </div>
    </div>
  )
}