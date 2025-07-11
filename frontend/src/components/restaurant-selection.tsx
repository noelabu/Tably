"use client"

import React, { useState } from 'react'
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card'
import { Badge } from '@/components/ui/badge'
import { Button } from '@/components/ui/button'
import { Input } from '@/components/ui/input'
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from '@/components/ui/select'
import { Star, Clock, MapPin, Search, Filter, LogOut, History } from 'lucide-react'

interface RestaurantSelectionProps {
  onLogout?: () => void
  onOrderHistory?: () => void
}

interface Restaurant {
  id: string
  name: string
  image: string
  rating: number
  reviewCount: number
  cuisine: string
  deliveryTime: string
  distance: string
  description: string
  featured?: boolean
}

const sampleRestaurants: Restaurant[] = [
  {
    id: "1",
    name: "Bella Vista Italiana",
    image: "/api/placeholder/300/200",
    rating: 4.8,
    reviewCount: 342,
    cuisine: "Italian",
    deliveryTime: "25-35 min",
    distance: "1.2 km",
    description: "Authentic Italian cuisine with fresh ingredients",
    featured: true,
  },
  {
    id: "2",
    name: "Dragon Palace",
    image: "/api/placeholder/300/200",
    rating: 4.6,
    reviewCount: 256,
    cuisine: "Chinese",
    deliveryTime: "30-40 min",
    distance: "0.8 km",
    description: "Traditional Chinese dishes with modern presentation",
  },
  {
    id: "3",
    name: "Burger Junction",
    image: "/api/placeholder/300/200",
    rating: 4.5,
    reviewCount: 189,
    cuisine: "American",
    deliveryTime: "20-30 min",
    distance: "1.5 km",
    description: "Gourmet burgers and craft beer selection",
  },
  {
    id: "4",
    name: "Sakura Sushi",
    image: "/api/placeholder/300/200",
    rating: 4.9,
    reviewCount: 421,
    cuisine: "Japanese",
    deliveryTime: "35-45 min",
    distance: "2.1 km",
    description: "Fresh sushi and traditional Japanese cuisine",
    featured: true,
  },
  {
    id: "5",
    name: "Curry House",
    image: "/api/placeholder/300/200",
    rating: 4.4,
    reviewCount: 167,
    cuisine: "Indian",
    deliveryTime: "40-50 min",
    distance: "1.8 km",
    description: "Aromatic spices and authentic Indian flavors",
  },
  {
    id: "6",
    name: "Mediterranean Coast",
    image: "/api/placeholder/300/200",
    rating: 4.7,
    reviewCount: 298,
    cuisine: "Mediterranean",
    deliveryTime: "30-40 min",
    distance: "1.1 km",
    description: "Fresh Mediterranean dishes with olive oil and herbs",
  },
]

const cuisineTypes = [
  "All Cuisines",
  "Italian",
  "Chinese",
  "Japanese",
  "Indian",
  "American",
  "Mediterranean",
  "Mexican",
  "Thai",
]

const deliveryTimes = [
  "Any Time",
  "Under 30 min",
  "30-45 min",
  "45+ min",
]

const ratings = [
  "Any Rating",
  "4.5+ stars",
  "4.0+ stars",
  "3.5+ stars",
]

