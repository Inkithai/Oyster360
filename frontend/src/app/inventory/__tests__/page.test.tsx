import { QueryClient, QueryClientProvider } from '@tanstack/react-query'
import { render, screen } from '@testing-library/react'
import { describe, expect, it, vi } from 'vitest'

import InventoryPage from '../page'
import { apiRequest } from '@/lib/api'

vi.mock('@/lib/api', () => ({ apiRequest: vi.fn() }))

const mockedApiRequest = vi.mocked(apiRequest)

function renderPage() {
  const queryClient = new QueryClient({ defaultOptions: { queries: { retry: false } } })
  return render(
    <QueryClientProvider client={queryClient}>
      <InventoryPage />
    </QueryClientProvider>,
  )
}

describe('InventoryPage', () => {
  it('renders inventory items and highlights stock at its reorder level', async () => {
    mockedApiRequest.mockResolvedValueOnce([
      { name: 'Hardwood pellets', category: 'substrate', current_stock: 10, unit: 'kg', reorder_level: 10 },
    ])

    renderPage()

    expect(await screen.findByText('Hardwood pellets')).toBeInTheDocument()
    expect(screen.getByText('substrate')).toBeInTheDocument()
    expect(screen.getByText('kg')).toBeInTheDocument()
    expect(screen.getByText('10', { selector: 'span' })).toHaveClass('text-orange-600')
  })

  it('does not mark healthy stock as needing a reorder', async () => {
    mockedApiRequest.mockResolvedValueOnce([
      { name: 'Gloves', category: 'supplies', current_stock: 20, unit: 'boxes', reorder_level: 5 },
    ])

    renderPage()

    const reorderLevel = await screen.findByText('5', { selector: 'span' })
    expect(reorderLevel).not.toHaveClass('text-orange-600')
  })
})
