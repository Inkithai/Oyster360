'use client'

import { Component, type ErrorInfo, type ReactNode } from 'react'

import { reportError } from '@/lib/logger'

interface ErrorBoundaryProps {
  children: ReactNode
  fallback?: ReactNode
}

interface ErrorBoundaryState {
  hasError: boolean
}

/**
 * Catches render-time exceptions in the client tree, reports them with the
 * structured logger (Sentry-compatible transport when configured), and shows
 * a recovery fallback instead of a blank page.
 */
export class ErrorBoundary extends Component<ErrorBoundaryProps, ErrorBoundaryState> {
  state: ErrorBoundaryState = { hasError: false }

  static getDerivedStateFromError(): ErrorBoundaryState {
    return { hasError: true }
  }

  componentDidCatch(error: Error, info: ErrorInfo): void {
    reportError(error, {
      component_stack: info.componentStack,
      scope: 'react_error_boundary',
    })
  }

  render(): ReactNode {
    if (this.state.hasError) {
      return (
        this.props.fallback ?? (
          <div role="alert" className="flex min-h-screen flex-col items-center justify-center gap-4 p-8">
            <h1 className="text-2xl font-semibold">Something went wrong</h1>
            <p className="text-muted-foreground">
              The error has been reported. Reload the page to continue.
            </p>
            <button
              type="button"
              className="rounded-lg bg-black px-4 py-2 text-white"
              onClick={() => window.location.reload()}
            >
              Reload
            </button>
          </div>
        )
      )
    }
    return this.props.children
  }
}
