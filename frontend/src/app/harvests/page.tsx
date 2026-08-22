'use client'

import { useQuery } from '@tanstack/react-query'
import { apiRequest } from '@/lib/api'
import { DataTable } from '@/components/ui/data-table'

export default function HarvestsPage() {
  const { data: harvests = [] } = useQuery({
    queryKey: ['harvests'],
    queryFn: () => apiRequest('/api/harvests'),
  })

  const columns = [
    { key: 'batch_id', label: 'Batch' },
    { key: 'quantity_kg', label: 'Quantity (kg)' },
    { key: 'quality_score', label: 'Quality' },
    { key: 'selling_price', label: 'Price/kg' },
    { 
      key: 'harvest_date', 
      label: 'Date',
      render: (item: any) => new Date(item.harvest_date).toLocaleDateString()
    },
  ]

  return (
    <div>
      <h1 className="text-3xl font-semibold tracking-tight mb-8">Harvest Records</h1>
      <DataTable data={harvests} columns={columns} searchable exportable />
    </div>
  )
}