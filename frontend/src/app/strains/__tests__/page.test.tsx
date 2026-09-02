import { QueryClient, QueryClientProvider } from '@tanstack/react-query'
import { render, screen } from '@testing-library/react'
import { describe, expect, it, vi } from 'vitest'

import StrainsPage from '../page'
import { apiRequest } from '@/lib/api'

vi.mock('@/lib/api', () => ({ apiRequest: vi.fn() }))
const mockedApiRequest = vi.mocked(apiRequest)

function renderPage() {
  const queryClient = new QueryClient({ defaultOptions: { queries: { retry: false } } })
  return render(
    <QueryClientProvider client={queryClient}>
      <StrainsPage />
    </QueryClientProvider>,
  )
}

describe('StrainsPage', () => {
  it('renders strain list returned by the API', async () => {
    mockedApiRequest.mockResolvedValueOnce([
      {
        id: 1,
        name: 'Pearl Oyster',
        species: 'Pleurotus ostreatus',
        difficulty: 'EASY',
        colonization_days: 14,
        fruiting_days: 7,
      },
      {
        id: 2,
        name: 'Golden Oyster',
        species: 'Pleurotus citrinopileatus',
        difficulty: 'MEDIUM',
        colonization_days: 16,
        fruiting_days: 8,
      },
    ])

    renderPage()

    expect(await screen.findByText('Pearl Oyster')).toBeInTheDocument()
    expect(screen.getByText('Golden Oyster')).toBeInTheDocument()
    expect(screen.getByText('Pleurotus ostreatus')).toBeInTheDocument()
  })

  it('handles empty strain list', async () => {
    mockedApiRequest.mockResolvedValueOnce([])
    renderPage()
    expect(await screen.findByText('No results found.')).toBeInTheDocument()
  })
})
