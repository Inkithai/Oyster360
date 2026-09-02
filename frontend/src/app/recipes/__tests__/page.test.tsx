import { QueryClient, QueryClientProvider } from '@tanstack/react-query'
import { render, screen } from '@testing-library/react'
import { describe, expect, it, vi } from 'vitest'

import RecipesPage from '../page'
import { apiRequest } from '@/lib/api'

vi.mock('@/lib/api', () => ({ apiRequest: vi.fn() }))
const mockedApiRequest = vi.mocked(apiRequest)

function renderPage() {
  const queryClient = new QueryClient({ defaultOptions: { queries: { retry: false } } })
  return render(
    <QueryClientProvider client={queryClient}>
      <RecipesPage />
    </QueryClientProvider>,
  )
}

describe('RecipesPage', () => {
  it('renders recipes list returned by the API', async () => {
    mockedApiRequest.mockResolvedValueOnce([
      {
        id: 1,
        name: "Master's Mix",
        description: 'Hardwood and soybean hulls substrate',
        success_rate: '94',
      },
    ])

    renderPage()

    expect(await screen.findByText("Master's Mix")).toBeInTheDocument()
    expect(screen.getByText('Hardwood and soybean hulls substrate')).toBeInTheDocument()
    expect(screen.getByText('94%')).toBeInTheDocument()
  })

  it('renders empty state when no recipes exist', async () => {
    mockedApiRequest.mockResolvedValueOnce([])
    renderPage()
    expect(await screen.findByText('No results found.')).toBeInTheDocument()
  })
})
