'use client'

import Link from 'next/link'
import { useQuery } from '@tanstack/react-query'
import { apiRequest } from '@/lib/api'
import { DataTable } from '@/components/ui/data-table'
import { Button } from '@/components/ui/button'
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card'

export default function BatchesPage() {
  const { data: batchList = [] } = useQuery({
    queryKey: ['batches'],
    queryFn: () => apiRequest('/api/batches'),
  })

  const highContamBatches = Array.isArray(batchList)
    ? batchList.filter((b: any) => (b.contamination_rate_pct ?? 0) >= 10)
    : []

  const columns = [
    {
      key: 'batch_number',
      label: 'Batch ID',
      render: (item: any) => (
        <Link href={`/batches/${item.id || 1}`} className="font-medium underline-offset-4 hover:underline">
          {item.batch_number}
        </Link>
      ),
    },
    {
      key: 'current_stage',
      label: 'Stage',
      render: (item: any) => (
        <span className="inline-block px-3 py-1 rounded-full text-xs bg-blue-100 text-blue-800">
          {item.current_stage}
        </span>
      ),
    },
    {
      key: 'bags_prepared',
      label: 'Bags Prepared',
      render: (item: any) => item.bags_prepared ?? 500,
    },
    {
      key: 'bags_contaminated',
      label: 'Contaminated',
      render: (item: any) => {
        const contam = item.bags_contaminated ?? 0
        const pct = item.contamination_rate_pct ?? 0
        return (
          <span className={pct >= 10 ? 'text-red-600 font-semibold' : ''}>
            {contam} ({pct}%)
          </span>
        )
      },
    },
    { key: 'status', label: 'Status' },
    {
      key: 'start_date',
      label: 'Start Date',
      render: (item: any) => (item.start_date ? new Date(item.start_date).toLocaleDateString() : '-'),
    },
  ]

  return (
    <div className="space-y-8">
      <div className="flex flex-col gap-4 sm:flex-row sm:items-center sm:justify-between">
        <div>
          <h1 className="text-3xl font-semibold tracking-tight">Batches</h1>
          <p className="text-sm text-muted-foreground">
            Track grow bags prepared, inoculated, contaminated, and harvested per batch
          </p>
        </div>
        <div className="flex gap-3">
          <Link href="/harvests/new">
            <Button variant="outline">+ Record Flush Harvest</Button>
          </Link>
          <Link href="/batches/new">
            <Button>+ Create Batch</Button>
          </Link>
        </div>
      </div>

      {highContamBatches.length > 0 && (
        <Card className="border-amber-200 bg-amber-50/50">
          <CardHeader className="pb-2">
            <CardTitle className="text-base">Crop-Loss &amp; Contamination Alerts ({highContamBatches.length})</CardTitle>
          </CardHeader>
          <CardContent>
            <ul className="space-y-2 text-sm">
              {highContamBatches.map((b: any, idx: number) => (
                <li key={idx} className="flex items-center justify-between rounded-lg bg-white p-3 border">
                  <span className="font-semibold text-red-700">
                    Batch {b.batch_number}: {b.bags_contaminated} bags contaminated ({b.contamination_rate_pct}%)
                  </span>
                  <span className="rounded-full bg-red-100 px-2.5 py-0.5 text-xs font-medium text-red-800">
                    Isolate contaminated bags
                  </span>
                </li>
              ))}
            </ul>
          </CardContent>
        </Card>
      )}

      <DataTable data={batchList} columns={columns} searchable exportable />
    </div>
  )
}
