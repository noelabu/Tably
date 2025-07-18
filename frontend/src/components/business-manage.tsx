"use client";

import { menuItemsService } from '@/services/menu-items';
import React, { useState, useEffect, useRef } from 'react';
import { motion, AnimatePresence } from 'motion/react';
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card';
import { Button } from '@/components/ui/button';
import { Input } from '@/components/ui/input';
import { Label } from '@/components/ui/label';
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from '@/components/ui/select';
import { Checkbox } from '@/components/ui/checkbox';
import { Progress } from '@/components/ui/progress';
import { Badge } from '@/components/ui/badge';
import { Separator } from '@/components/ui/separator';
import { Dialog, DialogContent, DialogDescription, DialogHeader, DialogTitle } from '@/components/ui/dialog';
import { 
  Building, 
  CheckCircle,
  ArrowLeft,
  ArrowRight,
  FileUp,
  Utensils,
  Settings,
  Loader2,
  Trash2
} from 'lucide-react';
import { useBusinessStore } from '@/stores/business.store';
import { useAuthStore } from '@/stores/auth.store';
import { analyzeMenuImage, bulkAnalyzeMenuImages } from '@/services/api';
import type { MenuImageAnalysisResult, ExtractedMenuItem } from '@/types/menu-items.types';

interface FormData {
  id?: string; // hidden value for business id
  businessName: string;
  address: string;
  city: string;
  state: string;
  zipCode: string;
  phone: string;
  email: string;
  cuisineType: string;
  openTime: string;
  closeTime: string;
  menuType: 'upload' | 'manual';
  menuFile?: File;
}

const cuisineTypes = [
  'American', 'Italian', 'Chinese', 'Mexican', 'Thai', 'Indian', 'Japanese', 'Mediterranean', 'French', 'Korean', 'Other'
];

interface BusinessManageProps {
  isOpen: boolean;
  onClose: () => void;
  business?: import('@/types/business').Business | null;
}

