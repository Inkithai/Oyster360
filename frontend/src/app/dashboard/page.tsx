'use client'

import { useQuery } from '@tanstack/react-query'
import { apiRequest } from '@/lib/api'
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card'
import { Skeleton } from '@/components/ui/skeleton'
import { 
  Chart as ChartJS,
  CategoryScale,
  LinearScale,
  PointElement,
  LineElement,
  Title,
  Tooltip,
  Legend,
} from 'chart.js'
import { Line } from 'react-chartjs-2'

ChartJS.register(
  CategoryScale,
  LinearScale,
  PointElement,
  LineElement,
  Title,
  Tooltip,
  Legend
)

export default function DashboardPage() {
  const { data: stats, isLoading } = useQuery({
    queryKey: ['dashboard'],
    queryFn: () => apiRequest('/api/analytics/dashboard'),
  })

  const { data: environment } = useQuery({
    queryKey: ['environment-trends'],
    queryFn: () => apiRequest('/api/analytics/environment'),
  })

  if (isLoading) {
    return (
      <div className="space-y-8">
        <div>
          <Skeleton className="h-9 w-48" />
          <Skeleton className="h-5 w-64 mt-2" />
        </div>
        
        <div className="grid grid-cols-2 md:grid-cols-4 gap-6">
          {[1,2,3,4].map(i => (
            <Card key={i}>
              <CardContent className="pt-6">
                <Skeleton className="h-16" />
              </CardContent>
            </Card>
          ))}
        </div>
      </div>
    )
  }

  return (
    <div className="space-y-8">
      <div>
        <h1 className="text-3xl font-bold tracking-tight">Dashboard</h1>
        <p className="text-muted-foreground mt-1">Oyster360 • Bim Mal Oyster Farm Demo</p>
      </div>

      {/* KPI Cards */}
      <div className="grid grid-cols-2 md:grid-cols-4 gap-6">
        <Card>
          <CardHeader className="pb-2">
            <CardTitle className="text-sm font-medium text-muted-foreground">Active Batches</CardTitle>
          </CardHeader>
          <CardContent>
            <div className="text-4xl font-bold">{stats?.active_batches || 18}</div>
            <p className="text-xs text-green-600 mt-1">+3 this week</p>
          </CardContent>
        </Card>

        <Card>
          <CardHeader className="pb-2">
            <CardTitle className="text-sm font-medium text-muted-foreground">Expected Harvest</CardTitle>
          </CardHeader>
          <CardContent>
            <div className="text-4xl font-bold">{stats?.total_production_kg || 485} kg</div>
            <p className="text-xs text-muted-foreground mt-1">This month</p>
          </CardContent>
        </Card>

        <Card>
          <CardHeader className="pb-2">
            <CardTitle className="text-sm font-medium text-muted-foreground">Success Rate</CardTitle>
          </CardHeader>
          <CardContent>
            <div className="text-4xl font-bold text-green-600">{stats?.success_rate || 91}%</div>
            <p className="text-xs text-muted-foreground mt-1">Last 90 days</p>
          </CardContent>
        </Card>

        <Card>
          <CardHeader className="pb-2">
            <CardTitle className="text-sm font-medium text-muted-foreground">Avg. Yield</CardTitle>
          </CardHeader>
          <CardContent>
            <div className="text-4xl font-bold">{stats?.average_yield || 785}g</div>
            <p className="text-xs text-green-600 mt-1">+12g vs last month</p>
          </CardContent>
        </Card>
      </div>

      <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
        {/* Environmental Trends */}
        <Card className="lg:col-span-2">
          <CardHeader>
            <CardTitle>Environmental Trends (Last 30 Days)</CardTitle>
          </CardHeader>
          <CardContent>
            <div className="h-80">
              <Line 
                data={{
                  labels: environment?.temperature?.map((d: any) => d.date) || [],
                  datasets: [{
                    label: 'Temperature (°C)',
                    data: environment?.temperature?.map((d: any) => d.value) || [],
                    borderColor: '#2563eb',
                    backgroundColor: 'rgba(37, 99, 235, 0.1)',
                    tension: 0.3,
                    borderWidth: 2
                  }]
                }}
                options={{
                  responsive: true,
                  maintainAspectRatio: false,
                  plugins: { legend: { display: true } },
                  scales: {
                    y: {
                      grid: { color: '#f1f5f9' }
                    }
                  }
                }}
              />
            </div>
          </CardContent>
        </Card>

        {/* Current Production Status */}
        <Card>
          <CardHeader>
            <CardTitle>Current Production Status</CardTitle>
          </CardHeader>
          <CardContent className="space-y-6">
            <div>
              <div className="flex justify-between text-sm mb-1.5">
                <span>Colonization</span>
                <span className="font-medium">920 bags</span>
              </div>
              <div className="h-2 bg-muted rounded-full overflow-hidden">
                <div className="h-2 w-[46%] bg-blue-600 rounded-full" />
              </div>
            </div>
            <div>
              <div className="flex justify-between text-sm mb-1.5">
                <span>Fruiting</span>
                <span className="font-medium">680 bags</span>
              </div>
              <div className="h-2 bg-muted rounded-full overflow-hidden">
                <div className="h-2 w-[34%] bg-emerald-600 rounded-full" />
              </div>
            </div>
            <div>
              <div className="flex justify-between text-sm mb-1.5">
                <span>Ready for Harvest</span>
                <span className="font-medium">240 bags</span>
              </div>
              <div className="h-2 bg-muted rounded-full overflow-hidden">
                <div className="h-2 w-[12%] bg-amber-600 rounded-full" />
              </div>
            </div>
          </CardContent>
        </Card>
      </div>

      {/* Quick Insights */}
      <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
        <Card>
          <CardHeader>
            <CardTitle>Top Performing Strain</CardTitle>
          </CardHeader>
          <CardContent>
            <div className="text-2xl font-semibold">Pearl Oyster</div>
            <p className="text-sm text-muted-foreground mt-1">820g avg yield • 93% success</p>
          </CardContent>
        </Card>

        <Card>
          <CardHeader>
            <CardTitle>Best Recipe</CardTitle>
          </CardHeader>
          <CardContent>
            <div className="text-2xl font-semibold">Rice Straw V2</div>
            <p className="text-sm text-muted-foreground mt-1">+18% yield vs V1</p>
          </CardContent>
        </Card>

        <Card>
          <CardHeader>
            <CardTitle>Recent AI Inspections</CardTitle>
          </CardHeader>
          <CardContent>
            <div className="text-sm">12 inspections this week • 2 flagged</div>
          </CardContent>
        </Card>
      </div>
    </div>
  )
}