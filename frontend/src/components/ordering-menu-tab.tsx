import React from 'react';
import { Button } from '@/components/ui/button';
import { ScrollArea } from '@/components/ui/scroll-area';
import { Card, CardHeader, CardTitle, CardContent } from '@/components/ui/card';
import { Badge } from '@/components/ui/badge';
import { Star, Clock, ChefHat, Plus } from 'lucide-react';
import type { MenuItem } from '@/types/menu-items.types';

interface OrderingMenuTabProps {
  categories: string[];
  selectedCategory: string;
  setSelectedCategory: (category: string) => void;
  filteredItems: MenuItem[];
  addToCart: (item: MenuItem, quantity?: number) => void;
}

const OrderingMenuTab: React.FC<OrderingMenuTabProps> = ({
  categories,
  selectedCategory,
  setSelectedCategory,
  filteredItems,
  addToCart,
}) => (
  <div className="h-full flex flex-col space-y-4">
    {/* Category Filter */}
    <div className="flex flex-wrap gap-2">
      {categories.map((category) => (
        <Button
          key={category}
          variant={selectedCategory === category ? 'default' : 'outline'}
          size="sm"
          onClick={() => setSelectedCategory(category)}
          className={selectedCategory === category ? 'bg-primary hover:bg-primary/90' : ''}
        >
          {category}
        </Button>
      ))}
    </div>
    {/* Menu Items */}
    <ScrollArea className="flex-1">
      <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
        {filteredItems.map((item) => (
          <Card key={item.id} className="bg-card">
            <CardHeader className="pb-3">
              <div className="flex items-start justify-between">
                <div>
                  <CardTitle className="text-lg flex items-center gap-2">
                    {item.name}
                  </CardTitle>
                  <p className="text-muted-foreground text-sm mt-1">{item.description}</p>
                </div>
                <div className="text-right">
                  <div className="text-xl font-semibold text-foreground">${item.price}</div>
                </div>
              </div>
            </CardHeader>
            <CardContent className="pt-0">
              <div className="flex items-center justify-between">
                <div className="flex items-center gap-4 text-sm text-muted-foreground">
                  <div className="flex items-center gap-1">
                    <ChefHat className="w-4 h-4" />
                    {item.category}
                  </div>
                </div>
                <Button onClick={() => addToCart(item)} className="bg-primary hover:bg-primary/90">
                  <Plus className="w-4 h-4 mr-1" />
                  Add
                </Button>
              </div>
            </CardContent>
          </Card>
        ))}
      </div>
    </ScrollArea>
  </div>
);

export default OrderingMenuTab; 