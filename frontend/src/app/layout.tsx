import type { Metadata } from 'next'
import './globals.css'
import { Providers } from './providers'
import { Sidebar } from '@/components/layout/Sidebar'
import { MobileSidebar } from '@/components/layout/MobileSidebar'
import { ToastProvider } from '@/components/ui/use-toast'
import { Toaster } from '@/components/ui/toaster'

export const metadata: Metadata = {
  title: 'Oyster360',
  description: 'AI-Powered Oyster Mushroom Cultivation Platform',
}

export default function RootLayout({
  children,
}: {
  children: React.ReactNode
}) {
  return (
    <html lang="en">
      <body>
        <Providers>
          <ToastProvider>
            <div className="flex min-h-screen bg-background">
              {/* Desktop Sidebar */}
              <Sidebar />
              
              {/* Mobile Sidebar */}
              <MobileSidebar />
              
              {/* Main Content */}
              <main className="flex-1 p-6 md:p-8 w-full max-w-7xl mx-auto">
                {children}
              </main>
            </div>
            <Toaster />
          </ToastProvider>
        </Providers>
      </body>
    </html>
  )
}