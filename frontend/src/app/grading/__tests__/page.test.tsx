import { QueryClient, QueryClientProvider } from '@tanstack/react-query'
import { render, screen } from '@testing-library/react'
import { describe, expect, it, vi } from 'vitest'

import GradingPage from '../page'
import { apiRequest } from '@/lib/api'

vi.mock('@/lib/api', () => ({ apiRequest: vi.fn() }))
const mockedApiRequest = vi.mocked(apiRequest)

function renderPage() {
  const queryClient = new QueryClient({ defaultOptions: { queries: { retry: false } } })
  return render(
    <QueryClientProvider client={queryClient}>
      <GradingPage />
    </QueryClientProvider>,
  )
}

describe('GradingPage', () => {
  it('renders harvest grading table with data', async () => {
    mockedApiRequest.mockResolvedValueOnce([
      {
        id: 1,
        grade: 'A',
        quantity_kg: 50,
        price_per_kg: 200,
      },
    ])

    renderPage()

    expect(await screen.findByText('A')).toBeInTheDocument()
    expect(screen.getByText('50')).toBeInTheDocument()
    expect(screen.getByText('200')).toBeInTheDocument()
    expect(screen.getByText('10000')).toBeInTheDocument()
  })

  it('renders empty state when no grade records', async () => {
    mockedApiRequest.mockResolvedValueOnce([])
    renderPage()
    expect(await screen.findByText('No results found.')).toBeInTheDocument()
  })
})
