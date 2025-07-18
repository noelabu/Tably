"use client";

import { useEffect, useState } from "react";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { Table, TableBody, TableCell, TableHead, TableHeader, TableRow } from "@/components/ui/table";
import { Badge } from "@/components/ui/badge";
import { Button } from "@/components/ui/button";
import { useOrderStore } from '@/stores/orders';
import { Order } from "@/types/orders";
import { useBusinessStore } from "@/stores/business.store";
import { get } from "http";
import {
  Breadcrumb,
  BreadcrumbList,
  BreadcrumbItem,
  BreadcrumbLink,
  BreadcrumbPage,
  BreadcrumbSeparator,
} from "@/components/ui/breadcrumb";
import { Eye, Wrench, Check } from 'lucide-react';
import { Tooltip, TooltipContent, TooltipProvider, TooltipTrigger } from '@/components/ui/tooltip';
import { Dialog, DialogContent, DialogHeader, DialogTitle, DialogDescription } from '@/components/ui/dialog';
import { Loader2 } from 'lucide-react';
import { useAuth } from "@/hooks/use-auth";

export default function BusinessOrdersPage() {
  const { user } = useAuth();
  const [orders, setOrders] = useState<Order[]>([]);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [page, setPage] = useState(1);
  const [pageSize] = useState(20);
  const [total, setTotal] = useState(0);
  const { business, getBusiness } = useBusinessStore();
  const [selectedOrder, setSelectedOrder] = useState<Order | null>(null);
  const [isOrderModalOpen, setIsOrderModalOpen] = useState(false);
  const [orderModalLoading, setOrderModalLoading] = useState(false);
  const orderStore = useOrderStore();
  // Track which order is being updated in the table
  const [updatingOrderId, setUpdatingOrderId] = useState<string | null>(null);

  useEffect(() => {
    if (!business) {
      getBusiness();
      return;
    }
    async function fetchOrders() {
      if (!business?.id) return;
      setLoading(true);
      setError(null);
      try {
        const response = await orderStore.getOrdersByBusiness(business.id, page, pageSize);
        if (response) {
          setOrders(response.items);
          setTotal(response.total);
        } else {
          setOrders([]);
          setTotal(0);
        }
      } catch (err) {
        setError("Failed to load orders.");
      } finally {
        setLoading(false);
      }
    }
    fetchOrders();
  }, [business, page, pageSize]);

  // Handler for updating order status from modal
  const handleUpdateOrderStatus = async (status: 'preparing' | 'completed') => {
    if (!selectedOrder) return;
    setOrderModalLoading(true);
    try {
      const updated = await orderStore.updateOrder(selectedOrder.id, { status });
      if (updated) {
        setSelectedOrder(updated);
        setIsOrderModalOpen(false);
        // Refresh orders
        if (business?.id) {
          setLoading(true);
          const response = await orderStore.getOrdersByBusiness(business.id, page, pageSize);
          setOrders(response?.items || []);
          setTotal(response?.total || 0);
          setLoading(false);
        }
      }
    } finally {
      setOrderModalLoading(false);
    }
  };

  return (
    <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
      {/* Breadcrumbs */}
      <Breadcrumb className="mb-6">
        <BreadcrumbList>
          <BreadcrumbItem>
            <BreadcrumbLink href="/business/dashboard">Dashboard</BreadcrumbLink>
          </BreadcrumbItem>
          <BreadcrumbSeparator />
          <BreadcrumbItem>
            <BreadcrumbPage>Orders</BreadcrumbPage>
          </BreadcrumbItem>
        </BreadcrumbList>
      </Breadcrumb>
      <Card>
        <CardHeader>
          <CardTitle>Orders</CardTitle>
        </CardHeader>
        <CardContent>
          {loading ? (
            <div>Loading...</div>
          ) : error ? (
            <div className="text-destructive text-sm">{error}</div>
          ) : orders.length === 0 ? (
            <div className="text-muted-foreground text-sm">No orders found.</div>
          ) : (
            <Table>
              <TableHeader>
                <TableRow>
                  <TableHead>Order ID</TableHead>
                  <TableHead>Status</TableHead>
                  <TableHead>Total</TableHead>
                  <TableHead>Created</TableHead>
                  <TableHead>Actions</TableHead>
                </TableRow>
              </TableHeader>
              <TableBody>
                {orders.map((order) => (
                  <TableRow key={order.id}>
                    <TableCell>{order.id}</TableCell>
                    <TableCell>
                      <Badge
                        className={
                          order.status === 'preparing'
                            ? 'bg-amber-100 text-amber-700 border-amber-200'
                            : order.status === 'completed'
                            ? 'bg-green-100 text-green-700 border-green-200'
                            : ''
                        }
                      >
                        {order.status.charAt(0).toUpperCase() + order.status.slice(1)}
                      </Badge>
                    </TableCell>
                    <TableCell>${Number(order.total_amount).toFixed(2)}</TableCell>
                    <TableCell>{new Date(order.created_at).toLocaleString()}</TableCell>
                    <TableCell className="space-x-2">
                      <TooltipProvider>
                        <Tooltip>
                          <TooltipTrigger asChild>
                            <Button size="icon" variant="outline" className="border-gray-300" onClick={async () => {
                              setOrderModalLoading(true);
                              setIsOrderModalOpen(true);
                              try {
                                const details = await orderStore.getOrder(order.id);
                                if (details) setSelectedOrder(details);
                              } finally {
                                setOrderModalLoading(false);
                              }
                            }}>
                              <Eye className="w-4 h-4" />
                            </Button>
                          </TooltipTrigger>
                          <TooltipContent>View</TooltipContent>
                        </Tooltip>
                        {order.status !== 'completed' && (
                          <>
                            <Tooltip>
                              <TooltipTrigger asChild>
                                <Button
                                  size="icon"
                                  variant="secondary"
                                  className="bg-amber-100 text-amber-700 hover:bg-amber-200 border-amber-200"
                                  disabled={updatingOrderId === order.id}
                                  onClick={async () => {
                                    setUpdatingOrderId(order.id);
                                    await orderStore.updateOrder(order.id, { status: 'preparing' });
                                    if (business?.id) {
                                      const response = await orderStore.getOrdersByBusiness(business.id, page, pageSize);
                                      setOrders(response?.items || []);
                                      setTotal(response?.total || 0);
                                    }
                                    setUpdatingOrderId(null);
                                  }}
                                >
                                  {updatingOrderId === order.id ? (
                                    <Loader2 className="w-4 h-4 animate-spin" />
                                  ) : (
                                    <Wrench className="w-4 h-4" />
                                  )}
                                </Button>
                              </TooltipTrigger>
                              <TooltipContent>Mark as Preparing</TooltipContent>
                            </Tooltip>
                            <Tooltip>
                              <TooltipTrigger asChild>
                                <Button
                                  size="icon"
                                  variant="secondary"
                                  className="bg-green-100 text-green-700 hover:bg-green-200 border-green-200"
                                  disabled={updatingOrderId === order.id}
                                  onClick={async () => {
                                    setUpdatingOrderId(order.id);
                                    await orderStore.updateOrder(order.id, { status: 'completed' });
                                    if (business?.id) {
                                      const response = await orderStore.getOrdersByBusiness(business.id, page, pageSize);
                                      setOrders(response?.items || []);
                                      setTotal(response?.total || 0);
                                    }
                                    setUpdatingOrderId(null);
                                  }}
                                >
                                  {updatingOrderId === order.id ? (
                                    <Loader2 className="w-4 h-4 animate-spin" />
                                  ) : (
                                    <Check className="w-4 h-4" />
                                  )}
                                </Button>
                              </TooltipTrigger>
                              <TooltipContent>Mark as Complete</TooltipContent>
                            </Tooltip>
                          </>
                        )}
                      </TooltipProvider>
                    </TableCell>
                  </TableRow>
                ))}
              </TableBody>
            </Table>
          )}
          {/* Pagination controls */}
          <div className="flex justify-between items-center mt-4">
            <Button
              variant="outline"
              disabled={page === 1}
              onClick={() => setPage((p) => Math.max(1, p - 1))}
            >
              Previous
            </Button>
            <span>
              Page {page} of {Math.ceil(total / pageSize) || 1}
            </span>
            <Button
              variant="outline"
              disabled={page * pageSize >= total}
              onClick={() => setPage((p) => p + 1)}
            >
              Next
            </Button>
          </div>
        </CardContent>
      </Card>
      {/* Order Details Modal */}
      <Dialog open={isOrderModalOpen} onOpenChange={setIsOrderModalOpen}>
        <DialogContent className="w-full max-w-2xl p-0">
          <DialogTitle asChild>
            <div className="flex items-center gap-2 text-lg font-semibold px-6 pt-2 pb-2 border-b">
              <Eye className="h-5 w-5" />
              Order Details
            </div>
          </DialogTitle>
          <Card className="border-none shadow-none">
            <CardContent className="pt-2">
              {orderModalLoading ? (
                <div className="flex items-center justify-center py-8"><Loader2 className="h-6 w-6 animate-spin text-primary" /></div>
              ) : selectedOrder ? (
                <div className="space-y-6">
                  <div className="grid grid-cols-2 gap-4">
                    <div>
                      <div className="text-xs text-muted-foreground">Order ID</div>
                      <div className="font-semibold break-all">{selectedOrder.id}</div>
                    </div>
                    <div>
                      <div className="text-xs text-muted-foreground">Status</div>
                      <Badge
                        className={
                          selectedOrder.status === 'preparing'
                            ? 'bg-amber-100 text-amber-700 border-amber-200'
                            : selectedOrder.status === 'completed'
                            ? 'bg-green-100 text-green-700 border-green-200'
                            : ''
                        }
                      >
                        {selectedOrder.status.charAt(0).toUpperCase() + selectedOrder.status.slice(1)}
                      </Badge>
                    </div>
                    <div>
                      <div className="text-xs text-muted-foreground">Total</div>
                      <div className="font-semibold">${Number(selectedOrder.total_amount).toFixed(2)}</div>
                    </div>
                    <div>
                      <div className="text-xs text-muted-foreground">Created</div>
                      <div>{new Date(selectedOrder.created_at).toLocaleString()}</div>
                    </div>
                  </div>
                  {/* Order Items Section */}
                  <div>
                    <div className="font-semibold mb-2">Order Items</div>
                    {selectedOrder.order_items && selectedOrder.order_items.length > 0 ? (
                      <div className="rounded-md border bg-card">
                        <Table>
                          <TableHeader>
                            <TableRow>
                              <TableHead>Item Name</TableHead>
                              <TableHead>Quantity</TableHead>
                              <TableHead>Price at Order</TableHead>
                            </TableRow>
                          </TableHeader>
                          <TableBody>
                            {selectedOrder.order_items.map(item => (
                              <TableRow key={item.id}>
                                <TableCell>{item.name}</TableCell>
                                <TableCell>{item.quantity}</TableCell>
                                <TableCell>${Number(item.price_at_order).toFixed(2)}</TableCell>
                              </TableRow>
                            ))}
                          </TableBody>
                        </Table>
                      </div>
                    ) : (
                      <div className="text-muted-foreground text-sm">No order items found for this order.</div>
                    )}
                  </div>
                  {/* Action Buttons */}
                  {selectedOrder.status !== 'completed' && (
                    <div className="flex gap-2 pt-2">
                      <Button
                        variant="outline"
                        className="text-yellow-600 border-yellow-600 hover:bg-yellow-50"
                        disabled={orderModalLoading}
                        onClick={() => handleUpdateOrderStatus('preparing')}
                      >
                        {orderModalLoading ? 'Updating...' : 'Mark as Preparing'}
                      </Button>
                      <Button
                        variant="default"
                        className="bg-green-600 hover:bg-green-700"
                        disabled={orderModalLoading}
                        onClick={() => handleUpdateOrderStatus('completed')}
                      >
                        {orderModalLoading ? 'Updating...' : 'Mark as Complete'}
                      </Button>
                    </div>
                  )}
                </div>
              ) : (
                <div>No order selected.</div>
              )}
            </CardContent>
          </Card>
        </DialogContent>
      </Dialog>
    </div>
  );
} 