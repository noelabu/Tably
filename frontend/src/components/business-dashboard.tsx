"use client"

import React, { useState, useMemo } from "react"
import { motion } from "motion/react"
import { Bar, BarChart, Line, LineChart, ResponsiveContainer, XAxis, YAxis, Tooltip, PieChart, Pie, Cell } from "recharts"
import { 
  ShoppingBag, 
  Plus, 
  Edit, 
  Trash2, 
  TrendingUp, 
  TrendingDown, 
  DollarSign, 
  Users, 
  Package, 
  AlertTriangle, 
  Clock, 
  CheckCircle2, 
  XCircle, 
  MoreHorizontal,
  Calendar,
  Filter,
  Search,
  Bell,
  Settings,
  Menu as MenuIcon,
  BarChart3,
  FileText,
  Grid3x3,
  LogOut
} from "lucide-react"
import { Button } from "@/components/ui/button"
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card"
import { Badge } from "@/components/ui/badge"
import { Table, TableBody, TableCell, TableHead, TableHeader, TableRow } from "@/components/ui/table"
import { Dialog, DialogContent, DialogDescription, DialogHeader, DialogTitle, DialogTrigger } from "@/components/ui/dialog"
import { Form, FormControl, FormField, FormItem, FormLabel, FormMessage } from "@/components/ui/form"
import { Input } from "@/components/ui/input"
import { Textarea } from "@/components/ui/textarea"
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from "@/components/ui/select"
import { Separator } from "@/components/ui/separator"
import { ScrollArea } from "@/components/ui/scroll-area"
import { DropdownMenu, DropdownMenuContent, DropdownMenuItem, DropdownMenuTrigger } from "@/components/ui/dropdown-menu"
import { useForm } from "react-hook-form"
import { zodResolver } from "@hookform/resolvers/zod"
import * as z from "zod"

// Types
interface Order {
  id: string
  customerName: string
  customerEmail: string
  items: Array<{
    name: string
    quantity: number
    price: number
  }>
  total: number
  status: "pending" | "preparing" | "ready" | "completed" | "cancelled"
  orderTime: Date
}

interface MenuItem {
  id: string
  name: string
  description: string
  price: number
  category: string
  image: string
  available: boolean
  stock: number
  lowStockThreshold: number
}

interface AnalyticsData {
  revenue: Array<{ date: string; amount: number }>
  orders: Array<{ date: string; count: number }>
  topItems: Array<{ name: string; orders: number; revenue: number }>
  categoryBreakdown: Array<{ name: string; value: number; color: string }>
}

// Form schemas
const menuItemSchema = z.object({
  name: z.string().min(1, "Name is required"),
  description: z.string().min(1, "Description is required"),
  price: z.number().positive("Price must be positive"),
  category: z.string().min(1, "Category is required"),
  stock: z.number().int().min(0, "Stock must be non-negative"),
  lowStockThreshold: z.number().int().min(0, "Threshold must be non-negative")
})

type MenuItemFormData = z.infer<typeof menuItemSchema>

// Mock data
const mockOrders: Order[] = [
  {
    id: "1",
    customerName: "John Doe",
    customerEmail: "john@example.com",
    items: [
      { name: "Classic Burger", quantity: 2, price: 12.99 },
      { name: "Fries", quantity: 1, price: 4.99 }
    ],
    total: 30.97,
    status: "preparing",
    orderTime: new Date(Date.now() - 15 * 60 * 1000)
  },
  {
    id: "2",
    customerName: "Jane Smith",
    customerEmail: "jane@example.com",
    items: [
      { name: "Chicken Salad", quantity: 1, price: 14.99 },
      { name: "Iced Tea", quantity: 2, price: 2.99 }
    ],
    total: 20.97,
    status: "ready",
    orderTime: new Date(Date.now() - 45 * 60 * 1000)
  },
  {
    id: "3",
    customerName: "Mike Johnson",
    customerEmail: "mike@example.com",
    items: [
      { name: "Pizza Margherita", quantity: 1, price: 16.99 }
    ],
    total: 16.99,
    status: "pending",
    orderTime: new Date(Date.now() - 5 * 60 * 1000)
  }
]

