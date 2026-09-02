import { QueryClient, QueryClientProvider } from '@tanstack/react-query'
import { render, screen } from '@testing-library/react'
import { describe, expect, it, vi } from 'vitest'

import SubscriptionPage from '../page'
import { apiRequest } from '@/lib/api'

const { mockToast } = vi.hoisted(() => ({
  mockToast: vi.fn(),
}))

vi.mock('@/lib/api', () => ({ apiRequest: vi.fn() }))
vi.mock('@/components/ui/use-toast', () => ({
  useToast: () => ({ toast: mockToast, toasts: [] }),
}))

const mockedApiRequest = vi.mocked(apiRequest)

function renderPage() {
  const queryClient = new QueryClient({ defaultOptions: { queries: { retry: false } } })
  return render(
    <QueryClientProvider client={queryClient}>
      <SubscriptionPage />
    </QueryClientProvider>,
  )
}

describe('SubscriptionPage', () => {
  it('renders available subscription tiers', () => {
    mockedApiRequest.mockResolvedValueOnce(null)
    renderPage()

    expect(screen.getByText('Subscription')).toBeInTheDocument()
    expect(screen.getByText('Free')).toBeInTheDocument()
    expect(screen.getByText('Starter')).toBeInTheDocument()
    expect(screen.getByText('Pro')).toBeInTheDocument()
    expect(screen.getByText('Enterprise')).toBeInTheDocument()
  })

  it('renders active subscription details when present', async () => {
    mockedApiRequest.mockResolvedValueOnce({
      plan: 'pro',
      status: 'active',
      current_period_end: '2026-12-31T00:00:00.000Z',
      cancel_at_period_end: false,
    })

    renderPage()

    expect(await screen.findByText('Current Plan: pro')).toBeInTheDocument()
    expect(screen.getByText('Cancel Subscription')).toBeInTheDocument()
  })
})
