"use client";

import { useState, useMemo } from 'react';
import { Card, CardContent, CardHeader } from '@/components/ui/card';
import { Button } from '@/components/ui/button';
import { Badge } from '@/components/ui/badge';
import { Input } from '@/components/ui/input';
import { 
  Search, 
  Filter, 
  ChevronDown, 
  ChevronUp, 
  Star, 
  RotateCcw, 
  Receipt, 
  Calendar, 
  MapPin, 
  CreditCard,
  LogOut,
  Download,
  Clock,
  DollarSign,
  TrendingUp,
  User
} from 'lucide-react';

interface OrderItem {
  id: string;
  name: string;
  quantity: number;
  price: number;
  customizations?: string[];
}

interface Order {
  id: string;
  restaurantName: string;
  restaurantLogo: string;
  date: string;
  time: string;
  status: 'Completed' | 'Cancelled';
  total: number;
  items: OrderItem[];
  deliveryAddress: string;
  paymentMethod: string;
  rating?: number;
  cuisine: string;
}

interface OrderHistoryProps {
  onLogout: () => void;
  onNavigate?: (view: string) => void;
}

const mockOrders: Order[] = [
  {
    id: 'ORD-2024-001',
    restaurantName: 'Mario\'s Pizzeria',
    restaurantLogo: '🍕',
    date: '2024-02-15',
    time: '7:30 PM',
    status: 'Completed',
    total: 42.50,
    items: [
      { id: '1', name: 'Margherita Pizza (Large)', quantity: 1, price: 18.99 },
      { id: '2', name: 'Caesar Salad', quantity: 1, price: 12.99 },
      { id: '3', name: 'Garlic Bread', quantity: 2, price: 5.26 }
    ],
    deliveryAddress: '123 Oak Street, Apt 2B',
    paymentMethod: 'Credit Card ending in 4567',
    rating: 5,
    cuisine: 'Italian'
  },
  {
    id: 'ORD-2024-002',
    restaurantName: 'Dragon Palace',
    restaurantLogo: '🥡',
    date: '2024-02-12',
    time: '6:45 PM',
    status: 'Completed',
    total: 58.75,
    items: [
      { id: '1', name: 'Sweet & Sour Pork', quantity: 1, price: 16.99 },
      { id: '2', name: 'Kung Pao Chicken', quantity: 1, price: 15.99 },
      { id: '3', name: 'Fried Rice', quantity: 2, price: 12.98 },
      { id: '4', name: 'Spring Rolls', quantity: 1, price: 8.99 }
    ],
    deliveryAddress: '123 Oak Street, Apt 2B',
    paymentMethod: 'PayPal',
    rating: 4,
    cuisine: 'Chinese'
  },
  {
    id: 'ORD-2024-003',
    restaurantName: 'Spice Garden',
    restaurantLogo: '🍛',
    date: '2024-02-08',
    time: '8:15 PM',
    status: 'Completed',
    total: 34.25,
    items: [
      { id: '1', name: 'Chicken Tikka Masala', quantity: 1, price: 17.99 },
      { id: '2', name: 'Basmati Rice', quantity: 1, price: 4.99 },
      { id: '3', name: 'Naan Bread', quantity: 2, price: 7.98 }
    ],
    deliveryAddress: '123 Oak Street, Apt 2B',
    paymentMethod: 'Credit Card ending in 4567',
    rating: 5,
    cuisine: 'Indian'
  },
  {
    id: 'ORD-2024-004',
    restaurantName: 'Taco Libre',
    restaurantLogo: '🌮',
    date: '2024-02-05',
    time: '1:20 PM',
    status: 'Cancelled',
    total: 28.50,
    items: [
      { id: '1', name: 'Fish Tacos', quantity: 3, price: 15.99 },
      { id: '2', name: 'Guacamole & Chips', quantity: 1, price: 8.99 }
    ],
    deliveryAddress: '123 Oak Street, Apt 2B',
    paymentMethod: 'Credit Card ending in 4567',
    cuisine: 'Mexican'
  },
  {
    id: 'ORD-2024-005',
    restaurantName: 'Burger Junction',
    restaurantLogo: '🍔',
    date: '2024-01-30',
    time: '12:45 PM',
    status: 'Completed',
    total: 24.75,
    items: [
      { id: '1', name: 'Double Cheeseburger', quantity: 1, price: 13.99 },
      { id: '2', name: 'French Fries', quantity: 1, price: 4.99 },
      { id: '3', name: 'Chocolate Milkshake', quantity: 1, price: 5.77 }
    ],
    deliveryAddress: '123 Oak Street, Apt 2B',
    paymentMethod: 'Apple Pay',
    rating: 3,
    cuisine: 'American'
  },
  {
    id: 'ORD-2024-006',
    restaurantName: 'Sakura Sushi',
    restaurantLogo: '🍣',
    date: '2024-01-25',
    time: '7:00 PM',
    status: 'Completed',
    total: 67.80,
    items: [
      { id: '1', name: 'Salmon Sashimi (8 pcs)', quantity: 1, price: 22.99 },
      { id: '2', name: 'California Roll', quantity: 2, price: 24.98 },
      { id: '3', name: 'Miso Soup', quantity: 2, price: 7.98 },
      { id: '4', name: 'Edamame', quantity: 1, price: 5.99 }
    ],
    deliveryAddress: '123 Oak Street, Apt 2B',
    paymentMethod: 'Credit Card ending in 4567',
    rating: 5,
    cuisine: 'Japanese'
  },
  {
    id: 'ORD-2024-007',
    restaurantName: 'Mediterranean Delight',
    restaurantLogo: '🥙',
    date: '2024-01-20',
    time: '6:30 PM',
    status: 'Completed',
    total: 39.60,
    items: [
      { id: '1', name: 'Chicken Shawarma Plate', quantity: 1, price: 16.99 },
      { id: '2', name: 'Hummus with Pita', quantity: 1, price: 8.99 },
      { id: '3', name: 'Greek Salad', quantity: 1, price: 10.99 }
    ],
    deliveryAddress: '123 Oak Street, Apt 2B',
    paymentMethod: 'Debit Card',
    rating: 4,
    cuisine: 'Mediterranean'
  },
  {
    id: 'ORD-2024-008',
    restaurantName: 'Thai Basil',
    restaurantLogo: '🍜',
    date: '2024-01-15',
    time: '8:45 PM',
    status: 'Completed',
    total: 45.30,
    items: [
      { id: '1', name: 'Pad Thai', quantity: 1, price: 14.99 },
      { id: '2', name: 'Green Curry with Rice', quantity: 1, price: 16.99 },
      { id: '3', name: 'Tom Yum Soup', quantity: 1, price: 9.99 }
    ],
    deliveryAddress: '123 Oak Street, Apt 2B',
    paymentMethod: 'Credit Card ending in 4567',
    rating: 4,
    cuisine: 'Thai'
  }
];