export default function RestaurantSelection({ onLogout, onOrderHistory }: RestaurantSelectionProps) {
  const [searchQuery, setSearchQuery] = useState("")
  const [selectedCuisine, setSelectedCuisine] = useState("All Cuisines")
  const [selectedDeliveryTime, setSelectedDeliveryTime] = useState("Any Time")
  const [selectedRating, setSelectedRating] = useState("Any Rating")
  const [filteredRestaurants, setFilteredRestaurants] = useState(sampleRestaurants)

  const filterRestaurants = (
    query: string,
    cuisine: string,
    deliveryTime: string,
    rating: string
  ) => {
    let filtered = sampleRestaurants

    // Search filter
    if (query.trim()) {
      filtered = filtered.filter(
        (restaurant) =>
          restaurant.name.toLowerCase().includes(query.toLowerCase()) ||
          restaurant.cuisine.toLowerCase().includes(query.toLowerCase()) ||
          restaurant.description.toLowerCase().includes(query.toLowerCase())
      )
    }

    // Cuisine filter
    if (cuisine !== "All Cuisines") {
      filtered = filtered.filter((restaurant) => restaurant.cuisine === cuisine)
    }

    // Delivery time filter
    if (deliveryTime !== "Any Time") {
      filtered = filtered.filter((restaurant) => {
        const timeRange = restaurant.deliveryTime
        if (deliveryTime === "Under 30 min") {
          return timeRange.includes("20-30") || timeRange.includes("25-35")
        }
        if (deliveryTime === "30-45 min") {
          return timeRange.includes("30-40") || timeRange.includes("35-45")
        }
        if (deliveryTime === "45+ min") {
          return timeRange.includes("40-50") || timeRange.includes("45-")
        }
        return true
      })
    }

    // Rating filter
    if (rating !== "Any Rating") {
      const minRating = parseFloat(rating.split("+")[0])
      filtered = filtered.filter((restaurant) => restaurant.rating >= minRating)
    }

    setFilteredRestaurants(filtered)
  }

  const handleSearchChange = (value: string) => {
    setSearchQuery(value)
    filterRestaurants(value, selectedCuisine, selectedDeliveryTime, selectedRating)
  }

  const handleCuisineChange = (value: string) => {
    setSelectedCuisine(value)
    filterRestaurants(searchQuery, value, selectedDeliveryTime, selectedRating)
  }

  const handleDeliveryTimeChange = (value: string) => {
    setSelectedDeliveryTime(value)
    filterRestaurants(searchQuery, selectedCuisine, value, selectedRating)
  }

  const handleRatingChange = (value: string) => {
    setSelectedRating(value)
    filterRestaurants(searchQuery, selectedCuisine, selectedDeliveryTime, value)
  }

  const clearFilters = () => {
    setSearchQuery("")
    setSelectedCuisine("All Cuisines")
    setSelectedDeliveryTime("Any Time")
    setSelectedRating("Any Rating")
    setFilteredRestaurants(sampleRestaurants)
  }

  return (
    <div className="min-h-screen bg-background p-6">
      <div className="max-w-7xl mx-auto space-y-6">
        {/* Header */}
        <div className="flex items-center justify-between">
          <div>
            <h1 className="text-3xl font-bold text-foreground">Choose Your Restaurant</h1>
            <p className="text-muted-foreground">Discover amazing places to order from</p>
          </div>
          <div className="flex items-center gap-3">
            {onOrderHistory && (
              <Button
                variant="outline"
                size="sm"
                onClick={onOrderHistory}
                className="text-purple-600 hover:text-purple-700 hover:bg-purple-50"
              >
                <History className="h-4 w-4 mr-1" />
                Order History
              </Button>
            )}
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

        {/* Search and Filters */}
        <div className="mb-8 space-y-4">
          {/* Search Bar */}
          <div className="relative">
            <Search className="absolute left-3 top-1/2 transform -translate-y-1/2 h-4 w-4 text-muted-foreground" />
            <Input
              placeholder="Search restaurants, cuisines, or dishes..."
              value={searchQuery}
              onChange={(e) => handleSearchChange(e.target.value)}
              className="pl-10 h-12 text-base"
            />
          </div>

          {/* Filters */}
          <div className="flex flex-col sm:flex-row gap-4">
            <div className="flex-1">
              <Select value={selectedCuisine} onValueChange={handleCuisineChange}>
                <SelectTrigger className="h-12">
                  <SelectValue placeholder="Select cuisine" />
                </SelectTrigger>
                <SelectContent>
                  {cuisineTypes.map((cuisine) => (
                    <SelectItem key={cuisine} value={cuisine}>
                      {cuisine}
                    </SelectItem>
                  ))}
                </SelectContent>
              </Select>
            </div>

            <div className="flex-1">
              <Select value={selectedDeliveryTime} onValueChange={handleDeliveryTimeChange}>
                <SelectTrigger className="h-12">
                  <SelectValue placeholder="Delivery time" />
                </SelectTrigger>
                <SelectContent>
                  {deliveryTimes.map((time) => (
                    <SelectItem key={time} value={time}>
                      {time}
                    </SelectItem>
                  ))}
                </SelectContent>
              </Select>
            </div>

            <div className="flex-1">
              <Select value={selectedRating} onValueChange={handleRatingChange}>
                <SelectTrigger className="h-12">
                  <SelectValue placeholder="Minimum rating" />
                </SelectTrigger>
                <SelectContent>
                  {ratings.map((rating) => (
                    <SelectItem key={rating} value={rating}>
                      {rating}
                    </SelectItem>
                  ))}
                </SelectContent>
              </Select>
            </div>

            <Button
              variant="outline"
              onClick={clearFilters}
              className="h-12 px-6"
            >
              <Filter className="h-4 w-4 mr-2" />
              Clear
            </Button>
          </div>
        </div>

        {/* Results Count */}
        <div className="mb-6">
          <p className="text-muted-foreground">
            {filteredRestaurants.length} restaurant{filteredRestaurants.length !== 1 ? "s" : ""} found
          </p>
        </div>

        {/* Restaurant Grid */}
        {filteredRestaurants.length === 0 ? (
          <div className="text-center py-16">
            <div className="text-muted-foreground mb-4">
              <Search className="h-12 w-12 mx-auto mb-4 opacity-50" />
              <p className="text-lg">No restaurants found</p>
              <p className="text-sm">Try adjusting your search or filters</p>
            </div>
          </div>
        ) : (
          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
            {filteredRestaurants.map((restaurant) => (
              <Card
                key={restaurant.id}
                className="group cursor-pointer transition-all duration-300 hover:shadow-lg hover:-translate-y-1 relative overflow-hidden bg-card"
              >
                {restaurant.featured && (
                  <Badge className="absolute top-4 left-4 z-10 bg-primary text-primary-foreground">
                    Featured
                  </Badge>
                )}
                
                <div className="relative">
                  <img
                    src={restaurant.image}
                    alt={restaurant.name}
                    className="w-full h-48 object-cover transition-transform duration-300 group-hover:scale-105"
                  />
                  <div className="absolute inset-0 bg-black/0 group-hover:bg-black/10 transition-colors duration-300" />
                </div>

                <CardContent className="p-6">
                  <div className="space-y-3">
                    <div>
                      <h3 className="text-xl font-semibold text-foreground mb-1 group-hover:text-primary transition-colors">
                        {restaurant.name}
                      </h3>
                      <p className="text-muted-foreground text-sm line-clamp-2">
                        {restaurant.description}
                      </p>
                    </div>

                    <div className="flex items-center gap-2">
                      <div className="flex items-center gap-1">
                        <Star className="h-4 w-4 fill-primary text-primary" />
                        <span className="font-medium text-foreground">
                          {restaurant.rating}
                        </span>
                        <span className="text-muted-foreground text-sm">
                          ({restaurant.reviewCount})
                        </span>
                      </div>
                      <Badge variant="secondary" className="text-xs">
                        {restaurant.cuisine}
                      </Badge>
                    </div>

                    <div className="flex items-center justify-between text-sm text-muted-foreground">
                      <div className="flex items-center gap-1">
                        <Clock className="h-4 w-4" />
                        <span>{restaurant.deliveryTime}</span>
                      </div>
                      <div className="flex items-center gap-1">
                        <MapPin className="h-4 w-4" />
                        <span>{restaurant.distance}</span>
                      </div>
                    </div>

                    <Button className="w-full mt-4 bg-primary hover:bg-primary/90 text-primary-foreground">
                      View Menu
                    </Button>
                  </div>
                </CardContent>
              </Card>
            ))}
          </div>
        )}
      </div>
    </div>
  )
}