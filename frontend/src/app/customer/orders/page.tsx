'use client'

import { useState, useEffect } from 'react'
import { useAuth } from '@/hooks/use-auth'
import { Button } from '@/components/ui/button'
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card'
import { Input } from '@/components/ui/input'
import { Badge } from '@/components/ui/badge'
import AuthGuard from '@/components/auth-guard'
import { businessService } from '@/services/business'
import { Business } from '@/types/business'
import { Search, MapPin, Clock, Star, ArrowRight, ShoppingCart } from 'lucide-react'
import Link from 'next/link'

export default function OrdersPage() {
  const { user } = useAuth()
  const [businesses, setBusinesses] = useState<Business[]>([])
  const [loading, setLoading] = useState(true)
  const [searchTerm, setSearchTerm] = useState('')
  const [currentPage, setCurrentPage] = useState(1)
  const [totalPages, setTotalPages] = useState(1)

  useEffect(() => {
    loadBusinesses()
  }, [currentPage])

  const loadBusinesses = async () => {
    try {
      setLoading(true)
      const response = await businessService.getAllBusinesses(currentPage, 12)
      setBusinesses(response.items)
      setTotalPages(Math.ceil(response.total / 12))
    } catch (error) {
      console.error('Error loading businesses:', error)
    } finally {
      setLoading(false)
    }
  }

  const filteredBusinesses = businesses.filter(business =>
    business.name.toLowerCase().includes(searchTerm.toLowerCase()) ||
    business.cuisine_type.toLowerCase().includes(searchTerm.toLowerCase()) ||
    business.city.toLowerCase().includes(searchTerm.toLowerCase())
  )

  const getStatusColor = (openTime: string, closeTime: string) => {
    const now = new Date()
    const currentTime = now.getHours() * 60 + now.getMinutes()
    
    const [openHour, openMin] = openTime.split(':').map(Number)
    const [closeHour, closeMin] = closeTime.split(':').map(Number)
    
    const openMinutes = openHour * 60 + openMin
    const closeMinutes = closeHour * 60 + closeMin
    
    if (currentTime >= openMinutes && currentTime <= closeMinutes) {
      return 'bg-green-100 text-green-800'
    }
    return 'bg-red-100 text-red-800'
  }

  const getStatusText = (openTime: string, closeTime: string) => {
    const now = new Date()
    const currentTime = now.getHours() * 60 + now.getMinutes()
    
    const [openHour, openMin] = openTime.split(':').map(Number)
    const [closeHour, closeMin] = closeTime.split(':').map(Number)
    
    const openMinutes = openHour * 60 + openMin
    const closeMinutes = closeHour * 60 + closeMin
    
    if (currentTime >= openMinutes && currentTime <= closeMinutes) {
      return 'Open'
    }
    return 'Closed'
  }

  return (
    <AuthGuard requireAuth={true} allowedRoles={['customer']}>
      <div className="min-h-screen bg-background">
        {/* Header */}
        <header className="bg-white shadow-sm border-b">
          <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
            <div className="flex justify-between items-center h-16">
              <div className="flex items-center">
                <Link href="/customer/dashboard" className="text-2xl font-bold text-primary">
                  Tably
                </Link>
                <span className="ml-2 text-sm text-muted-foreground">Orders</span>
              </div>
              <div className="flex items-center space-x-4">
                <span className="text-sm text-muted-foreground">Welcome, {user?.full_name || user?.email}</span>
                <Link href="/customer/dashboard">
                  <Button variant="outline">Dashboard</Button>
                </Link>
              </div>
            </div>
          </div>
        </header>

        {/* Main Content */}
        <main className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
          {/* Search and Filters */}
          <div className="mb-8">
            <div className="flex flex-col sm:flex-row gap-4 items-center justify-between">
              <div className="relative flex-1 max-w-md">
                <Search className="absolute left-3 top-1/2 transform -translate-y-1/2 text-gray-400 h-4 w-4" />
                <Input
                  placeholder="Search restaurants, cuisine, or location..."
                  value={searchTerm}
                  onChange={(e) => setSearchTerm(e.target.value)}
                  className="pl-10"
                />
              </div>
              <div className="flex items-center space-x-2">
                <Badge variant="secondary" className="flex items-center gap-1">
                  <ShoppingCart className="h-3 w-3" />
                  {businesses.length} Restaurants
                </Badge>
              </div>
            </div>
          </div>

          {/* Loading State */}
          {loading && (
            <div className="flex justify-center items-center py-12">
              <div className="animate-spin rounded-full h-8 w-8 border-b-2 border-primary"></div>
            </div>
          )}

          {/* Businesses Grid */}
          {!loading && (
            <>
              <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6 mb-8">
                {filteredBusinesses.map((business) => (
                  <Card key={business.id} className="hover:shadow-lg transition-shadow cursor-pointer">
                    <Link href={`/customer/orders/${business.id}`}>
                      <CardHeader className="pb-3">
                        <div className="flex items-start justify-between">
                          <div className="flex-1">
                            <CardTitle className="text-lg">{business.name}</CardTitle>
                            <CardDescription className="flex items-center gap-1 mt-1">
                              <MapPin className="h-3 w-3" />
                              {business.city}, {business.state}
                            </CardDescription>
                          </div>
                          <Badge 
                            className={getStatusColor(business.open_time, business.close_time)}
                          >
                            {getStatusText(business.open_time, business.close_time)}
                          </Badge>
                        </div>
                      </CardHeader>
                      <CardContent>
                        <div className="space-y-3">
                          <div className="flex items-center justify-between">
                            <span className="text-sm text-muted-foreground">Cuisine</span>
                            <Badge variant="outline">{business.cuisine_type}</Badge>
                          </div>
                          
                          <div className="flex items-center justify-between">
                            <span className="text-sm text-muted-foreground">Hours</span>
                            <span className="text-sm">
                              {business.open_time} - {business.close_time}
                            </span>
                          </div>
                          
                          <div className="flex items-center justify-between">
                            <span className="text-sm text-muted-foreground">Phone</span>
                            <span className="text-sm">{business.phone}</span>
                          </div>
                          
                          <div className="pt-3 border-t">
                            <Button className="w-full" size="sm">
                              View Menu
                              <ArrowRight className="ml-2 h-4 w-4" />
                            </Button>
                          </div>
                        </div>
                      </CardContent>
                    </Link>
                  </Card>
                ))}
              </div>

              {/* Pagination */}
              {totalPages > 1 && (
                <div className="flex justify-center items-center space-x-2">
                  <Button
                    variant="outline"
                    size="sm"
                    onClick={() => setCurrentPage(Math.max(1, currentPage - 1))}
                    disabled={currentPage === 1}
                  >
                    Previous
                  </Button>
                  
                  <span className="text-sm text-muted-foreground">
                    Page {currentPage} of {totalPages}
                  </span>
                  
                  <Button
                    variant="outline"
                    size="sm"
                    onClick={() => setCurrentPage(Math.min(totalPages, currentPage + 1))}
                    disabled={currentPage === totalPages}
                  >
                    Next
                  </Button>
                </div>
              )}

              {/* No Results */}
              {filteredBusinesses.length === 0 && !loading && (
                <div className="text-center py-12">
                  <div className="text-gray-500 mb-4">
                    <Search className="h-12 w-12 mx-auto mb-4" />
                    <h3 className="text-lg font-medium">No restaurants found</h3>
                    <p className="text-sm">Try adjusting your search terms</p>
                  </div>
                </div>
              )}
            </>
          )}
        </main>
      </div>
    </AuthGuard>
  )
} 