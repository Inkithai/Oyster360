import type { Metadata } from 'next'
import './globals.css'
import { Providers } from './providers'
import { Sidebar } from '@/components/layout/Sidebar'
import { MobileSidebar } from '@/components/layout/MobileSidebar'
import { ToastProvider } from '@/components/ui/use-toast'
import { Toaster } from '@/components/ui/toaster'
import { I18nProvider } from '@/lib/i18n'

export const metadata: Metadata = {
  title: 'Oyster360 — Sri Lanka Mushroom Farm Management',
  description: 'Track grow bags, record harvest flushes, manage LKR costs & buyer sales, and grow farm profit.',
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
          <I18nProvider>
            <ToastProvider>
              <div className="flex min-h-screen bg-background">
                {/* Desktop Sidebar */}
                <Sidebar />

                {/* Mobile Sidebar */}
                <MobileSidebar />

                {/* Main Content */}
                <main className="flex-1 p-4 md:p-8 w-full max-w-7xl mx-auto pt-16 md:pt-8">
                  {children}
                </main>
              </div>
              <Toaster />
            </ToastProvider>
          </I18nProvider>
        </Providers>
      </body>
    </html>
  )
}
