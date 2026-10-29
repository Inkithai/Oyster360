'use client'

import { useState } from 'react'
import Link from 'next/link'
import { useParams } from 'next/navigation'
import { useMutation, useQuery, useQueryClient } from '@tanstack/react-query'
import { apiRequest } from '@/lib/api'
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card'
import { Button } from '@/components/ui/button'
import { useToast } from '@/components/ui/use-toast'

const NEXT_STAGE: Record<string, string> = {
  PREPARATION: 'INOCULATION',
  INOCULATION: 'COLONIZATION',
  COLONIZATION: 'FRUITING',
  FRUITING: 'HARVEST',
  HARVEST: 'COMPLETED',
}

export default function BatchDetailPage() {
  const params = useParams()
  const batchId = params.id as string
  const queryClient = useQueryClient()
  const { toast } = useToast()

  const { data: batch } = useQuery({
    queryKey: ['batch', batchId],
    queryFn: () => apiRequest(`/api/batches/${batchId}`),
  })

  const { data: flushes = [] } = useQuery({
    queryKey: ['batch-harvests', batchId],
    queryFn: () => apiRequest(`/api/batches/${batchId}/harvests`),
  })

  const [contaminatedInput, setContaminatedInput] = useState<string>('')
  const [harvestedInput, setHarvestedInput] = useState<string>('')

  const updateBagsMutation = useMutation({
    mutationFn: (payload: Record<string, unknown>) =>
      apiRequest(`/api/batches/${batchId}/bags`, {
        method: 'PATCH',
        body: JSON.stringify(payload),
      }),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['batch', batchId] })
      toast({ title: 'Grow-bag counts updated', variant: 'success' })
    },
    onError: (err: Error) => {
      toast({ title: err.message || 'Update failed', variant: 'error' })
    },
  })

  const advanceStageMutation = useMutation({
    mutationFn: (stage: string) =>
      apiRequest(`/api/batches/${batchId}/stage`, {
        method: 'PATCH',
        body: JSON.stringify({ stage }),
      }),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['batch', batchId] })
      toast({ title: 'Batch stage updated', variant: 'success' })
    },
  })

  const nextStage = batch?.current_stage ? NEXT_STAGE[batch.current_stage] : undefined

  return (
    <div className="max-w-5xl mx-auto space-y-8">
      <div className="flex flex-col gap-4 sm:flex-row sm:items-center sm:justify-between">
        <div>
          <h1 className="text-3xl font-semibold tracking-tight">
            Batch #{batch?.batch_number || batchId}
          </h1>
          <p className="text-muted-foreground">
            Grow-bag tracking, contamination records, and harvest flushes
          </p>
        </div>
        <div className="flex gap-3">
          {nextStage && (
            <Button
              variant="outline"
              onClick={() => advanceStageMutation.mutate(nextStage)}
              disabled={advanceStageMutation.isPending}
            >
              Advance to {nextStage} →
            </Button>
          )}
          <Link href="/harvests/new">
            <Button>+ Record Flush Harvest</Button>
          </Link>
        </div>
      </div>

      {/* Grow-Bag Counters */}
      <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
        <Card>
          <CardHeader className="pb-2"><CardTitle className="text-sm text-muted-foreground">Bags Prepared</CardTitle></CardHeader>
          <CardContent><div className="text-3xl font-bold">{batch?.bags_prepared ?? 500}</div></CardContent>
        </Card>
        <Card>
          <CardHeader className="pb-2"><CardTitle className="text-sm text-muted-foreground">Healthy Active Bags</CardTitle></CardHeader>
          <CardContent><div className="text-3xl font-bold text-emerald-700">{batch?.active_healthy_bags ?? 500}</div></CardContent>
        </Card>
        <Card>
          <CardHeader className="pb-2"><CardTitle className="text-sm text-muted-foreground">Contaminated Bags</CardTitle></CardHeader>
          <CardContent>
            <div className="text-3xl font-bold text-red-600">
              {batch?.bags_contaminated ?? 0} ({batch?.contamination_rate_pct ?? 0}%)
            </div>
          </CardContent>
        </Card>
        <Card>
          <CardHeader className="pb-2"><CardTitle className="text-sm text-muted-foreground">Bags Harvested</CardTitle></CardHeader>
          <CardContent><div className="text-3xl font-bold">{batch?.bags_harvested ?? 0}</div></CardContent>
        </Card>
      </div>

      <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
        <Card>
          <CardHeader><CardTitle>Batch Information</CardTitle></CardHeader>
          <CardContent className="space-y-2 text-sm">
            <div>Status: <span className="font-medium">{batch?.status || 'Active'}</span></div>
            <div>Stage: <span className="font-medium">{batch?.current_stage || 'In Progress'}</span></div>
            <div>
              Expected Harvest:{' '}
              <span className="font-medium">
                {batch?.expected_harvest_date
                  ? new Date(batch.expected_harvest_date).toLocaleDateString()
                  : 'Calculated from strain cycle'}
              </span>
            </div>
          </CardContent>
        </Card>

        <Card>
          <CardHeader><CardTitle>Update Contaminated / Harvested Bags</CardTitle></CardHeader>
          <CardContent className="space-y-3">
            <div className="grid grid-cols-2 gap-2">
              <div>
                <label className="text-xs font-medium">Contaminated Bags</label>
                <input
                  type="number"
                  min={0}
                  value={contaminatedInput}
                  onChange={(e) => setContaminatedInput(e.target.value)}
                  placeholder={String(batch?.bags_contaminated ?? 0)}
                  className="mt-1 w-full rounded-lg border px-3 py-2 text-sm"
                />
              </div>
              <div>
                <label className="text-xs font-medium">Harvested Bags</label>
                <input
                  type="number"
                  min={0}
                  value={harvestedInput}
                  onChange={(e) => setHarvestedInput(e.target.value)}
                  placeholder={String(batch?.bags_harvested ?? 0)}
                  className="mt-1 w-full rounded-lg border px-3 py-2 text-sm"
                />
              </div>
            </div>
            <Button
              size="sm"
              className="w-full"
              onClick={() => {
                const payload: Record<string, unknown> = {}
                if (contaminatedInput !== '') payload.bags_contaminated = Number(contaminatedInput)
                if (harvestedInput !== '') payload.bags_harvested = Number(harvestedInput)
                updateBagsMutation.mutate(payload)
              }}
            >
              Save Bag Counts
            </Button>
          </CardContent>
        </Card>

        <Card>
          <CardHeader><CardTitle>Recorded Flushes ({flushes.length})</CardTitle></CardHeader>
          <CardContent className="space-y-2 text-sm">
            {flushes.length === 0 ? (
              <div className="text-muted-foreground">No harvest flushes recorded yet.</div>
            ) : (
              flushes.map((f: any) => (
                <div key={f.id} className="flex justify-between border-b pb-1.5">
                  <span>Flush #{f.flush_number}</span>
                  <span className="font-medium">
                    {f.quantity_kg} kg (Rs. {Number(f.revenue || 0).toLocaleString()})
                  </span>
                </div>
              ))
            )}
          </CardContent>
        </Card>
      </div>
    </div>
  )
}
