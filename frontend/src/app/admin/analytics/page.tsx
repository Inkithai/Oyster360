'use client'

import { useQuery } from '@tanstack/react-query'
import { apiRequest } from '@/lib/api'
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card'

export default function AdminAnalytics() {
  const { data: growth } = useQuery({
    queryKey: ['saas-growth'],
    queryFn: () => apiRequest('/api/saas-analytics/growth'),
  })

  const { data: revenue } = useQuery({
    queryKey: ['saas-revenue'],
    queryFn: () => apiRequest('/api/saas-analytics/revenue'),
  })

  const { data: retention } = useQuery({
    queryKey: ['saas-retention'],
    queryFn: () => apiRequest('/api/saas-analytics/retention'),
  })

  return (
    <div className="space-y-8">
      <div>
        <h1 className="text-3xl font-semibold tracking-tight">SaaS Analytics</h1>
        <p className="text-muted-foreground">Business intelligence and growth metrics</p>
      </div>

      <div className="grid grid-cols-2 md:grid-cols-4 gap-6">
        <Card>
          <CardHeader>
            <CardTitle>New Users (30 days)</CardTitle>
          </CardHeader>
          <CardContent>
            <div className="text-4xl font-bold">{growth?.new_users || 0}</div>
          </CardContent>
        </Card>

        <Card>
          <CardHeader>
            <CardTitle>Monthly Recurring Revenue</CardTitle>
          </CardHeader>
          <CardContent>
            <div className="text-4xl font-bold">${revenue?.monthly_recurring_revenue || 0}</div>
          </CardContent>
        </Card>

        <Card>
          <CardHeader>
            <CardTitle>Active Subscriptions</CardTitle>
          </CardHeader>
          <CardContent>
            <div className="text-4xl font-bold">{revenue?.active_subscriptions || 0}</div>
          </CardContent>
        </Card>

        <Card>
          <CardHeader>
            <CardTitle>Retention Rate</CardTitle>
          </CardHeader>
          <CardContent>
            <div className="text-4xl font-bold">{retention?.retention_rate || 0}%</div>
          </CardContent>
        </Card>
      </div>
    </div>
  )
}