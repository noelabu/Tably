import type { Metadata } from "next";
import "./globals.css";

export const metadata: Metadata = {
  title: "Tably - AI-Powered Restaurant Ordering",
  description: "Transform your restaurant with AI-powered ordering, real-time tracking, and advanced analytics. Boost revenue by 40% with intelligent recommendations.",
};

export default function RootLayout({
  children,
}: Readonly<{
  children: React.ReactNode;
}>) {
  return (
    <html lang="en">
      <body className="antialiased">{children}</body>
    </html>
  );
}