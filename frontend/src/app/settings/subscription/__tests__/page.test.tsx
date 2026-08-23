import { QueryClient, QueryClientProvider } from '@tanstack/react-query'
import { fireEvent, render, screen, waitFor } from '@testing-library/react'
import { beforeEach, describe, expect, it, vi } from 'vitest'

import SubscriptionPage from '../page'
import { apiRequest } from '@/lib/api'

const { mockToast } = vi.hoisted(() => ({ mockToast: vi.fn() }))

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
  beforeEach(() => {
    mockedApiRequest.mockReset()
    mockToast.mockReset()
    // No active subscription by default; tests opt in per case.
    mockedApiRequest.mockResolvedValue(undefined)
  })

  it('fetches the current subscription on load', async () => {
    renderPage()

    await waitFor(() =>
      expect(mockedApiRequest).toHaveBeenCalledWith('/api/billing/subscription'),
    )
  })

  it('lists all purchasable plans with pricing', () => {
    renderPage()

    expect(screen.getByText('Free')).toBeInTheDocument()
    expect(screen.getByText('Starter')).toBeInTheDocument()
    expect(screen.getByText('Pro')).toBeInTheDocument()
    expect(screen.getByText('Enterprise')).toBeInTheDocument()
    expect(screen.getByText('$0')).toBeInTheDocument()
    expect(screen.getByText('$29')).toBeInTheDocument()
    expect(screen.getByText('$99')).toBeInTheDocument()
    expect(screen.getByText('$299')).toBeInTheDocument()
  })

  it('shows the current plan card and disables its upgrade button', async () => {
    mockedApiRequest.mockImplementation((endpoint: string) =>
      endpoint === '/api/billing/subscription'
        ? Promise.resolve({
            plan: 'starter',
            status: 'active',
            current_period_end: '2026-09-01T00:00:00Z',
            cancel_at_period_end: false,
          })
        : Promise.resolve({}),
    )
    renderPage()

    expect(
      await screen.findByRole('heading', { name: /Current Plan: starter/ }),
    ).toBeInTheDocument()
    const currentPlanButton = screen.getByRole('button', { name: 'Current Plan' })
    expect(currentPlanButton).toBeDisabled()
    expect(screen.getAllByRole('button', { name: 'Upgrade' }).length).toBeGreaterThan(0)
  })

  it('starts checkout when upgrading plans', async () => {
    const urlSetter = vi.fn()
    Object.defineProperty(window, 'location', {
      value: { ...window.location, set href(v: string) { urlSetter(v) } },
      writable: true,
    })
    mockedApiRequest.mockImplementation((endpoint: string) =>
      endpoint === '/api/billing/create-checkout-session'
        ? Promise.resolve({ checkout_url: 'https://checkout.stripe.test/pay' })
        : Promise.resolve(null),
    )
    renderPage()

    const upgradeButtons = await screen.findAllByRole('button', { name: 'Upgrade' })
    fireEvent.click(upgradeButtons[0])

    await waitFor(() =>
      expect(mockedApiRequest).toHaveBeenCalledWith(
        '/api/billing/create-checkout-session',
        expect.objectContaining({ method: 'POST' }),
      ),
    )
    await waitFor(() => expect(urlSetter).toHaveBeenCalledWith('https://checkout.stripe.test/pay'))
  })

  it('shows an error toast when checkout fails', async () => {
    mockedApiRequest.mockImplementation((endpoint: string) =>
      endpoint === '/api/billing/create-checkout-session'
        ? Promise.reject(new Error('stripe down'))
        : Promise.resolve(null),
    )
    renderPage()

    const upgradeButtons = await screen.findAllByRole('button', { name: 'Upgrade' })
    fireEvent.click(upgradeButtons[0])

    await waitFor(() =>
      expect(mockToast).toHaveBeenCalledWith(
        expect.objectContaining({ title: 'Failed to start checkout', variant: 'error' }),
      ),
    )
  })
})
