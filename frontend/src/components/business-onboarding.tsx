"use client";

import React, { useState } from 'react';
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
import { 
  Building, 
  CreditCard, 
  CheckCircle,
  ArrowLeft,
  ArrowRight,
  FileUp,
  Utensils
} from 'lucide-react';

interface FormData {
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
  deliveryRadius: string;
  menuType: 'upload' | 'manual';
  menuFile?: File;
  paymentMethod: string;
  accountNumber: string;
}

const steps = [
  { id: 1, title: 'Business Information', icon: Building },
  { id: 2, title: 'Restaurant Details', icon: Utensils },
  { id: 3, title: 'Menu Setup', icon: FileUp },
  { id: 4, title: 'Payment Setup', icon: CreditCard },
  { id: 5, title: 'Review & Complete', icon: CheckCircle },
];

const cuisineTypes = [
  'American', 'Italian', 'Chinese', 'Mexican', 'Thai', 'Indian', 'Japanese', 'Mediterranean', 'French', 'Korean', 'Other'
];

const paymentMethods = [
  'Bank Account (ACH)', 'Credit Card', 'PayPal', 'Stripe'
];

export default function BusinessOnboarding() {
  const [currentStep, setCurrentStep] = useState(1);
  const [formData, setFormData] = useState<FormData>({
    businessName: '',
    address: '',
    city: '',
    state: '',
    zipCode: '',
    phone: '',
    email: '',
    cuisineType: '',
    openTime: '',
    closeTime: '',
    deliveryRadius: '',
    menuType: 'upload',
    paymentMethod: '',
    accountNumber: '',
  });
  const [errors, setErrors] = useState<Record<string, string>>({});

  const validateStep = (step: number): boolean => {
    const newErrors: Record<string, string> = {};

    switch (step) {
      case 1:
        if (!formData.businessName) newErrors.businessName = 'Business name is required';
        if (!formData.address) newErrors.address = 'Address is required';
        if (!formData.city) newErrors.city = 'City is required';
        if (!formData.state) newErrors.state = 'State is required';
        if (!formData.zipCode) newErrors.zipCode = 'ZIP code is required';
        if (!formData.phone) newErrors.phone = 'Phone number is required';
        if (!formData.email) newErrors.email = 'Email is required';
        break;
      case 2:
        if (!formData.cuisineType) newErrors.cuisineType = 'Cuisine type is required';
        if (!formData.openTime) newErrors.openTime = 'Opening time is required';
        if (!formData.closeTime) newErrors.closeTime = 'Closing time is required';
        if (!formData.deliveryRadius) newErrors.deliveryRadius = 'Delivery radius is required';
        break;
      case 3:
        if (formData.menuType === 'upload' && !formData.menuFile) {
          newErrors.menuFile = 'Please upload a menu file';
        }
        break;
      case 4:
        if (!formData.paymentMethod) newErrors.paymentMethod = 'Payment method is required';
        if (!formData.accountNumber) newErrors.accountNumber = 'Account information is required';
        break;
    }

    setErrors(newErrors);
    return Object.keys(newErrors).length === 0;
  };

  const handleNext = () => {
    if (validateStep(currentStep)) {
      setCurrentStep(prev => Math.min(prev + 1, 5));
    }
  };

  const handlePrevious = () => {
    setCurrentStep(prev => Math.max(prev - 1, 1));
  };

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
      if (errors.menuFile) {
        setErrors(prev => ({ ...prev, menuFile: '' }));
      }
    }
  };

  const progressPercentage = (currentStep / 5) * 100;

  const renderStepContent = () => {
    switch (currentStep) {
      case 1:
        return (
          <motion.div
            key="step1"
            initial={{ opacity: 0, x: 20 }}
            animate={{ opacity: 1, x: 0 }}
            exit={{ opacity: 0, x: -20 }}
            className="space-y-6"
          >
            <Card>
              <CardHeader>
                <CardTitle className="flex items-center gap-2">
                  <Building className="h-5 w-5 text-emerald-600" />
                  Business Information
                </CardTitle>
                <CardDescription>
                  Tell us about your restaurant business
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
          </motion.div>
        );

      case 2:
        return (
          <motion.div
            key="step2"
            initial={{ opacity: 0, x: 20 }}
            animate={{ opacity: 1, x: 0 }}
            exit={{ opacity: 0, x: -20 }}
            className="space-y-6"
          >
            <Card>
              <CardHeader>
                <CardTitle className="flex items-center gap-2">
                  <Utensils className="h-5 w-5 text-emerald-600" />
                  Restaurant Details
                </CardTitle>
                <CardDescription>
                  Configure your restaurant settings and operating hours
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

                <div>
                  <Label htmlFor="deliveryRadius">Delivery Radius (miles)</Label>
                  <Input
                    id="deliveryRadius"
                    type="number"
                    placeholder="5"
                    value={formData.deliveryRadius}
                    onChange={(e) => handleInputChange('deliveryRadius', e.target.value)}
                    className={errors.deliveryRadius ? 'border-destructive' : ''}
                  />
                  {errors.deliveryRadius && (
                    <p className="text-sm text-destructive mt-1">{errors.deliveryRadius}</p>
                  )}
                </div>
              </CardContent>
            </Card>
          </motion.div>
        );

      case 3:
        return (
          <motion.div
            key="step3"
            initial={{ opacity: 0, x: 20 }}
            animate={{ opacity: 1, x: 0 }}
            exit={{ opacity: 0, x: -20 }}
            className="space-y-6"
          >
            <Card>
              <CardHeader>
                <CardTitle className="flex items-center gap-2">
                  <FileUp className="h-5 w-5 text-emerald-600" />
                  Menu Setup
                </CardTitle>
                <CardDescription>
                  Upload your menu or add items manually
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
                  </div>
                )}

                {formData.menuType === 'manual' && (
                  <div className="space-y-4">
                    <p className="text-sm text-muted-foreground">
                      You can add menu items after completing the onboarding process.
                    </p>
                    <Card>
                      <CardContent className="pt-6">
                        <div className="flex items-center justify-center h-32 text-muted-foreground">
                          <div className="text-center">
                            <Utensils className="h-8 w-8 mx-auto mb-2" />
                            <p className="text-sm">Menu builder will be available next</p>
                          </div>
                        </div>
                      </CardContent>
                    </Card>
                  </div>
                )}
              </CardContent>
            </Card>
          </motion.div>
        );

      case 4:
        return (
          <motion.div
            key="step4"
            initial={{ opacity: 0, x: 20 }}
            animate={{ opacity: 1, x: 0 }}
            exit={{ opacity: 0, x: -20 }}
            className="space-y-6"
          >
            <Card>
              <CardHeader>
                <CardTitle className="flex items-center gap-2">
                  <CreditCard className="h-5 w-5 text-emerald-600" />
                  Payment Setup
                </CardTitle>
                <CardDescription>
                  Configure how you receive payments from customers
                </CardDescription>
              </CardHeader>
              <CardContent className="space-y-4">
                <div>
                  <Label htmlFor="paymentMethod">Payment Method</Label>
                  <Select
                    value={formData.paymentMethod}
                    onValueChange={(value) => handleInputChange('paymentMethod', value)}
                  >
                    <SelectTrigger className={errors.paymentMethod ? 'border-destructive' : ''}>
                      <SelectValue placeholder="Select payment method" />
                    </SelectTrigger>
                    <SelectContent>
                      {paymentMethods.map((method) => (
                        <SelectItem key={method} value={method}>
                          {method}
                        </SelectItem>
                      ))}
                    </SelectContent>
                  </Select>
                  {errors.paymentMethod && (
                    <p className="text-sm text-destructive mt-1">{errors.paymentMethod}</p>
                  )}
                </div>

                <div>
                  <Label htmlFor="accountNumber">Account Information</Label>
                  <Input
                    id="accountNumber"
                    placeholder="Account number or ID"
                    value={formData.accountNumber}
                    onChange={(e) => handleInputChange('accountNumber', e.target.value)}
                    className={errors.accountNumber ? 'border-destructive' : ''}
                  />
                  {errors.accountNumber && (
                    <p className="text-sm text-destructive mt-1">{errors.accountNumber}</p>
                  )}
                </div>

                <div className="bg-muted p-4 rounded-lg">
                  <p className="text-sm text-muted-foreground">
                    <strong>Note:</strong> Payment processing will be set up securely after account verification. 
                    We use industry-standard encryption to protect your financial information.
                  </p>
                </div>
              </CardContent>
            </Card>
          </motion.div>
        );

      case 5:
        return (
          <motion.div
            key="step5"
            initial={{ opacity: 0, x: 20 }}
            animate={{ opacity: 1, x: 0 }}
            exit={{ opacity: 0, x: -20 }}
            className="space-y-6"
          >
            <Card>
              <CardHeader>
                <CardTitle className="flex items-center gap-2">
                  <CheckCircle className="h-5 w-5 text-emerald-600" />
                  Review & Complete
                </CardTitle>
                <CardDescription>
                  Please review your information before submitting
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
                      <p><strong>Delivery Radius:</strong> {formData.deliveryRadius} miles</p>
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

                  <div>
                    <h4 className="font-medium mb-3">Payment</h4>
                    <div className="space-y-2 text-sm">
                      <p><strong>Method:</strong> {formData.paymentMethod}</p>
                      <p><strong>Account:</strong> ••••{formData.accountNumber.slice(-4)}</p>
                    </div>
                  </div>
                </div>

                <Separator />

                <div className="bg-emerald-50 p-4 rounded-lg">
                  <div className="flex items-center gap-2">
                    <CheckCircle className="h-5 w-5 text-emerald-600" />
                    <p className="text-sm font-medium">Ready to Complete Setup</p>
                  </div>
                  <p className="text-sm text-muted-foreground mt-1">
                    Your restaurant will be live on our platform within 24 hours after verification.
                  </p>
                </div>
              </CardContent>
            </Card>
          </motion.div>
        );

      default:
        return null;
    }
  };

  return (
    <div className="min-h-screen bg-secondary p-4">
      <div className="max-w-6xl mx-auto">
        {/* Header */}
        <div className="mb-8">
          <h1 className="text-3xl font-bold text-foreground mb-2">Welcome to FoodDelivery</h1>
          <p className="text-muted-foreground">Let's get your restaurant set up and ready to receive orders</p>
        </div>

        {/* Progress Bar */}
        <div className="mb-8">
          <div className="flex justify-between mb-4">
            <span className="text-sm font-medium text-foreground">Step {currentStep} of 5</span>
            <span className="text-sm text-muted-foreground">{Math.round(progressPercentage)}% Complete</span>
          </div>
          <Progress value={progressPercentage} className="h-2" />
        </div>

        <div className="grid grid-cols-1 lg:grid-cols-4 gap-8">
          {/* Main Content */}
          <div className="lg:col-span-3">
            <AnimatePresence mode="wait">
              {renderStepContent()}
            </AnimatePresence>

            {/* Navigation */}
            <div className="flex justify-between mt-8">
              <Button
                variant="outline"
                onClick={handlePrevious}
                disabled={currentStep === 1}
                className="flex items-center gap-2"
              >
                <ArrowLeft className="h-4 w-4" />
                Previous
              </Button>

              <Button
                onClick={currentStep === 5 ? () => console.log('Submit form') : handleNext}
                className="flex items-center gap-2 bg-emerald-600 hover:bg-emerald-700"
              >
                {currentStep === 5 ? 'Complete Setup' : 'Next'}
                {currentStep !== 5 && <ArrowRight className="h-4 w-4" />}
              </Button>
            </div>
          </div>

          {/* Progress Sidebar */}
          <div className="lg:col-span-1">
            <Card className="sticky top-4">
              <CardHeader>
                <CardTitle className="text-lg">Setup Progress</CardTitle>
              </CardHeader>
              <CardContent>
                <div className="space-y-4">
                  {steps.map((step) => {
                    const Icon = step.icon;
                    const isCompleted = currentStep > step.id;
                    const isCurrent = currentStep === step.id;

                    return (
                      <div
                        key={step.id}
                        className={`flex items-center gap-3 p-2 rounded-lg transition-colors ${
                          isCurrent
                            ? 'bg-emerald-50 text-emerald-900'
                            : isCompleted
                            ? 'text-emerald-600'
                            : 'text-muted-foreground'
                        }`}
                      >
                        <div
                          className={`flex items-center justify-center w-8 h-8 rounded-full ${
                            isCompleted
                              ? 'bg-emerald-600 text-white'
                              : isCurrent
                              ? 'bg-emerald-100 text-emerald-600'
                              : 'bg-muted'
                          }`}
                        >
                          {isCompleted ? (
                            <CheckCircle className="h-4 w-4" />
                          ) : (
                            <Icon className="h-4 w-4" />
                          )}
                        </div>
                        <span className={`text-sm font-medium ${isCurrent ? 'font-semibold' : ''}`}>
                          {step.title}
                        </span>
                      </div>
                    );
                  })}
                </div>
              </CardContent>
            </Card>
          </div>
        </div>
      </div>
    </div>
  );
}