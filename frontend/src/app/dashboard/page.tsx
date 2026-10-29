'use client'

import Link from 'next/link'
import { useQuery } from '@tanstack/react-query'
import { Chart as ChartJS, CategoryScale, Legend, LinearScale, LineElement, PointElement, Title, Tooltip } from 'chart.js'
import { AlertCircle, BarChart3, Calculator, Leaf, Scale, Store } from 'lucide-react'
import { Line } from 'react-chartjs-2'

import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card'
import { EmptyState } from '@/components/ui/empty-state'
import { Skeleton } from '@/components/ui/skeleton'
import { apiRequest } from '@/lib/api'

ChartJS.register(CategoryScale, LinearScale, PointElement, LineElement, Title, Tooltip, Legend)

type DashboardStats = {
  active_batches: number
  upcoming_harvests?: number
  total_production_kg: number
  success_rate: number
  average_yield: number
  total_expenses_lkr?: number
  total_revenue_lkr?: number
  estimated_profit_lkr?: number
  outstanding_payments_lkr?: number
}

type EnvironmentPoint = { date: string; value: number }
type EnvironmentTrends = { temperature?: EnvironmentPoint[] }

function DashboardLoading() {
  return (
    <div className="space-y-8" aria-label="Loading dashboard">
      <div><Skeleton className="h-9 w-48" /><Skeleton className="mt-2 h-5 w-64" /></div>
      <div className="grid grid-cols-2 gap-6 md:grid-cols-4">
        {[1, 2, 3, 4].map((item) => <Card key={item}><CardContent className="pt-6"><Skeleton className="h-16" /></CardContent></Card>)}
      </div>
    </div>
  )
}

