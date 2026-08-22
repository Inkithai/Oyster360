import { QueryClient, QueryClientProvider } from '@tanstack/react-query'
import { render, screen, waitFor } from '@testing-library/react'
import { beforeEach, describe, expect, it, vi } from 'vitest'

import DashboardPage from '../page'
import { apiRequest } from '@/lib/api'

vi.mock('@/lib/api', () => ({ apiRequest: vi.fn() }))
vi.mock('react-chartjs-2', () => ({ Line: () => <div data-testid="temperature-chart" /> }))
vi.mock('chart.js', () => ({
  Chart: { register: vi.fn() },
  CategoryScale: {}, LinearScale: {}, PointElement: {}, LineElement: {}, Title: {}, Tooltip: {}, Legend: {},
}))

const mockedApiRequest = vi.mocked(apiRequest)

function renderDashboard() {
  const queryClient = new QueryClient({ defaultOptions: { queries: { retry: false } } })
  return render(
    <QueryClientProvider client={queryClient}>
      <DashboardPage />
    </QueryClientProvider>,
  )
}

describe('DashboardPage', () => {
  beforeEach(() => mockedApiRequest.mockReset())

  it('renders API metrics, including legitimate zero values, without demo fallbacks', async () => {
    mockedApiRequest
      .mockResolvedValueOnce({ active_batches: 0, total_production_kg: 125, success_rate: 92, average_yield: 810 })
      .mockResolvedValueOnce({ temperature: [{ date: '2026-08-22', value: 24 }] })

    renderDashboard()

    expect(await screen.findByText('125 kg')).toBeInTheDocument()
    expect(screen.getByText('0')).toBeInTheDocument()
    expect(screen.getByText('92%')).toBeInTheDocument()
    expect(screen.getByText('810g')).toBeInTheDocument()
    expect(screen.getByTestId('temperature-chart')).toBeInTheDocument()
    expect(screen.queryByText('485 kg')).not.toBeInTheDocument()
  })

  it('shows an actionable error state when dashboard analytics fail', async () => {
    mockedApiRequest
      .mockRejectedValueOnce(new Error('network unavailable'))
      .mockResolvedValueOnce({ temperature: [] })
    renderDashboard()

    expect(await screen.findByText('Dashboard unavailable')).toBeInTheDocument()
    expect(screen.getByRole('button', { name: 'Try again' })).toBeInTheDocument()
  })

  it('shows a specific environmental error without hiding valid KPIs', async () => {
    mockedApiRequest
      .mockResolvedValueOnce({ active_batches: 2, total_production_kg: 20, success_rate: 80, average_yield: 600 })
      .mockRejectedValueOnce(new Error('sensor API unavailable'))
    renderDashboard()

    await waitFor(() => expect(screen.getByText('2')).toBeInTheDocument())
    expect(await screen.findByText('Environmental readings are temporarily unavailable.')).toBeInTheDocument()
  })
})
