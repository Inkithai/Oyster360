import { QueryClient, QueryClientProvider } from '@tanstack/react-query'
import { render, screen, waitFor, within } from '@testing-library/react'
import { beforeEach, describe, expect, it, vi } from 'vitest'

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
  beforeEach(() => {
    mockedApiRequest.mockReset()
  })

  it('loads strains from the tenant-scoped API', async () => {
    mockedApiRequest.mockResolvedValueOnce([])
    renderPage()

    await waitFor(() => expect(mockedApiRequest).toHaveBeenCalledWith('/api/strains'))
  })

  it('renders the strain catalogue with cultivation metadata', async () => {
    mockedApiRequest.mockResolvedValueOnce([
      {
        id: 1,
        name: 'Grey Oyster',
        species: 'Pleurotus ostreatus',
        difficulty: 'Easy',
        colonization_days: 14,
        fruiting_days: 7,
      },
      {
        id: 2,
        name: 'Golden Oyster',
        species: 'Pleurotus citrinopileatus',
        difficulty: 'Moderate',
        colonization_days: 18,
        fruiting_days: 9,
      },
    ])
    renderPage()

    const table = await screen.findByRole('table')
    const rows = within(table).getAllByRole('row')
    expect(rows).toHaveLength(3) // header + 2 strains
    expect(within(table).getByText('Grey Oyster')).toBeInTheDocument()
    expect(within(table).getByText('Golden Oyster')).toBeInTheDocument()
    expect(within(table).getByText('Pleurotus ostreatus')).toBeInTheDocument()
    expect(screen.getByText('Oyster Mushroom Strains')).toBeInTheDocument()
  })
})