const mockMenuItems: MenuItem[] = [
  {
    id: "1",
    name: "Classic Burger",
    description: "Juicy beef patty with lettuce, tomato, and our special sauce",
    price: 12.99,
    category: "Main Course",
    image: "/api/placeholder/300/200",
    available: true,
    stock: 25,
    lowStockThreshold: 10
  },
  {
    id: "2",
    name: "Chicken Salad",
    description: "Fresh mixed greens with grilled chicken and vinaigrette",
    price: 14.99,
    category: "Salads",
    image: "/api/placeholder/300/200",
    available: true,
    stock: 5,
    lowStockThreshold: 10
  },
  {
    id: "3",
    name: "Pizza Margherita",
    description: "Traditional pizza with tomato, mozzarella, and basil",
    price: 16.99,
    category: "Pizza",
    image: "/api/placeholder/300/200",
    available: false,
    stock: 0,
    lowStockThreshold: 5
  }
]

const mockAnalytics: AnalyticsData = {
  revenue: [
    { date: "Mon", amount: 1200 },
    { date: "Tue", amount: 1500 },
    { date: "Wed", amount: 1100 },
    { date: "Thu", amount: 1800 },
    { date: "Fri", amount: 2200 },
    { date: "Sat", amount: 2800 },
    { date: "Sun", amount: 2400 }
  ],
  orders: [
    { date: "Mon", count: 45 },
    { date: "Tue", count: 52 },
    { date: "Wed", count: 38 },
    { date: "Thu", count: 61 },
    { date: "Fri", count: 74 },
    { date: "Sat", count: 89 },
    { date: "Sun", count: 76 }
  ],
  topItems: [
    { name: "Classic Burger", orders: 156, revenue: 2025.44 },
    { name: "Pizza Margherita", orders: 123, revenue: 2089.77 },
    { name: "Chicken Salad", orders: 98, revenue: 1469.02 }
  ],
  categoryBreakdown: [
    { name: "Main Course", value: 45, color: "#8b5cf6" },
    { name: "Pizza", value: 30, color: "#a855f7" },
    { name: "Salads", value: 15, color: "#c084fc" },
    { name: "Drinks", value: 10, color: "#d8b4fe" }
  ]
}

// Utility functions
const formatTime = (date: Date) => {
  const now = new Date()
  const diffMs = now.getTime() - date.getTime()
  const diffMins = Math.floor(diffMs / (1000 * 60))
  
  if (diffMins < 60) {
    return `${diffMins}m ago`
  } else {
    const diffHours = Math.floor(diffMins / 60)
    return `${diffHours}h ago`
  }
}

const getStatusColor = (status: Order["status"]) => {
  switch (status) {
    case "pending": return "bg-yellow-100 text-yellow-800"
    case "preparing": return "bg-blue-100 text-blue-800"
    case "ready": return "bg-green-100 text-green-800"
    case "completed": return "bg-gray-100 text-gray-800"
    case "cancelled": return "bg-red-100 text-red-800"
    default: return "bg-gray-100 text-gray-800"
  }
}

const getStatusIcon = (status: Order["status"]) => {
  switch (status) {
    case "pending": return <Clock className="h-4 w-4" />
    case "preparing": return <Package className="h-4 w-4" />
    case "ready": return <CheckCircle2 className="h-4 w-4" />
    case "completed": return <CheckCircle2 className="h-4 w-4" />
    case "cancelled": return <XCircle className="h-4 w-4" />
    default: return <Clock className="h-4 w-4" />
  }
}

interface BusinessDashboardProps {
  onNavItemClick?: (section: string) => void
  activeSection?: string
  onLogout?: () => void
}

