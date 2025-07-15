import React, { useEffect, useState } from 'react';
import { useRouter } from 'next/navigation';
import { menuItemsService } from '@/services/menu-items';
import { MenuItem } from '@/types/menu-items.types';
import { useAuthStore } from '@/stores/auth.store';
import { Button } from '@/components/ui/button';
import { Card, CardHeader, CardTitle, CardContent } from '@/components/ui/card';
import { Loader2, Utensils, ArrowLeft } from 'lucide-react';
import MenuItemForm from './menu-item-form';
import { Dialog, DialogContent, DialogHeader, DialogTitle } from '@/components/ui/dialog';

interface MenuListProps {
  businessId: string;
  onClose?: () => void;
}

export default function MenuList({ businessId }: MenuListProps) {
  const [menuItems, setMenuItems] = useState<MenuItem[]>([]);
  const [loading, setLoading] = useState(true);
  const [showAddForm, setShowAddForm] = useState(false);
  const [viewItem, setViewItem] = useState<MenuItem | null>(null);
  const token = useAuthStore.getState().tokens?.access_token;
  const router = useRouter();

  const fetchMenuItems = () => {
    if (!token || !businessId) return;
    setLoading(true);
    menuItemsService.getMenuItemsByBusiness(token, businessId)
      .then(res => setMenuItems(res.items))
      .finally(() => setLoading(false));
  };

  useEffect(() => {
    fetchMenuItems();
    // eslint-disable-next-line
  }, [token, businessId]);

  return (
    <div className="max-w-6xl mx-auto py-8">
      <div className="flex items-center gap-2 mb-6">
        <Utensils className="h-6 w-6 text-emerald-600" />
        <h1 className="text-2xl font-bold">Menu Management</h1>
      </div>
      <div className="flex justify-end mb-4">
        <Button className="bg-emerald-600 hover:bg-emerald-700" onClick={() => setShowAddForm(true)}>+ Add Menu Item</Button>
      </div>
      {showAddForm && (
        <Dialog open={showAddForm} onOpenChange={() => setShowAddForm(false)}>
          <DialogContent className="max-w-lg">
            <DialogHeader>
              <DialogTitle>Add Menu Item</DialogTitle>
            </DialogHeader>
            <MenuItemForm
              businessId={businessId}
              onSuccess={() => {
                setShowAddForm(false);
                fetchMenuItems();
              }}
              onCancel={() => setShowAddForm(false)}
            />
          </DialogContent>
        </Dialog>
      )}
      {viewItem && (
        <Dialog open={!!viewItem} onOpenChange={() => setViewItem(null)}>
          <DialogContent className="max-w-lg">
            <DialogHeader>
              <DialogTitle>Edit Menu Item</DialogTitle>
            </DialogHeader>
            <MenuItemForm
              businessId={businessId}
              menuItem={viewItem}
              editMode={true}
              onSuccess={() => {
                setViewItem(null);
                fetchMenuItems();
              }}
              onCancel={() => setViewItem(null)}
            />
          </DialogContent>
        </Dialog>
      )}
      <Card>
        <CardHeader>
          <CardTitle>Menu Items</CardTitle>
        </CardHeader>
        <CardContent>
          {loading ? (
            <div className="flex flex-col items-center justify-center py-16">
              <Loader2 className="h-10 w-10 animate-spin text-emerald-600 mb-4" />
              <span className="text-muted-foreground">Loading menu items...</span>
            </div>
          ) : (
            <div className="overflow-x-auto">
              <table className="min-w-full divide-y divide-gray-200">
                <thead>
                  <tr>
                    <th className="px-4 py-2 text-left text-xs font-medium text-gray-500 uppercase">Name</th>
                    <th className="px-4 py-2 text-left text-xs font-medium text-gray-500 uppercase">Description</th>
                    <th className="px-4 py-2 text-left text-xs font-medium text-gray-500 uppercase">Price</th>
                    <th className="px-4 py-2 text-left text-xs font-medium text-gray-500 uppercase">Available</th>
                    <th className="px-4 py-2 text-left text-xs font-medium text-gray-500 uppercase">Actions</th>
                  </tr>
                </thead>
                <tbody className="bg-white divide-y divide-gray-200">
                  {menuItems.map(item => (
                    <tr key={item.id}>
                      <td className="px-4 py-2 whitespace-nowrap">{item.name}</td>
                      <td className="px-4 py-2 whitespace-nowrap">{item.description || '-'}</td>
                      <td className="px-4 py-2 whitespace-nowrap">{
                        typeof item.price === 'number'
                          ? `$${item.price.toFixed(2)}`
                          : `$${Number(item.price).toFixed(2)}`
                      }</td>
                      <td className="px-4 py-2 whitespace-nowrap">{item.available ? 'Yes' : 'No'}</td>
                      <td className="px-4 py-2 whitespace-nowrap">
                        <Button size="sm" variant="outline" onClick={() => setViewItem(item)}>View</Button>
                      </td>
                    </tr>
                  ))}
                </tbody>
              </table>
            </div>
          )}
        </CardContent>
      </Card>
    </div>
  );
} 