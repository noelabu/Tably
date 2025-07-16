"use client";

import { ReactNode } from 'react';
import { useAuth } from '@/hooks/use-auth';
import { Button } from '@/components/ui/button';
import { Bell } from 'lucide-react';

export default function CustomerLayout({ children }: { children: ReactNode }) {
  const { user, logout } = useAuth();

  const handleLogout = async () => {
    await logout();
  };

  return (
    <div className="min-h-screen bg-background">
      {/* Header */}
      <header className="bg-white shadow-sm border-b">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
          <div className="flex justify-between items-center h-16">
            <div className="flex items-center">
              <h1 className="text-2xl font-bold text-primary">Tably</h1>
              <span className="ml-2 text-sm text-muted-foreground">Customer</span>
            </div>
            <div className="flex items-center space-x-4">
              <Bell className="h-5 w-5 text-muted-foreground" />
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
      {children}
    </div>
  );
} 