export default function BusinessDashboard({ onNavItemClick, activeSection = "orders", onLogout }: BusinessDashboardProps) {
  const [currentSection, setCurrentSection] = useState(activeSection)
  const [orders, setOrders] = useState<Order[]>(mockOrders)
  const [menuItems, setMenuItems] = useState<MenuItem[]>(mockMenuItems)
  const [sidebarCollapsed, setSidebarCollapsed] = useState(false)
  const [isMenuItemDialogOpen, setIsMenuItemDialogOpen] = useState(false)
  const [editingMenuItem, setEditingMenuItem] = useState<MenuItem | null>(null)

  const form = useForm<MenuItemFormData>({
    resolver: zodResolver(menuItemSchema),
    defaultValues: {
      name: "",
      description: "",
      price: 0,
      category: "",
      stock: 0,
      lowStockThreshold: 5
    }
  })

  const handleNavigation = (section: string) => {
    setCurrentSection(section)
    onNavItemClick?.(section)
  }

  const updateOrderStatus = (orderId: string, newStatus: Order["status"]) => {
    setOrders(prev => prev.map(order => 
      order.id === orderId ? { ...order, status: newStatus } : order
    ))
  }

  const onSubmitMenuItem = (data: MenuItemFormData) => {
    if (editingMenuItem) {
      // Update existing item
      setMenuItems(prev => prev.map(item => 
        item.id === editingMenuItem.id 
          ? { ...item, ...data, available: data.stock > 0 }
          : item
      ))
    } else {
      // Add new item
      const newItem: MenuItem = {
        ...data,
        id: Date.now().toString(),
        image: "/api/placeholder/300/200",
        available: data.stock > 0
      }
      setMenuItems(prev => [...prev, newItem])
    }
    setIsMenuItemDialogOpen(false)
    setEditingMenuItem(null)
    form.reset()
  }

  const openEditDialog = (item: MenuItem) => {
    setEditingMenuItem(item)
    form.reset({
      name: item.name,
      description: item.description,
      price: item.price,
      category: item.category,
      stock: item.stock,
      lowStockThreshold: item.lowStockThreshold
    })
    setIsMenuItemDialogOpen(true)
  }

  const deleteMenuItem = (itemId: string) => {
    setMenuItems(prev => prev.filter(item => item.id !== itemId))
  }

  // Calculate metrics
  const totalRevenue = useMemo(() => mockAnalytics.revenue.reduce((sum, day) => sum + day.amount, 0), [])
  const totalOrders = useMemo(() => orders.length, [orders])
  const pendingOrders = useMemo(() => orders.filter(order => order.status === "pending").length, [orders])
  const lowStockItems = useMemo(() => menuItems.filter(item => item.stock <= item.lowStockThreshold).length, [menuItems])

  const sidebarItems = [
    { id: "orders", label: "Orders", icon: ShoppingBag, badge: pendingOrders },
    { id: "menu", label: "Menu", icon: Grid3x3 },
    { id: "analytics", label: "Analytics", icon: BarChart3 },
    { id: "stock", label: "Stock", icon: Package, badge: lowStockItems }
  ]

  return (
    <div className="flex h-screen bg-background">
      {/* Sidebar */}
      <motion.div
        initial={false}
        animate={{ width: sidebarCollapsed ? 80 : 280 }}
        className="border-r bg-card flex flex-col"
      >
        <div className="p-6 border-b">
          <div className="flex items-center gap-3">
            <Button
              variant="ghost"
              size="sm"
              onClick={() => setSidebarCollapsed(!sidebarCollapsed)}
              className="p-1 h-8 w-8"
            >
              <MenuIcon className="h-4 w-4" />
            </Button>
            {!sidebarCollapsed && (
              <div>
                <h1 className="font-semibold text-lg">Restaurant Dashboard</h1>
                <p className="text-sm text-muted-foreground">Manage your business</p>
              </div>
            )}
          </div>
        </div>

        <nav className="flex-1 p-4">
          <div className="space-y-2">
            {sidebarItems.map((item) => (
              <Button
                key={item.id}
                variant={currentSection === item.id ? "default" : "ghost"}
                className={`w-full justify-start gap-3 ${sidebarCollapsed ? 'px-2' : ''}`}
                onClick={() => handleNavigation(item.id)}
              >
                <item.icon className="h-5 w-5" />
                {!sidebarCollapsed && (
                  <>
                    <span>{item.label}</span>
                    {item.badge !== undefined && item.badge > 0 && (
                      <Badge variant="secondary" className="ml-auto">
                        {item.badge}
                      </Badge>
                    )}
                  </>
                )}
              </Button>
            ))}
          </div>
        </nav>

        <div className="p-4 border-t space-y-2">
          <Button
            variant="ghost"
            size="sm"
            className={`w-full gap-2 ${sidebarCollapsed ? 'px-2' : 'justify-start'}`}
          >
            <Settings className="h-4 w-4" />
            {!sidebarCollapsed && "Settings"}
          </Button>
          <Button
            variant="ghost"
            size="sm"
            className={`w-full gap-2 ${sidebarCollapsed ? 'px-2' : 'justify-start'} text-red-600 hover:text-red-700 hover:bg-red-50`}
            onClick={onLogout}
          >
            <LogOut className="h-4 w-4" />
            {!sidebarCollapsed && "Logout"}
          </Button>
        </div>
      </motion.div>

      {/* Main Content */}
      <div className="flex-1 flex flex-col overflow-hidden">
        {/* Header */}
        <header className="border-b bg-card px-6 py-4">
          <div className="flex items-center justify-between">
            <div>
              <h2 className="text-2xl font-semibold capitalize">{currentSection}</h2>
              <p className="text-muted-foreground">
                {currentSection === "orders" && "Manage incoming orders and track status"}
                {currentSection === "menu" && "Edit your menu items and categories"}
                {currentSection === "analytics" && "View your business performance"}
                {currentSection === "stock" && "Monitor inventory levels and alerts"}
              </p>
            </div>
            <div className="flex items-center gap-2">
              <Button variant="outline" size="sm">
                <Filter className="h-4 w-4 mr-2" />
                Filter
              </Button>
              <Button variant="outline" size="sm">
                <Bell className="h-4 w-4" />
              </Button>
            </div>
          </div>
        </header>

        {/* Content Area */}
        <main className="flex-1 overflow-auto">
          <div className="p-6">
            {currentSection === "orders" && (
              <div className="space-y-6">
                {/* Quick Stats */}
                <div className="grid grid-cols-1 md:grid-cols-4 gap-4">
                  <Card>
                    <CardContent className="p-6">
                      <div className="flex items-center gap-4">
                        <div className="p-2 bg-primary/10 rounded-lg">
                          <ShoppingBag className="h-5 w-5 text-primary" />
                        </div>
                        <div>
                          <p className="text-sm text-muted-foreground">Total Orders</p>
                          <p className="text-xl font-semibold">{totalOrders}</p>
                        </div>
                      </div>
                    </CardContent>
                  </Card>
                  <Card>
                    <CardContent className="p-6">
                      <div className="flex items-center gap-4">
                        <div className="p-2 bg-yellow-500/10 rounded-lg">
                          <Clock className="h-5 w-5 text-yellow-600" />
                        </div>
                        <div>
                          <p className="text-sm text-muted-foreground">Pending</p>
                          <p className="text-xl font-semibold">{pendingOrders}</p>
                        </div>
                      </div>
                    </CardContent>
                  </Card>
                  <Card>
                    <CardContent className="p-6">
                      <div className="flex items-center gap-4">
                        <div className="p-2 bg-primary/10 rounded-lg">
                          <DollarSign className="h-5 w-5 text-primary" />
                        </div>
                        <div>
                          <p className="text-sm text-muted-foreground">Today's Revenue</p>
                          <p className="text-xl font-semibold">${totalRevenue.toFixed(2)}</p>
                        </div>
                      </div>
                    </CardContent>
                  </Card>
                  <Card>
                    <CardContent className="p-6">
                      <div className="flex items-center gap-4">
                        <div className="p-2 bg-primary/10 rounded-lg">
                          <TrendingUp className="h-5 w-5 text-primary" />
                        </div>
                        <div>
                          <p className="text-sm text-muted-foreground">Avg. Order</p>
                          <p className="text-xl font-semibold">
                            ${totalOrders > 0 ? (orders.reduce((sum, order) => sum + order.total, 0) / totalOrders).toFixed(2) : '0.00'}
                          </p>
                        </div>
                      </div>
                    </CardContent>
                  </Card>
                </div>

                {/* Orders Grid */}
                <div className="grid grid-cols-1 lg:grid-cols-2 xl:grid-cols-3 gap-6">
                  {orders.map((order) => (
                    <Card key={order.id} className="bg-card">
                      <CardHeader className="pb-3">
                        <div className="flex items-center justify-between">
                          <div>
                            <CardTitle className="text-lg">Order #{order.id}</CardTitle>
                            <CardDescription>{order.customerName} • {order.customerEmail}</CardDescription>
                          </div>
                          <div className="text-right">
                            <p className="font-semibold">${order.total.toFixed(2)}</p>
                            <p className="text-sm text-muted-foreground">{formatTime(order.orderTime)}</p>
                          </div>
                        </div>
                      </CardHeader>
                      <CardContent className="space-y-4">
                        <div className="space-y-2">
                          {order.items.map((item, index) => (
                            <div key={index} className="flex justify-between text-sm">
                              <span>{item.quantity}x {item.name}</span>
                              <span>${(item.quantity * item.price).toFixed(2)}</span>
                            </div>
                          ))}
                        </div>
                        <Separator />
                        <div className="flex items-center justify-between">
                          <Badge className={getStatusColor(order.status)}>
                            <span className="flex items-center gap-1">
                              {getStatusIcon(order.status)}
                              {order.status.charAt(0).toUpperCase() + order.status.slice(1)}
                            </span>
                          </Badge>
                          <DropdownMenu>
                            <DropdownMenuTrigger asChild>
                              <Button variant="ghost" size="sm">
                                <MoreHorizontal className="h-4 w-4" />
                              </Button>
                            </DropdownMenuTrigger>
                            <DropdownMenuContent align="end">
                              {order.status === "pending" && (
                                <DropdownMenuItem onClick={() => updateOrderStatus(order.id, "preparing")}>
                                  Start Preparing
                                </DropdownMenuItem>
                              )}
                              {order.status === "preparing" && (
                                <DropdownMenuItem onClick={() => updateOrderStatus(order.id, "ready")}>
                                  Mark Ready
                                </DropdownMenuItem>
                              )}
                              {order.status === "ready" && (
                                <DropdownMenuItem onClick={() => updateOrderStatus(order.id, "completed")}>
                                  Mark Completed
                                </DropdownMenuItem>
                              )}
                              <DropdownMenuItem 
                                onClick={() => updateOrderStatus(order.id, "cancelled")}
                                className="text-red-600"
                              >
                                Cancel Order
                              </DropdownMenuItem>
                            </DropdownMenuContent>
                          </DropdownMenu>
                        </div>
                      </CardContent>
                    </Card>
                  ))}
                </div>
              </div>
            )}

            {currentSection === "menu" && (
              <div className="space-y-6">
                <div className="flex justify-between items-center">
                  <div className="flex items-center gap-4">
                    <div className="relative">
                      <Search className="absolute left-3 top-1/2 transform -translate-y-1/2 h-4 w-4 text-muted-foreground" />
                      <Input placeholder="Search menu items..." className="pl-9 w-80" />
                    </div>
                    <Select defaultValue="all">
                      <SelectTrigger className="w-48">
                        <SelectValue placeholder="Category" />
                      </SelectTrigger>
                      <SelectContent>
                        <SelectItem value="all">All Categories</SelectItem>
                        <SelectItem value="main">Main Course</SelectItem>
                        <SelectItem value="pizza">Pizza</SelectItem>
                        <SelectItem value="salads">Salads</SelectItem>
                      </SelectContent>
                    </Select>
                  </div>
                  <Dialog open={isMenuItemDialogOpen} onOpenChange={setIsMenuItemDialogOpen}>
                    <DialogTrigger asChild>
                      <Button onClick={() => {
                        setEditingMenuItem(null)
                        form.reset()
                      }}>
                        <Plus className="h-4 w-4 mr-2" />
                        Add Item
                      </Button>
                    </DialogTrigger>
                    <DialogContent className="max-w-2xl">
                      <DialogHeader>
                        <DialogTitle>{editingMenuItem ? "Edit Menu Item" : "Add New Menu Item"}</DialogTitle>
                        <DialogDescription>
                          {editingMenuItem ? "Update the details of this menu item." : "Create a new menu item for your restaurant."}
                        </DialogDescription>
                      </DialogHeader>
                      <Form {...form}>
                        <form onSubmit={form.handleSubmit(onSubmitMenuItem)} className="space-y-4">
                          <div className="grid grid-cols-2 gap-4">
                            <FormField
                              control={form.control}
                              name="name"
                              render={({ field }) => (
                                <FormItem>
                                  <FormLabel>Name</FormLabel>
                                  <FormControl>
                                    <Input placeholder="Item name" {...field} />
                                  </FormControl>
                                  <FormMessage />
                                </FormItem>
                              )}
                            />
                            <FormField
                              control={form.control}
                              name="price"
                              render={({ field }) => (
                                <FormItem>
                                  <FormLabel>Price ($)</FormLabel>
                                  <FormControl>
                                    <Input 
                                      type="number" 
                                      step="0.01" 
                                      placeholder="0.00" 
                                      {...field}
                                      onChange={(e) => field.onChange(parseFloat(e.target.value) || 0)}
                                    />
                                  </FormControl>
                                  <FormMessage />
                                </FormItem>
                              )}
                            />
                          </div>
                          <FormField
                            control={form.control}
                            name="description"
                            render={({ field }) => (
                              <FormItem>
                                <FormLabel>Description</FormLabel>
                                <FormControl>
                                  <Textarea placeholder="Item description" {...field} />
                                </FormControl>
                                <FormMessage />
                              </FormItem>
                            )}
                          />
                          <div className="grid grid-cols-3 gap-4">
                            <FormField
                              control={form.control}
                              name="category"
                              render={({ field }) => (
                                <FormItem>
                                  <FormLabel>Category</FormLabel>
                                  <Select onValueChange={field.onChange} value={field.value}>
                                    <FormControl>
                                      <SelectTrigger>
                                        <SelectValue placeholder="Select category" />
                                      </SelectTrigger>
                                    </FormControl>
                                    <SelectContent>
                                      <SelectItem value="Main Course">Main Course</SelectItem>
                                      <SelectItem value="Pizza">Pizza</SelectItem>
                                      <SelectItem value="Salads">Salads</SelectItem>
                                      <SelectItem value="Drinks">Drinks</SelectItem>
                                    </SelectContent>
                                  </Select>
                                  <FormMessage />
                                </FormItem>
                              )}
                            />
                            <FormField
                              control={form.control}
                              name="stock"
                              render={({ field }) => (
                                <FormItem>
                                  <FormLabel>Stock</FormLabel>
                                  <FormControl>
                                    <Input 
                                      type="number" 
                                      placeholder="0" 
                                      {...field}
                                      onChange={(e) => field.onChange(parseInt(e.target.value) || 0)}
                                    />
                                  </FormControl>
                                  <FormMessage />
                                </FormItem>
                              )}
                            />
                            <FormField
                              control={form.control}
                              name="lowStockThreshold"
                              render={({ field }) => (
                                <FormItem>
                                  <FormLabel>Low Stock Alert</FormLabel>
                                  <FormControl>
                                    <Input 
                                      type="number" 
                                      placeholder="5" 
                                      {...field}
                                      onChange={(e) => field.onChange(parseInt(e.target.value) || 0)}
                                    />
                                  </FormControl>
                                  <FormMessage />
                                </FormItem>
                              )}
                            />
                          </div>
                          <div className="flex justify-end gap-2 pt-4">
                            <Button type="button" variant="outline" onClick={() => setIsMenuItemDialogOpen(false)}>
                              Cancel
                            </Button>
                            <Button type="submit">
                              {editingMenuItem ? "Update Item" : "Add Item"}
                            </Button>
                          </div>
                        </form>
                      </Form>
                    </DialogContent>
                  </Dialog>
                </div>

                <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
                  {menuItems.map((item) => (
                    <Card key={item.id} className="bg-card">
                      <div className="aspect-video bg-muted rounded-t-lg relative overflow-hidden">
                        <div className="absolute inset-0 bg-gradient-to-br from-primary/20 to-transparent" />
                        <div className="absolute top-2 right-2">
                          {!item.available && (
                            <Badge variant="secondary" className="bg-red-100 text-red-800">
                              Unavailable
                            </Badge>
                          )}
                          {item.stock <= item.lowStockThreshold && item.available && (
                            <Badge variant="secondary" className="bg-yellow-100 text-yellow-800">
                              Low Stock
                            </Badge>
                          )}
                        </div>
                      </div>
                      <CardHeader>
                        <div className="flex justify-between items-start">
                          <div>
                            <CardTitle className="text-lg">{item.name}</CardTitle>
                            <CardDescription className="text-sm">{item.category}</CardDescription>
                          </div>
                          <p className="text-xl font-semibold">${item.price.toFixed(2)}</p>
                        </div>
                      </CardHeader>
                      <CardContent className="space-y-4">
                        <p className="text-sm text-muted-foreground">{item.description}</p>
                        <div className="flex justify-between text-sm">
                          <span>Stock: {item.stock}</span>
                          <span>Alert at: {item.lowStockThreshold}</span>
                        </div>
                        <div className="flex gap-2">
                          <Button variant="outline" size="sm" onClick={() => openEditDialog(item)}>
                            <Edit className="h-4 w-4 mr-1" />
                            Edit
                          </Button>
                          <Button 
                            variant="outline" 
                            size="sm" 
                            onClick={() => deleteMenuItem(item.id)}
                            className="text-red-600 hover:text-red-700"
                          >
                            <Trash2 className="h-4 w-4 mr-1" />
                            Delete
                          </Button>
                        </div>
                      </CardContent>
                    </Card>
                  ))}
                </div>
              </div>
            )}

            {currentSection === "analytics" && (
              <div className="space-y-6">
                {/* Key Metrics */}
                <div className="grid grid-cols-1 md:grid-cols-4 gap-4">
                  <Card>
                    <CardContent className="p-6">
                      <div className="flex items-center gap-4">
                        <div className="p-2 bg-primary/10 rounded-lg">
                          <DollarSign className="h-5 w-5 text-primary" />
                        </div>
                        <div>
                          <p className="text-sm text-muted-foreground">Weekly Revenue</p>
                          <p className="text-2xl font-bold">${totalRevenue.toFixed(2)}</p>
                          <div className="flex items-center text-sm">
                            <TrendingUp className="h-3 w-3 text-green-600 mr-1" />
                            <span className="text-green-600">+12.5%</span>
                          </div>
                        </div>
                      </div>
                    </CardContent>
                  </Card>
                  <Card>
                    <CardContent className="p-6">
                      <div className="flex items-center gap-4">
                        <div className="p-2 bg-blue-500/10 rounded-lg">
                          <ShoppingBag className="h-5 w-5 text-blue-600" />
                        </div>
                        <div>
                          <p className="text-sm text-muted-foreground">Total Orders</p>
                          <p className="text-2xl font-bold">435</p>
                          <div className="flex items-center text-sm">
                            <TrendingUp className="h-3 w-3 text-green-600 mr-1" />
                            <span className="text-green-600">+8.2%</span>
                          </div>
                        </div>
                      </div>
                    </CardContent>
                  </Card>
                  <Card>
                    <CardContent className="p-6">
                      <div className="flex items-center gap-4">
                        <div className="p-2 bg-orange-500/10 rounded-lg">
                          <Users className="h-5 w-5 text-orange-600" />
                        </div>
                        <div>
                          <p className="text-sm text-muted-foreground">Customers</p>
                          <p className="text-2xl font-bold">256</p>
                          <div className="flex items-center text-sm">
                            <TrendingUp className="h-3 w-3 text-green-600 mr-1" />
                            <span className="text-green-600">+15.3%</span>
                          </div>
                        </div>
                      </div>
                    </CardContent>
                  </Card>
                  <Card>
                    <CardContent className="p-6">
                      <div className="flex items-center gap-4">
                        <div className="p-2 bg-purple-500/10 rounded-lg">
                          <TrendingUp className="h-5 w-5 text-purple-600" />
                        </div>
                        <div>
                          <p className="text-sm text-muted-foreground">Avg Order Value</p>
                          <p className="text-2xl font-bold">$28.45</p>
                          <div className="flex items-center text-sm">
                            <TrendingDown className="h-3 w-3 text-red-600 mr-1" />
                            <span className="text-red-600">-2.1%</span>
                          </div>
                        </div>
                      </div>
                    </CardContent>
                  </Card>
                </div>

                {/* Charts */}
                <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
                  <Card>
                    <CardHeader>
                      <CardTitle>Weekly Revenue</CardTitle>
                      <CardDescription>Revenue trends over the past week</CardDescription>
                    </CardHeader>
                    <CardContent>
                      <ResponsiveContainer width="100%" height={300}>
                        <BarChart data={mockAnalytics.revenue}>
                          <XAxis dataKey="date" />
                          <YAxis />
                          <Tooltip formatter={(value) => [`$${value}`, "Revenue"]} />
                          <Bar dataKey="amount" fill="#8b5cf6" radius={[4, 4, 0, 0]} />
                        </BarChart>
                      </ResponsiveContainer>
                    </CardContent>
                  </Card>

                  <Card>
                    <CardHeader>
                      <CardTitle>Daily Orders</CardTitle>
                      <CardDescription>Order volume trends over the past week</CardDescription>
                    </CardHeader>
                    <CardContent>
                      <ResponsiveContainer width="100%" height={300}>
                        <LineChart data={mockAnalytics.orders}>
                          <XAxis dataKey="date" />
                          <YAxis />
                          <Tooltip formatter={(value) => [`${value}`, "Orders"]} />
                          <Line 
                            type="monotone" 
                            dataKey="count" 
                            stroke="#8b5cf6" 
                            strokeWidth={3}
                            dot={{ fill: "#8b5cf6", strokeWidth: 2, r: 4 }}
                          />
                        </LineChart>
                      </ResponsiveContainer>
                    </CardContent>
                  </Card>
                </div>

                {/* Additional Analytics */}
                <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
                  <Card>
                    <CardHeader>
                      <CardTitle>Top Selling Items</CardTitle>
                      <CardDescription>Best performing menu items this week</CardDescription>
                    </CardHeader>
                    <CardContent>
                      <div className="space-y-4">
                        {mockAnalytics.topItems.map((item, index) => (
                          <div key={index} className="flex items-center justify-between">
                            <div>
                              <p className="font-medium">{item.name}</p>
                              <p className="text-sm text-muted-foreground">{item.orders} orders</p>
                            </div>
                            <p className="font-semibold">${item.revenue.toFixed(2)}</p>
                          </div>
                        ))}
                      </div>
                    </CardContent>
                  </Card>

                  <Card>
                    <CardHeader>
                      <CardTitle>Category Breakdown</CardTitle>
                      <CardDescription>Sales distribution by category</CardDescription>
                    </CardHeader>
                    <CardContent>
                      <ResponsiveContainer width="100%" height={250}>
                        <PieChart>
                          <Pie
                            data={mockAnalytics.categoryBreakdown}
                            cx="50%"
                            cy="50%"
                            innerRadius={60}
                            outerRadius={100}
                            paddingAngle={5}
                            dataKey="value"
                          >
                            {mockAnalytics.categoryBreakdown.map((entry, index) => (
                              <Cell key={`cell-${index}`} fill={entry.color} />
                            ))}
                          </Pie>
                          <Tooltip formatter={(value) => [`${value}%`, "Share"]} />
                        </PieChart>
                      </ResponsiveContainer>
                      <div className="grid grid-cols-2 gap-2 mt-4">
                        {mockAnalytics.categoryBreakdown.map((item, index) => (
                          <div key={index} className="flex items-center gap-2">
                            <div 
                              className="w-3 h-3 rounded-full" 
                              style={{ backgroundColor: item.color }}
                            />
                            <span className="text-sm">{item.name}</span>
                          </div>
                        ))}
                      </div>
                    </CardContent>
                  </Card>
                </div>
              </div>
            )}

            {currentSection === "stock" && (
              <div className="space-y-6">
                {/* Stock Overview */}
                <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
                  <Card>
                    <CardContent className="p-6">
                      <div className="flex items-center gap-4">
                        <div className="p-2 bg-red-500/10 rounded-lg">
                          <AlertTriangle className="h-5 w-5 text-red-600" />
                        </div>
                        <div>
                          <p className="text-sm text-muted-foreground">Low Stock Items</p>
                          <p className="text-2xl font-bold">{lowStockItems}</p>
                        </div>
                      </div>
                    </CardContent>
                  </Card>
                  <Card>
                    <CardContent className="p-6">
                      <div className="flex items-center gap-4">
                        <div className="p-2 bg-gray-500/10 rounded-lg">
                          <Package className="h-5 w-5 text-gray-600" />
                        </div>
                        <div>
                          <p className="text-sm text-muted-foreground">Out of Stock</p>
                          <p className="text-2xl font-bold">{menuItems.filter(item => item.stock === 0).length}</p>
                        </div>
                      </div>
                    </CardContent>
                  </Card>
                  <Card>
                    <CardContent className="p-6">
                      <div className="flex items-center gap-4">
                        <div className="p-2 bg-primary/10 rounded-lg">
                          <CheckCircle2 className="h-5 w-5 text-primary" />
                        </div>
                        <div>
                          <p className="text-sm text-muted-foreground">Well Stocked</p>
                          <p className="text-2xl font-bold">{menuItems.filter(item => item.stock > item.lowStockThreshold).length}</p>
                        </div>
                      </div>
                    </CardContent>
                  </Card>
                </div>

                {/* Stock Table */}
                <Card>
                  <CardHeader>
                    <CardTitle>Inventory Management</CardTitle>
                    <CardDescription>Monitor stock levels and update inventory</CardDescription>
                  </CardHeader>
                  <CardContent>
                    <Table>
                      <TableHeader>
                        <TableRow>
                          <TableHead>Item Name</TableHead>
                          <TableHead>Category</TableHead>
                          <TableHead>Current Stock</TableHead>
                          <TableHead>Low Stock Alert</TableHead>
                          <TableHead>Status</TableHead>
                          <TableHead>Actions</TableHead>
                        </TableRow>
                      </TableHeader>
                      <TableBody>
                        {menuItems.map((item) => (
                          <TableRow key={item.id}>
                            <TableCell className="font-medium">{item.name}</TableCell>
                            <TableCell>{item.category}</TableCell>
                            <TableCell>{item.stock}</TableCell>
                            <TableCell>{item.lowStockThreshold}</TableCell>
                            <TableCell>
                              {item.stock === 0 ? (
                                <Badge variant="secondary" className="bg-red-100 text-red-800">
                                  Out of Stock
                                </Badge>
                              ) : item.stock <= item.lowStockThreshold ? (
                                <Badge variant="secondary" className="bg-yellow-100 text-yellow-800">
                                  Low Stock
                                </Badge>
                              ) : (
                                <Badge className="bg-green-100 text-green-800">
                                  In Stock
                                </Badge>
                              )}
                            </TableCell>
                            <TableCell>
                              <div className="flex gap-2">
                                <Button variant="outline" size="sm" onClick={() => openEditDialog(item)}>
                                  <Edit className="h-4 w-4" />
                                </Button>
                                <Button
                                  variant="outline"
                                  size="sm"
                                  onClick={() => {
                                    setMenuItems(prev => prev.map(menuItem => 
                                      menuItem.id === item.id 
                                        ? { ...menuItem, stock: menuItem.stock + 10 }
                                        : menuItem
                                    ))
                                  }}
                                >
                                  <Plus className="h-4 w-4 mr-1" />
                                  Restock
                                </Button>
                              </div>
                            </TableCell>
                          </TableRow>
                        ))}
                      </TableBody>
                    </Table>
                  </CardContent>
                </Card>
              </div>
            )}
          </div>
        </main>
      </div>
    </div>
  )
}