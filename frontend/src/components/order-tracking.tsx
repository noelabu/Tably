"use client"

import React, { useState, useEffect } from 'react'
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card'
import { Badge } from "@/components/ui/badge"
import { Button } from "@/components/ui/button"
import { Separator } from "@/components/ui/separator"
import { 
  Package, 
  Clock, 
  CheckCircle2, 
  Truck, 
  MapPin, 
  Phone, 
  Bell, 
  User, 
  Star,
  Map,
  LogOut
} from "lucide-react"

interface OrderTrackingProps {
  orderId?: string
  onLogout?: () => void
}

export default function OrderTracking({ orderId = "ORD-2024-001234", onLogout }: OrderTrackingProps) {
  const [currentStage, setCurrentStage] = useState(3)
  const [estimatedDelivery] = useState("2:45 PM")
  const [driverName] = useState("Mike Johnson")
  const [driverRating] = useState("4.9")
  const [orderTotal] = useState("$45.97")
  const [orderItems] = useState([
    { name: "Classic Burger", quantity: 2 },
    { name: "Pizza Margherita", quantity: 1 },
    { name: "Caesar Salad", quantity: 1 }
  ])

  const stages = [
    {
      id: 0,
      title: "Order Confirmed",
      description: "We've received your order",
      timestamp: "12:45 PM",
      icon: CheckCircle2,
      completed: true
    },
    {
      id: 1,
      title: "Preparing Food",
      description: "Your order is being prepared",
      timestamp: "1:05 PM", 
      icon: Package,
      completed: true
    },
    {
      id: 2,
      title: "Ready for Pickup",
      description: "Order is ready and waiting",
      timestamp: "1:25 PM",
      icon: CheckCircle2,
      completed: true
    },
    {
      id: 3,
      title: "Out for Delivery",
      description: "Driver is on the way",
      timestamp: "1:35 PM",
      icon: Truck,
      completed: true
    },
    {
      id: 4,
      title: "Delivered",
      description: "Order has been delivered",
      timestamp: "Est. 2:45 PM",
      icon: MapPin,
      completed: false
    }
  ]

  return (
    <div className="min-h-screen bg-background p-6">
      <div className="max-w-4xl mx-auto space-y-6">
        {/* Header */}
        <div className="flex items-center justify-between">
          <div>
            <h1 className="text-3xl font-bold text-foreground">Order Tracking</h1>
            <p className="text-muted-foreground">Track your order in real-time</p>
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

        {/* Order Info */}
        <Card className="bg-card border-border">
          <CardContent className="p-6">
            <div className="flex items-center justify-between">
              <div>
                <h2 className="text-xl font-semibold text-card-foreground">Order #{orderId}</h2>
                <p className="text-muted-foreground">Bella Vista Italiana</p>
              </div>
              <Badge variant="secondary" className="bg-primary/10 text-primary">
                In Transit
              </Badge>
            </div>
          </CardContent>
        </Card>

        {/* Estimated Delivery */}
        <Card className="bg-card border-border">
          <CardContent className="p-6">
            <div className="flex items-center justify-between">
              <div className="flex items-center space-x-3">
                <Clock className="h-6 w-6 text-primary" />
                <div>
                  <h3 className="font-medium text-card-foreground">Estimated Delivery</h3>
                  <p className="text-lg font-semibold text-primary">{estimatedDelivery}</p>
                </div>
              </div>
              <Badge variant="secondary" className="bg-secondary text-secondary-foreground">
                On Time
              </Badge>
            </div>
          </CardContent>
        </Card>

        <div className="grid lg:grid-cols-3 gap-6">
          {/* Order Timeline */}
          <div className="lg:col-span-2">
            <Card className="bg-card border-border">
              <CardHeader className="bg-card border-b border-border">
                <h2 className="text-xl font-semibold text-card-foreground">Order Progress</h2>
              </CardHeader>
              <CardContent className="p-6">
                <div className="space-y-6">
                  {stages.map((stage, index) => {
                    const Icon = stage.icon
                    const isCompleted = stage.completed
                    const isCurrent = index === currentStage
                    
                    return (
                      <div key={stage.id} className="flex items-start space-x-4">
                        {/* Status Dot */}
                        <div className="flex flex-col items-center">
                          <div className={`
                            flex items-center justify-center w-10 h-10 rounded-full border-2
                            ${isCompleted 
                              ? 'bg-primary border-primary text-primary-foreground' 
                              : 'bg-background border-border text-muted-foreground'
                            }
                          `}>
                            <Icon className="h-5 w-5" />
                          </div>
                          {/* Connecting Line */}
                          {index < stages.length - 1 && (
                            <div className={`
                              w-0.5 h-12 mt-2
                              ${isCompleted ? 'bg-primary' : 'bg-border'}
                            `} />
                          )}
                        </div>
                        
                        {/* Stage Content */}
                        <div className="flex-1 min-w-0">
                          <div className="flex items-center justify-between">
                            <h3 className={`
                              font-medium
                              ${isCompleted ? 'text-card-foreground' : 'text-muted-foreground'}
                            `}>
                              {stage.title}
                            </h3>
                            <span className="text-sm text-muted-foreground">
                              {stage.timestamp}
                            </span>
                          </div>
                          <p className={`
                            text-sm mt-1
                            ${isCompleted ? 'text-muted-foreground' : 'text-muted-foreground'}
                          `}>
                            {stage.description}
                          </p>
                          {isCurrent && (
                            <Badge variant="secondary" className="mt-2 bg-primary/10 text-primary">
                              In Progress
                            </Badge>
                          )}
                        </div>
                      </div>
                    )
                  })}
                </div>
              </CardContent>
            </Card>
          </div>

          <div className="space-y-6">
            {/* Driver Info */}
            {currentStage >= 3 && (
              <Card className="bg-card border-border">
                <CardHeader className="bg-card border-b border-border">
                  <h2 className="text-lg font-semibold text-card-foreground">Your Driver</h2>
                </CardHeader>
                <CardContent className="p-6 space-y-4">
                  <div className="flex items-center space-x-3">
                    <div className="w-12 h-12 rounded-full bg-secondary flex items-center justify-center">
                      <User className="h-6 w-6 text-secondary-foreground" />
                    </div>
                    <div>
                      <h3 className="font-medium text-card-foreground">{driverName}</h3>
                      <div className="flex items-center space-x-1">
                        <Star className="h-4 w-4 fill-primary text-primary" />
                        <span className="text-sm text-muted-foreground">{driverRating}</span>
                      </div>
                    </div>
                  </div>
                  <Button variant="outline" className="w-full border-border text-foreground hover:bg-accent">
                    <Phone className="h-4 w-4 mr-2" />
                    Call Driver
                  </Button>
                </CardContent>
              </Card>
            )}

            {/* Live Map Placeholder */}
            {currentStage >= 3 && (
              <Card className="bg-card border-border">
                <CardHeader className="bg-card border-b border-border">
                  <h2 className="text-lg font-semibold text-card-foreground">Live Tracking</h2>
                </CardHeader>
                <CardContent className="p-6">
                  <div className="aspect-square bg-secondary rounded-lg flex items-center justify-center">
                    <div className="text-center space-y-2">
                      <Map className="h-8 w-8 text-muted-foreground mx-auto" />
                      <p className="text-sm text-muted-foreground">Map integration would appear here</p>
                    </div>
                  </div>
                </CardContent>
              </Card>
            )}

            {/* Order Summary */}
            <Card className="bg-card border-border">
              <CardHeader className="bg-card border-b border-border">
                <h2 className="text-lg font-semibold text-card-foreground">Order Summary</h2>
              </CardHeader>
              <CardContent className="p-6 space-y-4">
                <div className="space-y-2">
                  {orderItems.map((item, index) => (
                    <div key={index} className="flex justify-between text-sm">
                      <span className="text-card-foreground">
                        {item.quantity}x {item.name}
                      </span>
                    </div>
                  ))}
                </div>
                <Separator className="bg-border" />
                <div className="flex justify-between font-semibold">
                  <span className="text-card-foreground">Total</span>
                  <span className="text-primary">{orderTotal}</span>
                </div>
              </CardContent>
            </Card>

            {/* Notifications & Contact */}
            <Card className="bg-card border-border">
              <CardHeader className="bg-card border-b border-border">
                <h2 className="text-lg font-semibold text-card-foreground">Preferences</h2>
              </CardHeader>
              <CardContent className="p-6 space-y-4">
                <Button variant="outline" className="w-full justify-start border-border text-foreground hover:bg-accent">
                  <Bell className="h-4 w-4 mr-2" />
                  Notification Settings
                </Button>
                <Button variant="outline" className="w-full justify-start border-border text-foreground hover:bg-accent">
                  <Phone className="h-4 w-4 mr-2" />
                  Contact Support
                </Button>
              </CardContent>
            </Card>
          </div>
        </div>
      </div>
    </div>
  )
}