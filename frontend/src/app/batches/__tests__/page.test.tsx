import { QueryClient, QueryClientProvider } from '@tanstack/react-query'
import { render, screen } from '@testing-library/react'
import { describe, expect, it, vi } from 'vitest'

import BatchesPage from '../page'
import { apiRequest } from '@/lib/api'

vi.mock('@/lib/api', () => ({ apiRequest: vi.fn() }))

const mockedApiRequest = vi.mocked(apiRequest)

function renderPage() {
  const queryClient = new QueryClient({ defaultOptions: { queries: { retry: false } } })
  return render(
    <QueryClientProvider client={queryClient}>
      <BatchesPage />
    </QueryClientProvider>,
  )
}

describe('BatchesPage', () => {
  it('renders batches returned by the API with formatted dates and stage badges', async () => {
    mockedApiRequest.mockResolvedValueOnce([
      {
        batch_number: 'B-2026-001',
        current_stage: 'FRUITING',
        status: 'active',
        start_date: '2026-08-01T00:00:00.000Z',
      },
    ])

    renderPage()

    expect(await screen.findByText('B-2026-001')).toBeInTheDocument()
    expect(screen.getByText('FRUITING')).toBeInTheDocument()
    expect(screen.getByText('active')).toBeInTheDocument()
    expect(screen.getByRole('columnheader', { name: /start date/i })).toBeInTheDocument()
  })

  it('shows the table empty state when there are no batches', async () => {
    mockedApiRequest.mockResolvedValueOnce([])

    renderPage()

    expect(await screen.findByText('No results found.')).toBeInTheDocument()
  })
})
