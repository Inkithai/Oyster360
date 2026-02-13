'use client'

import { useQuery } from '@tanstack/react-query'
import { Chart as ChartJS, CategoryScale, Legend, LinearScale, LineElement, PointElement, Title, Tooltip } from 'chart.js'
import { AlertCircle, BarChart3 } from 'lucide-react'
import { Line } from 'react-chartjs-2'

import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card'
import { EmptyState } from '@/components/ui/empty-state'
import { Skeleton } from '@/components/ui/skeleton'
import { apiRequest } from '@/lib/api'

ChartJS.register(CategoryScale, LinearScale, PointElement, LineElement, Title, Tooltip, Legend)

type DashboardStats = {
  active_batches: number
  total_production_kg: number
  success_rate: number
  average_yield: number
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

  return (
    <div className="space-y-8">
      <div>
        <h1 className="text-3xl font-bold tracking-tight">Dashboard</h1>
        <p className="mt-1 text-muted-foreground">Oyster360 farm overview</p>
      </div>

      <div className="grid grid-cols-2 gap-6 md:grid-cols-4">
        <MetricCard label="Active Batches" value={stats.active_batches} note="Currently in production" />
        <MetricCard label="Expected Harvest" value={`${stats.total_production_kg} kg`} note="This month" />
        <MetricCard label="Success Rate" value={`${stats.success_rate}%`} note="Last 90 days" valueClassName="text-green-600" />
        <MetricCard label="Avg. Yield" value={`${stats.average_yield}g`} note="Per grow bag" />
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
          <CardContent>
            <p className="text-sm text-muted-foreground">
              Detailed stage distribution is available from the Batches page.
            </p>
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
        <div className={`text-4xl font-bold ${valueClassName}`}>{value}</div>
        <p className="mt-1 text-xs text-muted-foreground">{note}</p>
      </CardContent>
    </Card>
  )
}