export const OrderHistory = ({ onLogout, onNavigate }: OrderHistoryProps) => {
  const [activeTab, setActiveTab] = useState('Order History');
  const [searchQuery, setSearchQuery] = useState('');
  const [dateFilter, setDateFilter] = useState('All Time');
  const [statusFilter, setStatusFilter] = useState('All');
  const [expandedOrders, setExpandedOrders] = useState<Set<string>>(new Set());
  const [showFilters, setShowFilters] = useState(false);

  const filteredOrders = useMemo(() => {
    return mockOrders.filter(order => {
      const matchesSearch = order.restaurantName.toLowerCase().includes(searchQuery.toLowerCase()) ||
                           order.id.toLowerCase().includes(searchQuery.toLowerCase());
      const matchesStatus = statusFilter === 'All' || order.status === statusFilter;
      
      // Date filtering
      let matchesDate = true;
      if (dateFilter !== 'All Time') {
        const orderDate = new Date(order.date);
        const now = new Date();
        
        switch (dateFilter) {
          case 'Last 7 days':
            matchesDate = (now.getTime() - orderDate.getTime()) <= 7 * 24 * 60 * 60 * 1000;
            break;
          case 'Last 30 days':
            matchesDate = (now.getTime() - orderDate.getTime()) <= 30 * 24 * 60 * 60 * 1000;
            break;
          case 'Last 6 months':
            matchesDate = (now.getTime() - orderDate.getTime()) <= 180 * 24 * 60 * 60 * 1000;
            break;
        }
      }
      
      return matchesSearch && matchesStatus && matchesDate;
    });
  }, [searchQuery, statusFilter, dateFilter]);

  const toggleExpanded = (orderId: string) => {
    const newExpanded = new Set(expandedOrders);
    if (newExpanded.has(orderId)) {
      newExpanded.delete(orderId);
    } else {
      newExpanded.add(orderId);
    }
    setExpandedOrders(newExpanded);
  };

  const orderStats = useMemo(() => {
    const completed = mockOrders.filter(o => o.status === 'Completed');
    const totalSpent = completed.reduce((sum, order) => sum + order.total, 0);
    const favoriteRestaurant = completed.reduce((acc, order) => {
      acc[order.restaurantName] = (acc[order.restaurantName] || 0) + 1;
      return acc;
    }, {} as Record<string, number>);
    
    const mostOrdered = Object.entries(favoriteRestaurant).sort((a, b) => b[1] - a[1])[0];
    
    return {
      totalOrders: completed.length,
      totalSpent,
      favoriteRestaurant: mostOrdered ? mostOrdered[0] : 'N/A'
    };
  }, []);

  const renderStars = (rating: number) => {
    return Array.from({ length: 5 }, (_, i) => (
      <Star
        key={i}
        className={`h-4 w-4 ${
          i < rating 
            ? 'fill-yellow-400 text-yellow-400' 
            : 'text-gray-300'
        }`}
      />
    ));
  };

  const handleTabClick = (tab: string) => {
    setActiveTab(tab)
    if (onNavigate) {
      if (tab === 'Current Orders') {
        onNavigate('order-tracking')
      } else if (tab === 'Profile') {
        // Could navigate to a profile page in the future
        console.log('Profile page not implemented yet')
      }
    }
  };

  return (
    <div className="min-h-screen bg-gray-50">
      {/* Header */}
      <div className="bg-purple-gradient text-white sticky top-0 z-50 shadow-lg">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
          <div className="flex items-center justify-between h-16">
            {/* Logo */}
            <div className="flex items-center space-x-4">
              <div className="text-2xl font-bold">🍽️ Tably</div>
            </div>

            {/* Navigation */}
            <div className="hidden md:flex space-x-8">
              {['Current Orders', 'Order History', 'Profile'].map((tab) => (
                <button
                  key={tab}
                  onClick={() => handleTabClick(tab)}
                  className={`px-3 py-2 rounded-md text-sm font-medium transition-colors ${
                    activeTab === tab
                      ? 'bg-white/20 text-white'
                      : 'text-purple-100 hover:text-white hover:bg-white/10'
                  }`}
                >
                  {tab}
                </button>
              ))}
            </div>

            {/* Logout */}
            <Button
              onClick={onLogout}
              variant="ghost"
              size="sm"
              className="text-white hover:bg-white/10"
            >
              <LogOut className="h-4 w-4 mr-2" />
              Logout
            </Button>
          </div>
        </div>
      </div>

      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
        {/* Stats Cards */}
        <div className="grid grid-cols-1 md:grid-cols-3 gap-6 mb-8">
          <Card>
            <CardContent className="p-6">
              <div className="flex items-center">
                <div className="p-2 bg-purple-100 rounded-lg">
                  <Receipt className="h-8 w-8 text-purple-600" />
                </div>
                <div className="ml-4">
                  <p className="text-sm font-medium text-gray-600">Total Orders</p>
                  <p className="text-2xl font-bold text-gray-900">{orderStats.totalOrders}</p>
                </div>
              </div>
            </CardContent>
          </Card>

          <Card>
            <CardContent className="p-6">
              <div className="flex items-center">
                <div className="p-2 bg-green-100 rounded-lg">
                  <DollarSign className="h-8 w-8 text-green-600" />
                </div>
                <div className="ml-4">
                  <p className="text-sm font-medium text-gray-600">Total Spent</p>
                  <p className="text-2xl font-bold text-gray-900">${orderStats.totalSpent.toFixed(2)}</p>
                </div>
              </div>
            </CardContent>
          </Card>

          <Card>
            <CardContent className="p-6">
              <div className="flex items-center">
                <div className="p-2 bg-orange-100 rounded-lg">
                  <TrendingUp className="h-8 w-8 text-orange-600" />
                </div>
                <div className="ml-4">
                  <p className="text-sm font-medium text-gray-600">Favorite Restaurant</p>
                  <p className="text-lg font-bold text-gray-900 truncate">{orderStats.favoriteRestaurant}</p>
                </div>
              </div>
            </CardContent>
          </Card>
        </div>

        {/* Search and Filters */}
        <Card className="mb-8">
          <CardContent className="p-6">
            <div className="flex flex-col lg:flex-row lg:items-center lg:justify-between gap-4">
              <div className="flex-1 max-w-md">
                <div className="relative">
                  <Search className="absolute left-3 top-1/2 transform -translate-y-1/2 text-gray-400 h-4 w-4" />
                  <Input
                    placeholder="Search by restaurant or order ID..."
                    value={searchQuery}
                    onChange={(e) => setSearchQuery(e.target.value)}
                    className="pl-10"
                  />
                </div>
              </div>

              <div className="flex items-center gap-4">
                <Button
                  variant="outline"
                  size="sm"
                  onClick={() => setShowFilters(!showFilters)}
                  className="flex items-center gap-2"
                >
                  <Filter className="h-4 w-4" />
                  Filters
                  {showFilters ? <ChevronUp className="h-4 w-4" /> : <ChevronDown className="h-4 w-4" />}
                </Button>

                <Button variant="outline" size="sm" className="flex items-center gap-2">
                  <Download className="h-4 w-4" />
                  Export
                </Button>
              </div>
            </div>

            {showFilters && (
              <div className="mt-6 pt-6 border-t grid grid-cols-1 md:grid-cols-3 gap-4">
                <div>
                  <label className="block text-sm font-medium text-gray-700 mb-2">Date Range</label>
                  <select
                    value={dateFilter}
                    onChange={(e) => setDateFilter(e.target.value)}
                    className="w-full rounded-md border border-gray-300 px-3 py-2"
                  >
                    <option>All Time</option>
                    <option>Last 7 days</option>
                    <option>Last 30 days</option>
                    <option>Last 6 months</option>
                  </select>
                </div>

                <div>
                  <label className="block text-sm font-medium text-gray-700 mb-2">Status</label>
                  <select
                    value={statusFilter}
                    onChange={(e) => setStatusFilter(e.target.value)}
                    className="w-full rounded-md border border-gray-300 px-3 py-2"
                  >
                    <option>All</option>
                    <option>Completed</option>
                    <option>Cancelled</option>
                  </select>
                </div>

                <div className="flex items-end">
                  <Button
                    variant="outline"
                    onClick={() => {
                      setSearchQuery('');
                      setDateFilter('All Time');
                      setStatusFilter('All');
                    }}
                    className="w-full"
                  >
                    Clear Filters
                  </Button>
                </div>
              </div>
            )}
          </CardContent>
        </Card>

        {/* Order History */}
        {filteredOrders.length === 0 ? (
          <Card>
            <CardContent className="p-12 text-center">
              <div className="text-gray-400 mb-4">
                <Receipt className="h-16 w-16 mx-auto" />
              </div>
              <h3 className="text-lg font-medium text-gray-900 mb-2">No orders found</h3>
              <p className="text-gray-600">Try adjusting your search or filter criteria.</p>
            </CardContent>
          </Card>
        ) : (
          <div className="space-y-6">
            {filteredOrders.map((order) => (
              <Card key={order.id} className="overflow-hidden hover:shadow-md transition-shadow">
                <CardHeader className="pb-4">
                  <div className="flex items-start justify-between">
                    <div className="flex items-center space-x-4">
                      <div className="text-2xl">{order.restaurantLogo}</div>
                      <div>
                        <h3 className="text-lg font-semibold text-gray-900">{order.restaurantName}</h3>
                        <div className="flex items-center space-x-4 text-sm text-gray-600">
                          <span className="flex items-center">
                            <Calendar className="h-4 w-4 mr-1" />
                            {order.date}
                          </span>
                          <span className="flex items-center">
                            <Clock className="h-4 w-4 mr-1" />
                            {order.time}
                          </span>
                          <span className="text-gray-400">•</span>
                          <span className="font-medium">{order.id}</span>
                        </div>
                      </div>
                    </div>

                    <div className="flex items-center space-x-4">
                      <Badge 
                        variant={order.status === 'Completed' ? 'default' : 'destructive'}
                        className={order.status === 'Completed' ? 'bg-green-100 text-green-800' : ''}
                      >
                        {order.status}
                      </Badge>
                      <div className="text-right">
                        <div className="text-xl font-bold text-gray-900">${order.total.toFixed(2)}</div>
                        {order.rating && (
                          <div className="flex items-center mt-1">
                            {renderStars(order.rating)}
                          </div>
                        )}
                      </div>
                    </div>
                  </div>
                </CardHeader>

                <CardContent className="pt-0">
                  <div className="flex items-center justify-between">
                    <div className="flex items-center space-x-6 text-sm text-gray-600">
                      <span className="flex items-center">
                        <MapPin className="h-4 w-4 mr-1" />
                        {order.deliveryAddress}
                      </span>
                      <span className="flex items-center">
                        <CreditCard className="h-4 w-4 mr-1" />
                        {order.paymentMethod}
                      </span>
                    </div>

                    <Button
                      variant="ghost"
                      size="sm"
                      onClick={() => toggleExpanded(order.id)}
                      className="flex items-center"
                    >
                      {expandedOrders.has(order.id) ? 'Less Details' : 'More Details'}
                      {expandedOrders.has(order.id) ? (
                        <ChevronUp className="h-4 w-4 ml-1" />
                      ) : (
                        <ChevronDown className="h-4 w-4 ml-1" />
                      )}
                    </Button>
                  </div>

                  {expandedOrders.has(order.id) && (
                    <div className="mt-6 pt-6 border-t">
                      <h4 className="font-medium text-gray-900 mb-4">Order Items</h4>
                      <div className="space-y-2">
                        {order.items.map((item) => (
                          <div key={item.id} className="flex justify-between items-center py-2">
                            <div className="flex-1">
                              <span className="font-medium">{item.name}</span>
                              <span className="text-gray-600 ml-2">× {item.quantity}</span>
                            </div>
                            <span className="font-medium">${(item.price * item.quantity).toFixed(2)}</span>
                          </div>
                        ))}
                      </div>

                      <div className="flex justify-between items-center pt-4 border-t font-medium">
                        <span>Total</span>
                        <span>${order.total.toFixed(2)}</span>
                      </div>

                      <div className="flex gap-3 mt-6">
                        <Button variant="outline" size="sm" className="flex items-center">
                          <RotateCcw className="h-4 w-4 mr-2" />
                          Reorder
                        </Button>
                        {order.status === 'Completed' && !order.rating && (
                          <Button variant="outline" size="sm" className="flex items-center">
                            <Star className="h-4 w-4 mr-2" />
                            Rate & Review
                          </Button>
                        )}
                        <Button variant="outline" size="sm" className="flex items-center">
                          <Receipt className="h-4 w-4 mr-2" />
                          Get Receipt
                        </Button>
                      </div>
                    </div>
                  )}
                </CardContent>
              </Card>
            ))}
          </div>
        )}
      </div>
    </div>
  );
};