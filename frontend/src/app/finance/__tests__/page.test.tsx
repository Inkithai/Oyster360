import { QueryClient, QueryClientProvider } from '@tanstack/react-query'
import { render, screen } from '@testing-library/react'
import { describe, expect, it, vi } from 'vitest'

import FinancePage from '../page'
import { ToastProvider } from '@/components/ui/use-toast'
import { apiRequest } from '@/lib/api'

vi.mock('@/lib/api', () => ({ apiRequest: vi.fn() }))

const mockedApiRequest = vi.mocked(apiRequest)

function renderPage() {
  const queryClient = new QueryClient({ defaultOptions: { queries: { retry: false } } })
  return render(
    <QueryClientProvider client={queryClient}>
      <ToastProvider>
        <FinancePage />
      </ToastProvider>
    </QueryClientProvider>,
  )
}

describe('FinancePage', () => {
  it('renders LKR profitability metrics and batch profitability table', async () => {
    mockedApiRequest.mockImplementation(async (endpoint: string) => {
      if (endpoint.includes('/api/finance/profitability')) {
        return {
          currency: 'LKR',
          total_expenses_lkr: 42500,
          total_revenue_lkr: 97500,
          gross_profit_lkr: 55000,
          estimated_net_profit_lkr: 55000,
          cost_per_bag_lkr: 42.5,
          cost_per_kg_lkr: 283.33,
          profit_per_kg_lkr: 366.67,
          profit_margin_pct: 56.4,
          total_harvested_kg: 150,
          expected_yield_kg: 300,
          yield_efficiency_pct: 50,
          batch_profitability: [
            {
              batch_id: 1,
              batch_number: 'OY-2026-001',
              bags_prepared: 1000,
              expected_yield_kg: 300,
              actual_yield_kg: 150,
              cost_per_bag_lkr: 42.5,
              total_cost_lkr: 42500,
              revenue_lkr: 97500,
              net_profit_lkr: 55000,
            },
          ],
        }
      }
      return [
        {
          id: 1,
          category: 'SUBSTRATE',
          description: 'Rubber sawdust and rice bran',
          amount_lkr: 18500,
          expense_date: '2026-10-01T00:00:00.000Z',
        },
      ]
    })

    renderPage()

    expect(await screen.findByText('Profit & Cost Calculator (LKR)')).toBeInTheDocument()
    expect(await screen.findByText('OY-2026-001')).toBeInTheDocument()
    expect(await screen.findByText('Rubber sawdust and rice bran')).toBeInTheDocument()
  })
})