export default function BusinessManage({ isOpen, onClose, business }: BusinessManageProps) {
  const token = useAuthStore.getState().tokens?.access_token;
  const [formData, setFormData] = useState<FormData>({
    id: business?.id,
    businessName: business?.name || '',
    address: business?.address || '',
    city: business?.city || '',
    state: business?.state || '',
    zipCode: business?.zip_code || '',
    phone: business?.phone || '',
    email: business?.email || '',
    cuisineType: business?.cuisine_type || '',
    openTime: business?.open_time || '',
    closeTime: business?.close_time || '',
    menuType: 'manual',
  });
  const [errors, setErrors] = useState<Record<string, string>>({});
  // Add state for image analysis in step 3
  const [showAnalysisForm, setShowAnalysisForm] = useState(false);
  const [analyzing, setAnalyzing] = useState(false);
  const [analysisResults, setAnalysisResults] = useState<ExtractedMenuItem[]>([]);
  const [editedAnalysis, setEditedAnalysis] = useState<ExtractedMenuItem[]>([]);
  const [extractionCount, setExtractionCount] = useState<number | null>(null);
  const [menuAnalyzedAndSaved, setMenuAnalyzedAndSaved] = useState(false);
  const fileInputRef = useRef<HTMLInputElement>(null);

  useEffect(() => {
    if (business) {
      setFormData({
        id: business.id,
        businessName: business.name || '',
        address: business.address || '',
        city: business.city || '',
        state: business.state || '',
        zipCode: business.zip_code || '',
        phone: business.phone || '',
        email: business.email || '',
        cuisineType: business.cuisine_type || '',
        openTime: business.open_time || '',
        closeTime: business.close_time || '',
        menuType: 'manual',
      });
    }
  }, [business, isOpen]);

  const { manageBusiness, updateBusiness, isLoading } = useBusinessStore();

  const handleInputChange = (field: keyof FormData, value: string) => {
    setFormData(prev => ({ ...prev, [field]: value }));
    if (errors[field]) {
      setErrors(prev => ({ ...prev, [field]: '' }));
    }
  };

  const handleFileUpload = (event: React.ChangeEvent<HTMLInputElement>) => {
    const file = event.target.files?.[0];
    if (file) {
      setFormData(prev => ({ ...prev, menuFile: file }));
      setMenuAnalyzedAndSaved(false);
      if (errors.menuFile) {
        setErrors(prev => ({ ...prev, menuFile: '' }));
      }
    }
  };

  const handleAnalyzeMenuImages = async (files: FileList | null) => {
    setAnalyzing(true);
    setAnalysisResults([]);
    setEditedAnalysis([]);
    setExtractionCount(null);
    try {
      let results: MenuImageAnalysisResult[] = [];
      if (files && files.length === 1) {
        const res = await analyzeMenuImage(token, files[0]);
        results = [res];
      } else if (files && files.length > 1) {
        results = await bulkAnalyzeMenuImages(token, Array.from(files));
      }
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
    if (!token) {
      console.error('No auth token found for menu analysis save.');
      alert('Authentication error: Please log in again.');
      return;
    }
    setAnalyzing(true);
    try {
      await Promise.all(
        editedAnalysis.map(item =>
          menuItemsService.createMenuItem(token, {
            business_id: formData.id!,
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
      setExtractionCount(null);
      setMenuAnalyzedAndSaved(true);
      // Optionally, refresh menu items in dashboard
    } catch (err) {
      console.error('Failed to save analyzed menu items:', err);
      alert('Failed to save analyzed menu items.');
    } finally {
      setAnalyzing(false);
    }
  };

  const handleDiscardAnalysis = () => {
    if (window.confirm('Are you sure you want to discard the extracted menu items? This action cannot be undone.')) {
      setShowAnalysisForm(false);
      setAnalysisResults([]);
      setEditedAnalysis([]);
      setExtractionCount(null);
      setMenuAnalyzedAndSaved(false);
    }
  };

  const handleSave = async () => {
    // Validate all fields at once
    const newErrors: Record<string, string> = {};
    if (!formData.businessName) newErrors.businessName = 'Business name is required';
    if (!formData.address) newErrors.address = 'Address is required';
    if (!formData.city) newErrors.city = 'City is required';
    if (!formData.state) newErrors.state = 'State is required';
    if (!formData.zipCode) newErrors.zipCode = 'ZIP code is required';
    if (!formData.phone) newErrors.phone = 'Phone number is required';
    if (!formData.email) newErrors.email = 'Email is required';
    if (!formData.cuisineType) newErrors.cuisineType = 'Cuisine type is required';
    if (!formData.openTime) newErrors.openTime = 'Opening time is required';
    if (!formData.closeTime) newErrors.closeTime = 'Closing time is required';
    if (
      formData.menuType === 'upload' &&
      !formData.menuFile &&
      !menuAnalyzedAndSaved
    ) {
      newErrors.menuFile = 'Please upload a menu file or analyze and save menu items from image.';
    }
    setErrors(newErrors);
    if (Object.keys(newErrors).length > 0) return;

    const businessPayload = {
      id: String(formData.id ?? ''),
      name: formData.businessName,
      address: formData.address,
      city: formData.city,
      state: formData.state,
      zip_code: formData.zipCode,
      phone: formData.phone,
      email: formData.email,
      cuisine_type: formData.cuisineType,
      open_time: formData.openTime,
      close_time: formData.closeTime,
    };
    if (formData.id == "" || formData.id == undefined) {
      await manageBusiness(businessPayload);
    } else {
      await updateBusiness(businessPayload);
    }
    onClose();
  };

  return (
    <Dialog open={isOpen} onOpenChange={onClose}>
      <DialogContent className="w-full max-w-6xl sm:min-w-[800px] flex flex-col p-0" style={{ height: '90vh' }}>
        {/* Modal Header */}
        <div className="sticky top-0 z-10 bg-white px-4 sm:px-6 pt-4 pb-2 border-b">
          <DialogHeader>
            <DialogTitle className="flex items-center gap-2">
              <Settings className="h-5 w-5" />
              Business Management
            </DialogTitle>
            <DialogDescription>
              Update your restaurant settings and configuration
            </DialogDescription>
          </DialogHeader>
        </div>

        {/* Modal Body (Scrollable) */}
        <div className="flex-1 overflow-y-auto px-4 sm:px-6 py-6 space-y-8 pb-28">
          {isLoading && isOpen ? (
            <div className="flex flex-col items-center justify-center py-16">
              <Loader2 className="h-10 w-10 animate-spin text-emerald-600 mb-4" />
              <span className="text-muted-foreground">Loading business data...</span>
            </div>
          ) : (
            <>
              {/* Business Information */}
              <Card>
                <CardHeader>
                  <CardTitle className="flex items-center gap-2">
                    <Building className="h-5 w-5 text-emerald-600" />
                    Business Information
                  </CardTitle>
                  <CardDescription>
                    Update your restaurant business information
                  </CardDescription>
                </CardHeader>
                <CardContent className="space-y-4">
                  <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                    <div className="md:col-span-2">
                      <Label htmlFor="businessName">Business Name</Label>
                      <Input
                        id="businessName"
                        placeholder="Enter your restaurant name"
                        value={formData.businessName}
                        onChange={(e) => handleInputChange('businessName', e.target.value)}
                        className={errors.businessName ? 'border-destructive' : ''}
                      />
                      {errors.businessName && (
                        <p className="text-sm text-destructive mt-1">{errors.businessName}</p>
                      )}
                    </div>
                    <div className="md:col-span-2">
                      <Label htmlFor="address">Street Address</Label>
                      <Input
                        id="address"
                        placeholder="Enter your business address"
                        value={formData.address}
                        onChange={(e) => handleInputChange('address', e.target.value)}
                        className={errors.address ? 'border-destructive' : ''}
                      />
                      {errors.address && (
                        <p className="text-sm text-destructive mt-1">{errors.address}</p>
                      )}
                    </div>
                    <div>
                      <Label htmlFor="city">City</Label>
                      <Input
                        id="city"
                        placeholder="City"
                        value={formData.city}
                        onChange={(e) => handleInputChange('city', e.target.value)}
                        className={errors.city ? 'border-destructive' : ''}
                      />
                      {errors.city && (
                        <p className="text-sm text-destructive mt-1">{errors.city}</p>
                      )}
                    </div>
                    <div>
                      <Label htmlFor="state">State</Label>
                      <Input
                        id="state"
                        placeholder="State"
                        value={formData.state}
                        onChange={(e) => handleInputChange('state', e.target.value)}
                        className={errors.state ? 'border-destructive' : ''}
                      />
                      {errors.state && (
                        <p className="text-sm text-destructive mt-1">{errors.state}</p>
                      )}
                    </div>
                    <div>
                      <Label htmlFor="zipCode">ZIP Code</Label>
                      <Input
                        id="zipCode"
                        placeholder="ZIP Code"
                        value={formData.zipCode}
                        onChange={(e) => handleInputChange('zipCode', e.target.value)}
                        className={errors.zipCode ? 'border-destructive' : ''}
                      />
                      {errors.zipCode && (
                        <p className="text-sm text-destructive mt-1">{errors.zipCode}</p>
                      )}
                    </div>
                    <div>
                      <Label htmlFor="phone">Phone Number</Label>
                      <Input
                        id="phone"
                        placeholder="(555) 123-4567"
                        value={formData.phone}
                        onChange={(e) => handleInputChange('phone', e.target.value)}
                        className={errors.phone ? 'border-destructive' : ''}
                      />
                      {errors.phone && (
                        <p className="text-sm text-destructive mt-1">{errors.phone}</p>
                      )}
                    </div>
                    <div>
                      <Label htmlFor="email">Email Address</Label>
                      <Input
                        id="email"
                        type="email"
                        placeholder="business@example.com"
                        value={formData.email}
                        onChange={(e) => handleInputChange('email', e.target.value)}
                        className={errors.email ? 'border-destructive' : ''}
                      />
                      {errors.email && (
                        <p className="text-sm text-destructive mt-1">{errors.email}</p>
                      )}
                    </div>
                  </div>
                </CardContent>
              </Card>

              {/* Restaurant Details */}
              <Card>
                <CardHeader>
                  <CardTitle className="flex items-center gap-2">
                    <Utensils className="h-5 w-5 text-emerald-600" />
                    Restaurant Details
                  </CardTitle>
                  <CardDescription>
                    Update your restaurant settings and operating hours
                  </CardDescription>
                </CardHeader>
                <CardContent className="space-y-4">
                  <div>
                    <Label htmlFor="cuisineType">Cuisine Type</Label>
                    <Select
                      value={formData.cuisineType}
                      onValueChange={(value) => handleInputChange('cuisineType', value)}
                    >
                      <SelectTrigger className={errors.cuisineType ? 'border-destructive' : ''}>
                        <SelectValue placeholder="Select cuisine type" />
                      </SelectTrigger>
                      <SelectContent>
                        {cuisineTypes.map((cuisine) => (
                          <SelectItem key={cuisine} value={cuisine}>
                            {cuisine}
                          </SelectItem>
                        ))}
                      </SelectContent>
                    </Select>
                    {errors.cuisineType && (
                      <p className="text-sm text-destructive mt-1">{errors.cuisineType}</p>
                    )}
                  </div>
                  <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                    <div>
                      <Label htmlFor="openTime">Opening Time</Label>
                      <Input
                        id="openTime"
                        type="time"
                        value={formData.openTime}
                        onChange={(e) => handleInputChange('openTime', e.target.value)}
                        className={errors.openTime ? 'border-destructive' : ''}
                      />
                      {errors.openTime && (
                        <p className="text-sm text-destructive mt-1">{errors.openTime}</p>
                      )}
                    </div>
                    <div>
                      <Label htmlFor="closeTime">Closing Time</Label>
                      <Input
                        id="closeTime"
                        type="time"
                        value={formData.closeTime}
                        onChange={(e) => handleInputChange('closeTime', e.target.value)}
                        className={errors.closeTime ? 'border-destructive' : ''}
                      />
                      {errors.closeTime && (
                        <p className="text-sm text-destructive mt-1">{errors.closeTime}</p>
                      )}
                    </div>
                  </div>
                </CardContent>
              </Card>

              {/* Menu Setup */}
              <Card>
                <CardHeader>
                  <CardTitle className="flex items-center gap-2">
                    <FileUp className="h-5 w-5 text-emerald-600" />
                    Menu Setup
                  </CardTitle>
                  <CardDescription>
                    Update your menu or add new items
                  </CardDescription>
                </CardHeader>
                <CardContent className="space-y-6">
                  <div className="flex gap-4">
                    <div className="flex items-center space-x-2">
                      <Checkbox
                        id="upload"
                        checked={formData.menuType === 'upload'}
                        onCheckedChange={() => handleInputChange('menuType', 'upload')}
                      />
                      <Label htmlFor="upload">Upload menu file</Label>
                    </div>
                    <div className="flex items-center space-x-2">
                      <Checkbox
                        id="manual"
                        checked={formData.menuType === 'manual'}
                        onCheckedChange={() => handleInputChange('menuType', 'manual')}
                      />
                      <Label htmlFor="manual">Add manually</Label>
                    </div>
                  </div>
                  {formData.menuType === 'upload' && (
                    <>
                      <div className="border-2 border-dashed border-muted-foreground/25 rounded-lg p-8 text-center">
                        <FileUp className="h-12 w-12 mx-auto text-muted-foreground mb-4" />
                        <div className="space-y-2">
                          <Label htmlFor="menuFile" className="text-sm font-medium cursor-pointer">
                            Drop your menu file here, or click to browse
                          </Label>
                          <p className="text-xs text-muted-foreground">
                            Supported formats: PDF, DOC, DOCX, JPG, PNG (max 10MB)
                          </p>
                          <Input
                            id="menuFile"
                            type="file"
                            accept=".pdf,.doc,.docx,.jpg,.jpeg,.png"
                            onChange={handleFileUpload}
                            className="hidden"
                          />
                        </div>
                        {formData.menuFile && (
                          <div className="mt-4">
                            <Badge variant="secondary" className="bg-emerald-50 text-emerald-700">
                              {formData.menuFile.name}
                            </Badge>
                          </div>
                        )}
                        {errors.menuFile && (
                          <p className="text-sm text-destructive mt-2">{errors.menuFile}</p>
                        )}
                        <div className="mt-4">
                          <Button className="bg-emerald-600 hover:bg-emerald-700" onClick={() => setShowAnalysisForm(true)}>
                            Analyze Menu from Image
                          </Button>
                        </div>
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
                                    <Button variant="outline" onClick={handleDiscardAnalysis} disabled={analyzing}>
                                      Discard
                                    </Button>
                                  </div>
                                </div>
                              )}
                            </div>
                          </DialogContent>
                        </Dialog>
                      )}
                    </>
                  )}
                  {formData.menuType === 'manual' && (
                    <div className="space-y-4">
                      <p className="text-sm text-muted-foreground">
                        You can manage menu items in the main dashboard.
                      </p>
                      <Card>
                        <CardContent className="pt-6">
                          <div className="flex items-center justify-center h-32 text-muted-foreground">
                            <div className="text-center">
                              <Utensils className="h-8 w-8 mx-auto mb-2" />
                              <p className="text-sm">Menu management available in dashboard</p>
                            </div>
                          </div>
                        </CardContent>
                      </Card>
                    </div>
                  )}
                </CardContent>
              </Card>

              {/* Review & Save Changes */}
              <Card>
                <CardHeader>
                  <CardTitle className="flex items-center gap-2">
                    <CheckCircle className="h-5 w-5 text-emerald-600" />
                    Review & Save Changes
                  </CardTitle>
                  <CardDescription>
                    Please review your changes before saving
                  </CardDescription>
                </CardHeader>
                <CardContent className="space-y-6">
                  <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
                    <div>
                      <h4 className="font-medium mb-3">Business Information</h4>
                      <div className="space-y-2 text-sm">
                        <p><strong>Name:</strong> {formData.businessName}</p>
                        <p><strong>Address:</strong> {formData.address}, {formData.city}, {formData.state} {formData.zipCode}</p>
                        <p><strong>Phone:</strong> {formData.phone}</p>
                        <p><strong>Email:</strong> {formData.email}</p>
                      </div>
                    </div>
                    <div>
                      <h4 className="font-medium mb-3">Restaurant Details</h4>
                      <div className="space-y-2 text-sm">
                        <p><strong>Cuisine:</strong> {formData.cuisineType}</p>
                        <p><strong>Hours:</strong> {formData.openTime} - {formData.closeTime}</p>
                      </div>
                    </div>
                    <div>
                      <h4 className="font-medium mb-3">Menu</h4>
                      <div className="space-y-2 text-sm">
                        <p><strong>Setup Type:</strong> {formData.menuType === 'upload' ? 'File Upload' : 'Manual Entry'}</p>
                        {formData.menuFile && (
                          <p><strong>File:</strong> {formData.menuFile.name}</p>
                        )}
                      </div>
                    </div>
                  </div>
                  <Separator />
                  <div className="bg-emerald-50 p-4 rounded-lg">
                    <div className="flex items-center gap-2">
                      <CheckCircle className="h-5 w-5 text-emerald-600" />
                      <p className="text-sm font-medium">Ready to Save Changes</p>
                    </div>
                    <p className="text-sm text-muted-foreground mt-1">
                      Your business information will be updated immediately.
                    </p>
                  </div>
                </CardContent>
              </Card>
            </>
          )}
        </div>

        {/* Modal Footer (Sticky) */}
        <div className="bottom-0 z-10 bg-white px-4 sm:px-6 py-4 border-t flex justify-end gap-2">
          <Button
            variant="outline"
            onClick={onClose}
          >
            Cancel
          </Button>
          <Button
            onClick={handleSave}
            className="flex items-center gap-2 bg-emerald-600 hover:bg-emerald-700"
          >
            Save Changes
          </Button>
        </div>
      </DialogContent>
    </Dialog>
  );
}