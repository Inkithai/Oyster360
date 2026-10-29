import { QueryClient, QueryClientProvider } from '@tanstack/react-query'
import { render, screen } from '@testing-library/react'
import { describe, expect, it, vi } from 'vitest'

import SalesPage from '../page'
import { ToastProvider } from '@/components/ui/use-toast'
import { apiRequest } from '@/lib/api'

vi.mock('@/lib/api', () => ({ apiRequest: vi.fn() }))

const mockedApiRequest = vi.mocked(apiRequest)

function renderPage() {
  const queryClient = new QueryClient({ defaultOptions: { queries: { retry: false } } })
  return render(
    <QueryClientProvider client={queryClient}>
      <ToastProvider>
        <SalesPage />
      </ToastProvider>
    </QueryClientProvider>,
  )
}

describe('SalesPage', () => {
  it('renders sellable stock summary, buyers, and sales orders', async () => {
    mockedApiRequest.mockImplementation(async (endpoint: string) => {
      if (endpoint.includes('/api/sales/stock-summary')) {
        return {
          total_harvested_kg: 80,
          total_sold_kg: 55,
          total_spoiled_kg: 3,
          available_for_sale_kg: 22,
          total_sales_lkr: 35750,
          outstanding_balance_lkr: 6500,
        }
      }
      if (endpoint.includes('/api/sales/buyers')) {
        return [
          {
            id: 1,
            name: 'Keells Super — Maharagama',
            buyer_type: 'RETAILER',
            phone: '077-1234567',
            location: 'Maharagama',
            order_count: 3,
            total_purchased_kg: 55,
            outstanding_balance_lkr: 6500,
          },
        ]
      }
      return [
        {
          id: 1,
          buyer_id: 1,
          buyer_name: 'Keells Super — Maharagama',
          quantity_kg: 20,
          price_per_kg_lkr: 650,
          total_amount_lkr: 13000,
          amount_paid_lkr: 6500,
          balance_due_lkr: 6500,
          payment_status: 'PARTIAL',
        },
      ]
    })

    renderPage()

    expect(await screen.findByText('Harvest Sales & Buyer Management')).toBeInTheDocument()
    expect(await screen.findByText('22 kg')).toBeInTheDocument()
    expect(await screen.findByText('PARTIAL')).toBeInTheDocument()
  })
})
