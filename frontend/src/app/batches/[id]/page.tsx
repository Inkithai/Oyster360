'use client'

import { useParams } from 'next/navigation'
import { useQuery } from '@tanstack/react-query'
import { apiRequest } from '@/lib/api'
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card'

export default function BatchDetailPage() {
  const params = useParams()
  const batchId = params.id as string

  const { data: batch } = useQuery({
    queryKey: ['batch', batchId],
    queryFn: () => apiRequest(`/api/batches/${batchId}`),
  })

  return (
    <div className="max-w-5xl mx-auto space-y-8">
      <div>
        <h1 className="text-3xl font-semibold tracking-tight">Batch #{batchId}</h1>
        <p className="text-muted-foreground">Detailed view and AI insights</p>
      </div>

      <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
        <Card>
          <CardHeader><CardTitle>Batch Information</CardTitle></CardHeader>
          <CardContent>
            <div className="space-y-2 text-sm">
              <div>Status: <span className="font-medium">{batch?.status || 'Active'}</span></div>
              <div>Stage: <span className="font-medium">{batch?.current_stage || 'In Progress'}</span></div>
            </div>
          </CardContent>
        </Card>

        <Card>
          <CardHeader><CardTitle>Timeline</CardTitle></CardHeader>
          <CardContent>
            <div className="text-sm space-y-1">
              <div>Preparation → Inoculation → Colonization → Fruiting → Harvest</div>
            </div>
          </CardContent>
        </Card>

        <Card>
          <CardHeader><CardTitle>AI Insights</CardTitle></CardHeader>
          <CardContent>
            <div className="text-sm text-muted-foreground">
              Ask the AI Assistant for predictions and recommendations.
            </div>
          </CardContent>
        </Card>
      </div>
    </div>
  )
}