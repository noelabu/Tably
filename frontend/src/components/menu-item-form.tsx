import React, { useState } from 'react';
import { useMenuItemsStore } from '@/stores/menu_items.store';
import { Button } from '@/components/ui/button';
import { Input } from '@/components/ui/input';
import { Label } from '@/components/ui/label';
import { Card, CardHeader, CardTitle, CardContent } from '@/components/ui/card';
import { Loader2 } from 'lucide-react';
import { DialogTitle } from '@/components/ui/dialog';
import { MenuItem } from '@/types/menu-items.types';

interface MenuItemFormProps {
  businessId: string;
  onSuccess: () => void;
  onCancel: () => void;
  menuItem?: MenuItem;
  editMode?: boolean;
}

export default function MenuItemForm({ businessId, onSuccess, onCancel, menuItem, editMode }: MenuItemFormProps) {
  const [name, setName] = useState(menuItem?.name || '');
  const [description, setDescription] = useState(menuItem?.description || '');
  const [price, setPrice] = useState(menuItem ? String(menuItem.price) : '');
  const [imageUrl, setImageUrl] = useState(menuItem?.image_url || '');
  const [available, setAvailable] = useState(menuItem?.available ?? true);
  const [quantity, setQuantity] = useState(
    menuItem && (typeof menuItem.quantity === 'number' ? String(menuItem.quantity) : menuItem.stock_level?.quantity_available !== undefined ? String(menuItem.stock_level.quantity_available) : '0')
      || '0'
  );
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const createMenuItem = useMenuItemsStore((state) => state.createMenuItem);
  const updateMenuItem = useMenuItemsStore((state) => state.updateMenuItem);

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    setLoading(true);
    setError(null);
    try {
      if (editMode && menuItem) {
        const updatePayload: any = {
          name,
          description,
          price: parseFloat(price),
          image_url: imageUrl,
          available,
        };
        if (quantity !== undefined && quantity !== null) {
          updatePayload.quantity = parseInt(quantity, 10);
        }
        await updateMenuItem(menuItem.id, updatePayload);
      } else {
        const qty = parseInt(quantity, 10);
        await createMenuItem({
          business_id: businessId,
          name,
          description,
          price: parseFloat(price),
          image_url: imageUrl,
          available,
          quantity: qty,
          stock_level: {
            quantity_available: qty,
            total_quantity: qty,
          },
        });
      }
      onSuccess();
    } catch (err) {
      setError('Failed to save menu item.');
    } finally {
      setLoading(false);
    }
  };

  return (
    <form onSubmit={handleSubmit} className="space-y-4">
          <div>
            <Label htmlFor="name">Name</Label>
            <Input id="name" value={name} onChange={e => setName(e.target.value)} required />
          </div>
          <div>
            <Label htmlFor="description">Description</Label>
            <Input id="description" value={description} onChange={e => setDescription(e.target.value)} />
          </div>
          <div>
            <Label htmlFor="price">Price</Label>
            <Input id="price" type="number" step="0.01" value={price} onChange={e => setPrice(e.target.value)} required />
          </div>
          <div>
            <Label htmlFor="image_url">Image URL</Label>
            <Input id="image_url" value={imageUrl} onChange={e => setImageUrl(e.target.value)} />
          </div>
          <div>
            <Label htmlFor="quantity">Quantity</Label>
            <Input
              id="quantity"
              type="number"
              min="0"
              step="1"
              value={quantity}
              onChange={e => setQuantity(e.target.value)}
              required
            />
          </div>
          <div className="flex items-center gap-2">
            <input id="available" type="checkbox" checked={available} onChange={e => setAvailable(e.target.checked)} />
            <Label htmlFor="available">Available</Label>
          </div>
          {error && <div className="text-destructive text-sm">{error}</div>}
          <div className="flex justify-end gap-2">
            <Button type="button" variant="outline" onClick={onCancel} disabled={loading}>Cancel</Button>
            <Button type="submit" className="bg-emerald-600 hover:bg-emerald-700" disabled={loading}>
              {loading ? <Loader2 className="h-4 w-4 animate-spin mr-2" /> : null}
              {editMode ? 'Save Changes' : 'Add Item'}
            </Button>
          </div>
    </form>
  );
} 