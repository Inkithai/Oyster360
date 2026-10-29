'use client'

import Link from 'next/link'
import { useQuery } from '@tanstack/react-query'
import { apiRequest } from '@/lib/api'
import { DataTable } from '@/components/ui/data-table'
import { Button } from '@/components/ui/button'

export default function HarvestsPage() {
  const { data: harvests = [] } = useQuery({
    queryKey: ['harvests'],
    queryFn: () => apiRequest('/api/harvests'),
  })

  const columns = [
    { key: 'batch_id', label: 'Batch' },
    {
      key: 'flush_number',
      label: 'Flush #',
      render: (item: any) => `Flush ${item.flush_number || 1}`,
    },
    { key: 'quantity_kg', label: 'Quantity (kg)' },
    {
      key: 'spoiled_kg',
      label: 'Unsold / Spoiled (kg)',
      render: (item: any) => `${item.unsold_kg ?? 0} / ${item.spoiled_kg ?? 0}`,
    },
    { key: 'quality_score', label: 'Quality' },
    { key: 'selling_price', label: 'Price/kg (Rs.)' },
    {
      key: 'harvest_date',
      label: 'Date',
      render: (item: any) => (item.harvest_date ? new Date(item.harvest_date).toLocaleDateString() : '-'),
    },
  ]

  return (
    <div className="space-y-8">
      <div className="flex flex-col gap-4 sm:flex-row sm:items-center sm:justify-between">
        <div>
          <h1 className="text-3xl font-semibold tracking-tight">Harvest Records</h1>
          <p className="text-sm text-muted-foreground">
            Track harvest weight per batch and per flush, selling price in LKR, and unsold or spoiled stock
          </p>
        </div>
        <Link href="/harvests/new">
          <Button className="bg-emerald-700 hover:bg-emerald-800">
            + 60-Second Harvest Entry
          </Button>
        </Link>
      </div>

      <DataTable data={harvests} columns={columns} searchable exportable />
    </div>
  )
}
