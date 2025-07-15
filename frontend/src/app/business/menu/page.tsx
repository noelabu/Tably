"use client";

import { useEffect, useState } from "react";
import { useBusinessStore } from "@/stores/business.store";
import { Loader2 } from "lucide-react";
import MenuList from "@/components/menu-list";
import type { Business } from "@/types/business";
import { Button } from "@/components/ui/button";
import Link from 'next/link';
import { ChevronRight } from 'lucide-react';

export default function MenuManagementPage() {
  const [business, setBusiness] = useState<Business | null>(null);
  const [isLoading, setIsLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const getBusiness = useBusinessStore((state) => state.getBusiness);

  useEffect(() => {
    setIsLoading(true);
    setError(null);
    getBusiness()
      .then(setBusiness)
      .catch(() => setError("Failed to load business info."))
      .finally(() => setIsLoading(false));
  }, [getBusiness]);

  return (
    <>
      {/* Breadcrumbs */}
      <nav className="bg-white border-b">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 flex items-center h-12 space-x-2 text-sm">
          <Link href="/business/dashboard" className="text-muted-foreground hover:text-primary">Dashboard</Link>
          <ChevronRight className="h-4 w-4 text-muted-foreground" />
          <span className="text-primary font-medium">Menu</span>
        </div>
      </nav>
      <main className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
        {isLoading ? (
          <div className="flex flex-col items-center justify-center py-16">
            <Loader2 className="h-10 w-10 animate-spin text-emerald-600 mb-4" />
            <span className="text-muted-foreground">Loading business info...</span>
          </div>
        ) : error ? (
          <div className="flex flex-col items-center justify-center py-16">
            <span className="text-destructive font-semibold mb-2">{error}</span>
            <Button variant="outline" onClick={() => window.location.reload()}>Retry</Button>
          </div>
        ) : business?.id ? (
          <MenuList businessId={business.id} />
        ) : null}
      </main>
    </>
  );
} 