export default function DashboardPage() {
  const statsQuery = useQuery<DashboardStats>({
    queryKey: ['dashboard'],
    queryFn: () => apiRequest('/api/analytics/dashboard'),
  })
  const environmentQuery = useQuery<EnvironmentTrends>({
    queryKey: ['environment-trends'],
    queryFn: () => apiRequest('/api/analytics/environment'),
  })

  if (statsQuery.isLoading) return <DashboardLoading />

  if (statsQuery.isError) {
    return (
      <EmptyState
        icon={<AlertCircle className="h-12 w-12" />}
        title="Dashboard unavailable"
        description="We could not load the latest farm analytics. Check your connection and try again."
        actionLabel="Try again"
        onAction={() => statsQuery.refetch()}
      />
    )
  }

  if (!statsQuery.data) {
    return (
      <EmptyState
        icon={<BarChart3 className="h-12 w-12" />}
        title="No analytics yet"
        description="Dashboard metrics will appear after you create and track your first production batch."
      />
    )
  }

  const stats = statsQuery.data
  const temperatures = environmentQuery.data?.temperature ?? []
  const revenueLkr = stats.total_revenue_lkr ?? 0
  const expensesLkr = stats.total_expenses_lkr ?? 0
  const profitLkr = stats.estimated_profit_lkr ?? (revenueLkr - expensesLkr)
  const outstandingLkr = stats.outstanding_payments_lkr ?? 0

  return (
    <div className="space-y-8">
      <div className="flex flex-col gap-4 md:flex-row md:items-center md:justify-between">
        <div>
          <h1 className="text-3xl font-bold tracking-tight">Dashboard</h1>
          <p className="mt-1 text-muted-foreground">Oyster360 farm overview • Production, LKR costs &amp; profit</p>
        </div>

        {/* Mobile-friendly quick-entry buttons */}
        <div className="flex flex-wrap gap-2">
          <Link
            href="/harvests/new"
            className="inline-flex items-center gap-2 rounded-xl bg-emerald-700 px-4 py-2.5 text-sm font-semibold text-white hover:bg-emerald-800"
          >
            <Scale className="h-4 w-4" />
            + 60s Harvest Entry
          </Link>
          <Link
            href="/finance"
            className="inline-flex items-center gap-2 rounded-xl border bg-white px-4 py-2.5 text-sm font-medium hover:bg-gray-50"
          >
            <Calculator className="h-4 w-4" />
            + Expense (Rs.)
          </Link>
          <Link
            href="/sales"
            className="inline-flex items-center gap-2 rounded-xl border bg-white px-4 py-2.5 text-sm font-medium hover:bg-gray-50"
          >
            <Store className="h-4 w-4" />
            + Buyer Sale
          </Link>
          <Link
            href="/batches/new"
            className="inline-flex items-center gap-2 rounded-xl border bg-white px-4 py-2.5 text-sm font-medium hover:bg-gray-50"
          >
            <Leaf className="h-4 w-4" />
            + New Batch
          </Link>
        </div>
      </div>

      {/* Primary Cultivation KPIs */}
      <div className="grid grid-cols-2 gap-4 md:grid-cols-4">
        <MetricCard label="Active Batches" value={stats.active_batches} note="Currently in production" />
        <MetricCard label="Expected Harvest" value={`${stats.total_production_kg} kg`} note="Harvested weight" />
        <MetricCard label="Success Rate" value={`${stats.success_rate}%`} note="Completed batches" valueClassName="text-green-600" />
        <MetricCard label="Avg. Yield" value={`${stats.average_yield}g`} note="Per grow bag" />
      </div>

      {/* Sri Lankan Farm Profitability Summary (LKR) */}
      <div className="grid grid-cols-2 gap-4 md:grid-cols-4">
        <MetricCard
          label="Upcoming Harvests"
          value={`${stats.upcoming_harvests ?? stats.active_batches} batches`}
          note="Batches in fruiting / harvest"
        />
        <MetricCard
          label="Revenue (LKR)"
          value={`Rs. ${revenueLkr.toLocaleString()}`}
          note="From harvest & buyer sales"
        />
        <MetricCard
          label="Expenses (LKR)"
          value={`Rs. ${expensesLkr.toLocaleString()}`}
          note="Substrate, spawn, labour & utilities"
        />
        <MetricCard
          label="Estimated Profit (LKR)"
          value={`Rs. ${profitLkr.toLocaleString()}`}
          note={outstandingLkr > 0 ? `Rs. ${outstandingLkr.toLocaleString()} buyer balance due` : 'Net farm profit'}
          valueClassName={profitLkr >= 0 ? 'text-emerald-700' : 'text-red-600'}
        />
      </div>

      <div className="grid grid-cols-1 gap-6 lg:grid-cols-3">
        <Card className="lg:col-span-2">
          <CardHeader><CardTitle>Environmental Trends (Last 30 Days)</CardTitle></CardHeader>
          <CardContent>
            {environmentQuery.isError ? (
              <p className="flex h-80 items-center justify-center text-sm text-muted-foreground" role="status">
                Environmental readings are temporarily unavailable.
              </p>
            ) : temperatures.length === 0 ? (
              <p className="flex h-80 items-center justify-center text-sm text-muted-foreground" role="status">
                No temperature readings have been recorded.
              </p>
            ) : (
              <div className="h-80">
                <Line
                  data={{
                    labels: temperatures.map((point) => point.date),
                    datasets: [{
                      label: 'Temperature (°C)',
                      data: temperatures.map((point) => point.value),
                      borderColor: '#2563eb',
                      backgroundColor: 'rgba(37, 99, 235, 0.1)',
                      tension: 0.3,
                      borderWidth: 2,
                    }],
                  }}
                  options={{ responsive: true, maintainAspectRatio: false, plugins: { legend: { display: true } } }}
                />
              </div>
            )}
          </CardContent>
        </Card>

        <Card>
          <CardHeader><CardTitle>Current Production Status</CardTitle></CardHeader>
          <CardContent className="space-y-4">
            <p className="text-sm text-muted-foreground">
              Detailed stage distribution, grow-bag contamination counts, and daily tasks are available from the Batches page.
            </p>
            <div className="space-y-2 pt-2 text-sm">
              <Link href="/batches" className="block rounded-lg border p-3 hover:bg-muted/50">
                <div className="font-medium">Manage Grow-Bag Batches →</div>
                <div className="text-xs text-muted-foreground">Prepared, inoculated, contaminated &amp; harvested bags</div>
              </Link>
              <Link href="/finance" className="block rounded-lg border p-3 hover:bg-muted/50">
                <div className="font-medium">Open LKR Profit Calculator →</div>
                <div className="text-xs text-muted-foreground">Cost per bag, cost per kg &amp; batch net profit</div>
              </Link>
              <Link href="/sales" className="block rounded-lg border p-3 hover:bg-muted/50">
                <div className="font-medium">Buyer Sales &amp; Payments →</div>
                <div className="text-xs text-muted-foreground">Track retail/wholesale orders &amp; unpaid balances</div>
              </Link>
            </div>
          </CardContent>
        </Card>
      </div>
    </div>
  )
}

function MetricCard({ label, value, note, valueClassName = '' }: {
  label: string
  value: string | number
  note: string
  valueClassName?: string
}) {
  return (
    <Card>
      <CardHeader className="pb-2"><CardTitle className="text-sm font-medium text-muted-foreground">{label}</CardTitle></CardHeader>
      <CardContent>
        <div className={`text-2xl md:text-3xl font-bold ${valueClassName}`}>{value}</div>
        <p className="mt-1 text-xs text-muted-foreground">{note}</p>
      </CardContent>
    </Card>
  )
}
