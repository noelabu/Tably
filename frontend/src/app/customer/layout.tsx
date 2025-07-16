'use client'

import React from 'react';
import { useAuth } from '@/hooks/use-auth';
import { Button } from '@/components/ui/button';

export default function CustomerLayout({ children }: { children: React.ReactNode }) {
  const { user, logout } = useAuth();

  const handleLogout = async () => {
    await logout();
  };

  return (
    <div className="min-h-screen flex flex-col bg-background">
      <header className="bg-white shadow-sm border-b sticky top-0 z-10">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
          <div className="flex justify-between items-center h-16">
            <div className="flex items-center">
              <h1 className="text-2xl font-bold text-primary">Tably</h1>
              <span className="ml-2 text-sm text-muted-foreground">Customer</span>
            </div>
            <div className="flex items-center space-x-4">
              <span className="text-sm text-muted-foreground">Welcome, {user?.full_name || user?.email || 'Guest'}</span>
              {user && (
                <Button variant="outline" onClick={handleLogout}>
                  Logout
                </Button>
              )}
            </div>
          </div>
        </div>
      </header>
      {/* Add padding-top to prevent overlap with sticky header */}
      <main className="flex-1 w-full max-w-7xl mx-auto p-4 pt-8 sm:pt-10 lg:pt-12">
        {children}
      </main>
    </div>
  );
} 