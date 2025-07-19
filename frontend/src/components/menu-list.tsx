import React, { useEffect, useState, useRef } from 'react';
import { useRouter } from 'next/navigation';
import { menuItemsService } from '@/services/menu-items';
import { analyzeMenuImage, bulkAnalyzeMenuImages } from '@/services/api';
import type { MenuImageAnalysisResult, ExtractedMenuItem } from '@/types/menu-items.types';
import { useAuthStore } from '@/stores/auth.store';
import { Button } from '@/components/ui/button';
import { Card, CardHeader, CardTitle, CardContent } from '@/components/ui/card';
import { Loader2, Utensils, ArrowLeft, Trash2 } from 'lucide-react';
import MenuItemForm from './menu-item-form';
import { Dialog, DialogContent, DialogHeader, DialogTitle } from '@/components/ui/dialog';
import { MenuItem } from '@/types/menu-items.types';

interface MenuListProps {
  businessId: string;
  onClose?: () => void;
}

export default function MenuList({ businessId }: MenuListProps) {
  const [menuItems, setMenuItems] = useState<MenuItem[]>([]);
  const [loading, setLoading] = useState(true);
  const [showAddForm, setShowAddForm] = useState(false);
  const [viewItem, setViewItem] = useState<MenuItem | null>(null);
  const [showAnalysisForm, setShowAnalysisForm] = useState(false);
  const [analyzing, setAnalyzing] = useState(false);
  const [analysisResults, setAnalysisResults] = useState<ExtractedMenuItem[]>([]);
  const [editedAnalysis, setEditedAnalysis] = useState<ExtractedMenuItem[]>([]);
  const [extractionCount, setExtractionCount] = useState<number | null>(null);
  const token = useAuthStore.getState().tokens?.access_token;
  const router = useRouter();
  const fileInputRef = useRef<HTMLInputElement>(null);

  // Add pagination state
  const [total, setTotal] = useState(0);
  const [page, setPage] = useState(1);
  const itemsPerPage = 20;
  const paginatedMenuItems = menuItems.slice((page - 1) * itemsPerPage, page * itemsPerPage);
  const totalPages = Math.ceil(total / itemsPerPage);

  const [selectedItems, setSelectedItems] = useState<string[]>([]);

  useEffect(() => {
    let isMounted = true;
    setLoading(true);
    if (!token || !businessId) {
      setLoading(false);
      return;
    }
    menuItemsService.getMenuItemsByBusiness(token, businessId, { page, page_size: itemsPerPage })
      .then(res => {
        if (isMounted) {
          setMenuItems(res.items);
          setTotal(res.total);
          setPage(res.page);
        }
      })
      .catch(() => {
        if (isMounted) setMenuItems([]);
      })
      .finally(() => {
        if (isMounted) setLoading(false);
      });
    return () => { isMounted = false; };
  }, [token, businessId, page]);

  useEffect(() => {
    const totalPages = Math.ceil(total / itemsPerPage);
    if (page > totalPages) {
      setPage(totalPages || 1);
    }
  }, [total, page, itemsPerPage]);

  const handleAnalyzeMenuImages = async (files: FileList | null) => {
    if (!files || !token) return;
    setAnalyzing(true);
    setAnalysisResults([]);
    setEditedAnalysis([]);
    setExtractionCount(null);
    try {
      let results: MenuImageAnalysisResult[] = [];
      if (files.length === 1) {
        const res = await analyzeMenuImage(token, files[0]);
        results = [res];
      } else if (files.length > 1) {
        results = await bulkAnalyzeMenuImages(token, Array.from(files));
      }
      // Flatten all extracted menu items
      const allItems = results.flatMap(r => r.menu_items || []);
      setAnalysisResults(allItems);
      setEditedAnalysis(allItems.map(item => ({ ...item })));
      setExtractionCount(allItems.length);
    } catch (err) {
      alert('Menu analysis failed.');
    } finally {
      setAnalyzing(false);
    }
  };

  const handleEditAnalysisItem = (idx: number, field: keyof ExtractedMenuItem, value: any) => {
    setEditedAnalysis(prev => prev.map((item, i) => i === idx ? { ...item, [field]: value } : item));
  };

  const handleSaveAnalyzedMenu = async () => {
    if (!token) return;
    setAnalyzing(true);
    try {
      await Promise.all(
        editedAnalysis.map(item =>
          menuItemsService.createMenuItem(token, {
            business_id: businessId,
            name: item.name,
            description: item.description,
            price: item.price ?? 0,
            available: true,
            quantity: item.quantity ?? 0,
            stock_level: {
              quantity_available: item.quantity ?? 0,
              total_quantity: item.quantity ?? 0,
            },
          })
        )
      );
      setShowAnalysisForm(false);
      setAnalysisResults([]);
      setEditedAnalysis([]);
      // After fetchMenuItems, set to last page
      // fetchMenuItems(); // This line is removed as per the edit hint
    } catch (err) {
      alert('Failed to save analyzed menu items.');
    } finally {
      setAnalyzing(false);
    }
  };

  const handleDeleteMenuItem = async (itemId: string) => {
    if (!token) return;
    if (!window.confirm('Are you sure you want to delete this menu item?')) return;
    await menuItemsService.deleteMenuItem(token, itemId);
    // updateMenuItemsAndResetPage(menuItems.filter(item => item.id !== itemId)); // This line is removed as per the edit hint
    setSelectedItems(prev => prev.filter(id => id !== itemId));
  };
  const handleBulkDelete = async () => {
    if (!token || selectedItems.length === 0) return;
    if (!window.confirm('Are you sure you want to delete the selected menu items?')) return;
    await Promise.all(selectedItems.map(id => menuItemsService.deleteMenuItem(token, id)));
    // updateMenuItemsAndResetPage(menuItems.filter(item => !selectedItems.includes(item.id))); // This line is removed as per the edit hint
    setSelectedItems([]);
  };
  const handleSelectItem = (itemId: string, checked: boolean) => {
    setSelectedItems(prev => checked ? [...prev, itemId] : prev.filter(id => id !== itemId));
  };
  const handleSelectAll = (checked: boolean) => {
    if (checked) {
      setSelectedItems(menuItems.map(item => item.id));
    } else {
      setSelectedItems([]);
    }
  };

  // After setMenuItems (add, delete, or bulk delete), reset currentPage to 1 if the current page would be empty or out of range
  // const updateMenuItemsAndResetPage = (newItems: MenuItem[], goToLastPage = false) => { // This line is removed as per the edit hint
  //   setMenuItems(newItems);
  //   const newTotalPages = Math.ceil(newItems.length / itemsPerPage);
  //   setCurrentPage(goToLastPage ? newTotalPages || 1 : (prev) => Math.min(prev, newTotalPages) || 1);
  // };

  const handleDiscardAnalysis = () => {
    if (window.confirm('Are you sure you want to discard the extracted menu items? This action cannot be undone.')) {
      setShowAnalysisForm(false);
      setAnalysisResults([]);
      setEditedAnalysis([]);
      setExtractionCount(null);
    }
  };

  return (
    <div className="max-w-6xl mx-auto py-8">
      <div className="flex items-center gap-2 mb-6">
        <Utensils className="h-6 w-6 text-emerald-600" />
        <h1 className="text-2xl font-bold">Menu Management</h1>
      </div>
      <div className="flex justify-end mb-4">
        <Button className="bg-emerald-600 hover:bg-emerald-700 mr-2" onClick={() => setShowAnalysisForm(true)}>Analyze Menu from Image</Button>
        <Button className="bg-emerald-600 hover:bg-emerald-700" onClick={() => setShowAddForm(true)}>+ Add Menu Item</Button>
      </div>
      {showAnalysisForm && (
        <Dialog open={showAnalysisForm} onOpenChange={open => {
          if (!open && (analysisResults.length > 0 || editedAnalysis.length > 0)) {
            handleDiscardAnalysis();
          } else if (!open) {
            setShowAnalysisForm(false);
          } else {
            setShowAnalysisForm(true);
          }
        }}>
          <DialogContent className="max-w-7xl min-h-[600px] max-h-[90vh] flex flex-col">
            <DialogHeader>
              <DialogTitle>Analyze Menu from Image</DialogTitle>
            </DialogHeader>
            <div className="space-y-4 flex-1 flex flex-col min-h-[400px]">
              {/* Improved Dropzone */}
              <div
                className="border-2 border-dashed border-emerald-400 rounded-lg p-8 text-center cursor-pointer hover:bg-emerald-50 transition relative"
                onClick={() => fileInputRef.current?.click()}
                onDragOver={e => { e.preventDefault(); e.stopPropagation(); }}
                onDrop={e => {
                  e.preventDefault();
                  e.stopPropagation();
                  if (e.dataTransfer.files && e.dataTransfer.files.length > 0) {
                    handleAnalyzeMenuImages(e.dataTransfer.files);
                  }
                }}
                style={{ minHeight: 120 }}
              >
                <input
                  ref={fileInputRef}
                  type="file"
                  accept="image/*"
                  multiple
                  className="hidden"
                  onChange={e => handleAnalyzeMenuImages(e.target.files)}
                  disabled={analyzing}
                />
                <div className="flex flex-col items-center justify-center h-full">
                  <span className="text-emerald-600 font-semibold text-lg mb-2">Drop menu images here or click to browse</span>
                  <span className="text-xs text-muted-foreground">Supported formats: JPG, PNG, WEBP, GIF, BMP (max 10 files)</span>
                </div>
              </div>
              {analyzing && <div className="flex items-center gap-2"><Loader2 className="animate-spin" /> Analyzing...</div>}
              {analysisResults.length > 0 && (
                <div className="flex flex-col flex-1 min-h-[200px] max-h-[calc(60vh)] overflow-y-auto border rounded-lg p-2 bg-gray-50">
                  {extractionCount !== null && (
                    <div className="mb-2 text-emerald-700 font-semibold">{extractionCount} menu item{extractionCount === 1 ? '' : 's'} extracted from image(s).</div>
                  )}
                  <div className="mb-2 text-sm text-yellow-700 bg-yellow-50 border border-yellow-200 rounded px-2 py-1">
                    Please specify the available stock (quantity) for each menu item before saving.
                  </div>
                  <h3 className="font-semibold mb-2">Extracted Menu Items</h3>
                  <div className="overflow-x-auto w-full">
                    <table className="min-w-full w-full divide-y divide-gray-200 text-base">
                      <thead>
                        <tr>
                          <th className="px-2 py-1 text-left text-xs font-medium text-gray-500 uppercase">#</th>
                          <th className="px-2 py-1 text-left text-xs font-medium text-gray-500 uppercase">Name</th>
                          <th className="px-2 py-1 text-left text-xs font-medium text-gray-500 uppercase">Description</th>
                          <th className="px-2 py-1 text-left text-xs font-medium text-gray-500 uppercase">Price</th>
                          <th className="px-2 py-1 text-left text-xs font-medium text-gray-500 uppercase">Category</th>
                          <th className="px-2 py-1 text-left text-xs font-medium text-gray-500 uppercase">Quantity</th>
                        </tr>
                      </thead>
                      <tbody className="bg-white divide-y divide-gray-200">
                        {editedAnalysis.map((item, idx) => (
                          <tr key={idx}>
                            <td className="px-2 py-1 text-center font-semibold">{idx + 1}</td>
                            <td className="px-2 py-1"><input className="border rounded px-1 py-0.5 w-32" value={item.name} onChange={e => handleEditAnalysisItem(idx, 'name', e.target.value)} required /></td>
                            <td className="px-2 py-1"><input className="border rounded px-1 py-0.5 w-48" value={item.description || ''} onChange={e => handleEditAnalysisItem(idx, 'description', e.target.value)} /></td>
                            <td className="px-2 py-1"><input className="border rounded px-1 py-0.5 w-20" type="number" step="0.01" value={item.price ?? ''} onChange={e => handleEditAnalysisItem(idx, 'price', parseFloat(e.target.value) || 0)} required min={0.01} /></td>
                            <td className="px-2 py-1"><input className="border rounded px-1 py-0.5 w-24" value={item.category || ''} onChange={e => handleEditAnalysisItem(idx, 'category', e.target.value)} /></td>
                            <td className="px-2 py-1">
                              <input
                                className="border rounded px-1 py-0.5 w-20"
                                type="number"
                                min={0}
                                step={1}
                                value={item.quantity === undefined ? '' : item.quantity}
                                onChange={e => {
                                  const val = e.target.value;
                                  setEditedAnalysis(prev => prev.map((itm, i) => i === idx ? { ...itm, quantity: val === '' ? undefined : Math.max(0, parseInt(val) || 0) } : itm));
                                }}
                                required
                              />
                            </td>
                            <td className="px-2 py-1 text-center">
                              <button
                                className="text-destructive hover:text-red-700"
                                title="Remove this item"
                                onClick={() => setEditedAnalysis(prev => prev.filter((_, i) => i !== idx))}
                              >
                                <Trash2 className="w-4 h-4" />
                              </button>
                            </td>
                          </tr>
                        ))}
                      </tbody>
                    </table>
                  </div>
                  {/* Fixed Save Button at Bottom Right */}
                  <div className="flex justify-end mt-4">
                    <Button
                      className="bg-emerald-600 hover:bg-emerald-700"
                      style={{ minWidth: 180 }}
                      onClick={handleSaveAnalyzedMenu}
                      disabled={analyzing || !editedAnalysis.every(item => item.name && (item.price ?? 0) > 0 && item.quantity !== undefined && item.quantity >= 0)}
                      title={!editedAnalysis.every(item => item.name && (item.price ?? 0) > 0 && item.quantity !== undefined && item.quantity >= 0) ? 'Please fill all required fields (name, price > 0, quantity >= 0) for all items.' : ''}
                    >
                      Save All to Menu
                    </Button>
                  </div>
                </div>
              )}
            </div>
          </DialogContent>
        </Dialog>
      )}
      {showAddForm && (
        <Dialog open={showAddForm} onOpenChange={() => setShowAddForm(false)}>
          <DialogContent className="max-w-lg">
            <DialogHeader>
              <DialogTitle>Add Menu Item</DialogTitle>
            </DialogHeader>
            <MenuItemForm
              businessId={businessId}
              onSuccess={async () => {
                setShowAddForm(false);
                // Refetch menu items after add
                setLoading(true);
                try {
                  const res = await menuItemsService.getMenuItemsByBusiness(token, businessId, { page, page_size: itemsPerPage });
                  setMenuItems(res.items);
                  setTotal(res.total);
                  setPage(res.page);
                } catch {}
                setLoading(false);
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
              onSuccess={async () => {
                setViewItem(null);
                // Refetch menu items after edit
                setLoading(true);
                try {
                  const res = await menuItemsService.getMenuItemsByBusiness(token, businessId, { page, page_size: itemsPerPage });
                  setMenuItems(res.items);
                  setTotal(res.total);
                  setPage(res.page);
                } catch {}
                setLoading(false);
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
              {/* Bulk Delete Button */}
              {selectedItems.length > 0 && (
                <div className="mb-2 flex justify-end">
                  <Button variant="destructive" size="sm" onClick={handleBulkDelete}>
                    Delete Selected ({selectedItems.length})
                  </Button>
                </div>
              )}
              <table className="min-w-full divide-y divide-gray-200">
                <thead>
                  <tr>
                    <th className="px-2 py-1">
                      <input
                        type="checkbox"
                        checked={menuItems.length > 0 && menuItems.every(item => selectedItems.includes(item.id))}
                        onChange={e => handleSelectAll(e.target.checked)}
                      />
                    </th>
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
                      <td className="px-2 py-1 text-center">
                        <input
                          type="checkbox"
                          checked={selectedItems.includes(item.id)}
                          onChange={e => handleSelectItem(item.id, e.target.checked)}
                        />
                      </td>
                      <td className="px-4 py-2 whitespace-nowrap">{item.name}</td>
                      <td className="px-4 py-2 whitespace-nowrap">{item.description || '-'}</td>
                      <td className="px-4 py-2 whitespace-nowrap">{
                        typeof item.price === 'number'
                          ? `$${item.price.toFixed(2)}`
                          : `$${Number(item.price).toFixed(2)}`
                      }</td>
                      <td className="px-4 py-2 whitespace-nowrap">{item.available ? 'Yes' : 'No'}</td>
                      <td className="px-4 py-2 whitespace-nowrap flex gap-2 items-center">
                        <Button size="sm" variant="outline" onClick={() => setViewItem(item)}>View</Button>
                        <button
                          className="ml-2 text-destructive hover:text-red-700"
                          title="Delete"
                          onClick={() => handleDeleteMenuItem(item.id)}
                        >
                          <Trash2 className="w-4 h-4" />
                        </button>
                      </td>
                    </tr>
                  ))}
                </tbody>
              </table>
            </div>
          )}
        </CardContent>
      </Card>
      {/* Add pagination controls below the table */}
      {totalPages > 1 && (
        <div className="flex justify-center items-center gap-2 mt-4">
          <Button size="sm" variant="outline" onClick={() => setPage(p => Math.max(1, p - 1))} disabled={page === 1}>Previous</Button>
          <span>Page {page} of {totalPages}</span>
          <Button size="sm" variant="outline" onClick={() => setPage(p => Math.min(totalPages, p + 1))} disabled={page === totalPages}>Next</Button>
        </div>
      )}
    </div>
  );
} 