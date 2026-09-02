import { QueryClient, QueryClientProvider } from '@tanstack/react-query'
import { render, screen } from '@testing-library/react'
import { describe, expect, it, vi } from 'vitest'

import HarvestsPage from '../page'
import { apiRequest } from '@/lib/api'

vi.mock('@/lib/api', () => ({ apiRequest: vi.fn() }))
const mockedApiRequest = vi.mocked(apiRequest)

function renderPage() {
  const queryClient = new QueryClient({ defaultOptions: { queries: { retry: false } } })
  return render(
    <QueryClientProvider client={queryClient}>
      <HarvestsPage />
    </QueryClientProvider>,
  )
}

describe('HarvestsPage', () => {
  it('renders harvest records returned by API', async () => {
    mockedApiRequest.mockResolvedValueOnce([
      {
        id: 1,
        batch_id: 'BATCH-001',
        quantity_kg: 24.5,
        quality_score: 95,
        selling_price: 14.0,
        harvest_date: '2026-08-15T12:00:00.000Z',
      },
    ])

    renderPage()

    expect(await screen.findByText('BATCH-001')).toBeInTheDocument()
    expect(screen.getByText('24.5')).toBeInTheDocument()
    expect(screen.getByText('95')).toBeInTheDocument()
  })

  it('renders empty table when no harvests exist', async () => {
    mockedApiRequest.mockResolvedValueOnce([])
    renderPage()
    expect(await screen.findByText('No results found.')).toBeInTheDocument()
  })
})
