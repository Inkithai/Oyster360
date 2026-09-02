import { QueryClient, QueryClientProvider } from '@tanstack/react-query'
import { render, screen } from '@testing-library/react'
import { describe, expect, it, vi } from 'vitest'

import AdminDashboard from '../page'
import { apiRequest } from '@/lib/api'

vi.mock('@/lib/api', () => ({ apiRequest: vi.fn() }))
const mockedApiRequest = vi.mocked(apiRequest)

function renderPage() {
  const queryClient = new QueryClient({ defaultOptions: { queries: { retry: false } } })
  return render(
    <QueryClientProvider client={queryClient}>
      <AdminDashboard />
    </QueryClientProvider>,
  )
}

describe('AdminDashboard', () => {
  it('renders system stats for administrators', async () => {
    mockedApiRequest.mockResolvedValueOnce({
      total_users: 142,
      total_organizations: 28,
      total_subscriptions: 24,
      active_subscriptions: 21,
    })

    renderPage()

    expect(screen.getByText('Admin Dashboard')).toBeInTheDocument()
    expect(await screen.findByText('142')).toBeInTheDocument()
    expect(screen.getByText('28')).toBeInTheDocument()
    expect(screen.getByText('24')).toBeInTheDocument()
    expect(screen.getByText('21')).toBeInTheDocument()
  })
})
