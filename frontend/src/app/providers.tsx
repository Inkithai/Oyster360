'use client'

import { QueryClient, QueryClientProvider } from '@tanstack/react-query'
import { useState } from 'react'

import { ErrorBoundary } from '@/components/ErrorBoundary'
import { configureLogger } from '@/lib/logger'

// Bootstrap structured frontend logging once, at provider mount. The DSN is
// optional: without it the logger writes console JSON only and never touches
// the network (see src/lib/logger.ts).
if (typeof window !== 'undefined') {
  configureLogger({
    dsn: process.env.NEXT_PUBLIC_SENTRY_DSN || null,
    release: process.env.NEXT_PUBLIC_APP_VERSION || null,
    environment: process.env.NODE_ENV === 'production' ? 'production' : 'development',
  })
}

export function Providers({ children }: { children: React.ReactNode }) {
  const [queryClient] = useState(() => new QueryClient())

  return (
    <ErrorBoundary>
      <QueryClientProvider client={queryClient}>{children}</QueryClientProvider>
    </ErrorBoundary>
  )
}
