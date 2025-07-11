"use client"

import React, { useState, useEffect } from "react"
import AuthInterface from "@/components/auth-interface"
import RestaurantSelection from "@/components/restaurant-selection"
import OrderingSystem from "@/components/ordering-system"
import BusinessDashboard from "@/components/business-dashboard"
import BusinessOnboarding from "@/components/business-onboarding"
import OrderTracking from "@/components/order-tracking"
import { OrderHistory } from "@/components/order-history"

export default function Page() {
  const [currentView, setCurrentView] = useState<string>("auth")
  const [userType, setUserType] = useState<string | null>(null)
  const [isAuthenticated, setIsAuthenticated] = useState(false)
  const [currentOrder, setCurrentOrder] = useState<string | null>(null)

  const handleLogin = (email: string, password: string) => {
    console.log("Login attempt:", email)
    setIsAuthenticated(true)
    // Simulate user type detection
    if (email.includes("business") || email.includes("restaurant")) {
      setUserType("business")
      setCurrentView("business-dashboard")
    } else {
      setUserType("customer")
      setCurrentView("restaurant-selection")
    }
  }

  const handleRegister = (data: {
    name: string
    email: string
    password: string
    role: string
    acceptTerms: boolean
  }) => {
    console.log("Registration attempt:", data)
    setIsAuthenticated(true)
    setUserType(data.role === "business-owner" ? "business" : "customer")
    
    if (data.role === "business-owner") {
      setCurrentView("business-onboarding")
    } else {
      setCurrentView("restaurant-selection")
    }
  }

  const handleSocialLogin = (provider: string) => {
    console.log("Social login attempt:", provider)
    setIsAuthenticated(true)
    setUserType("customer")
    setCurrentView("restaurant-selection")
  }

  const handleForgotPassword = (email: string) => {
    console.log("Password reset requested for:", email)
  }

  const handleLogout = () => {
    setIsAuthenticated(false)
    setUserType(null)
    setCurrentView("auth")
    setCurrentOrder(null)
    console.log("User logged out successfully")
  }

  const handleRestaurantSelect = () => {
    setCurrentView("ordering-system")
  }

  const handleOrderPlace = () => {
    setCurrentOrder("ORD-2024-001234")
    setCurrentView("order-tracking")
  }

  const handleBusinessOnboardingComplete = () => {
    setCurrentView("business-dashboard")
  }

  const handleNavigation = (view: string) => {
    setCurrentView(view)
  }

  // Customer workflow
  const renderCustomerFlow = () => {
    switch (currentView) {
      case "restaurant-selection":
        return (
          <div onClick={handleRestaurantSelect}>
            <RestaurantSelection 
              onLogout={handleLogout} 
              onOrderHistory={() => setCurrentView("order-history")}
            />
          </div>
        )
      case "ordering-system":
        return (
          <div>
            <OrderingSystem onLogout={handleLogout} />
            <div className="fixed bottom-4 right-4 space-x-2">
              <button
                onClick={handleOrderPlace}
                className="bg-purple-600 hover:bg-purple-700 text-white px-6 py-3 rounded-lg shadow-lg font-medium"
              >
                Complete Order
              </button>
            </div>
          </div>
        )
      case "order-tracking":
        return (
          <div>
            <OrderTracking orderId={currentOrder || undefined} onLogout={handleLogout} />
            <div className="fixed bottom-4 left-4 space-x-2">
              <button
                onClick={() => setCurrentView("restaurant-selection")}
                className="bg-gray-600 hover:bg-gray-700 text-white px-4 py-2 rounded-lg font-medium"
              >
                New Order
              </button>
              <button
                onClick={() => setCurrentView("order-history")}
                className="bg-purple-600 hover:bg-purple-700 text-white px-4 py-2 rounded-lg font-medium"
              >
                Order History
              </button>
            </div>
          </div>
        )
      case "order-history":
        return <OrderHistory onLogout={handleLogout} onNavigate={setCurrentView} />
      default:
        return <RestaurantSelection onLogout={handleLogout} />
    }
  }

  // Business workflow
  const renderBusinessFlow = () => {
    switch (currentView) {
      case "business-onboarding":
        return (
          <div>
            <BusinessOnboarding />
            <div className="fixed bottom-4 right-4">
              <button
                onClick={handleBusinessOnboardingComplete}
                className="bg-purple-600 hover:bg-purple-700 text-white px-6 py-3 rounded-lg shadow-lg font-medium"
              >
                Complete Setup
              </button>
            </div>
          </div>
        )
      case "business-dashboard":
      case "orders":
      case "menu":
      case "analytics":
      case "stock":
        return (
          <BusinessDashboard
            activeSection={currentView === "business-dashboard" ? "orders" : currentView}
            onNavItemClick={handleNavigation}
            onLogout={handleLogout}
          />
        )
      default:
        return <BusinessDashboard activeSection="orders" onNavItemClick={handleNavigation} onLogout={handleLogout} />
    }
  }

  if (!isAuthenticated) {
    return (
      <AuthInterface
        onLogin={handleLogin}
        onRegister={handleRegister}
        onSocialLogin={handleSocialLogin}
        onForgotPassword={handleForgotPassword}
      />
    )
  }

  return (
    <div className="min-h-screen bg-background">
      {userType === "business" && renderBusinessFlow()}
      {userType === "customer" && renderCustomerFlow()}
    </div>
  )
}