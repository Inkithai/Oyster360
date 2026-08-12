'use client'

import { useQuery } from '@tanstack/react-query'
import { apiRequest } from '@/lib/api'
import { DataTable } from '@/components/ui/data-table'

export default function GradingPage() {
  const { data: grades = [] } = useQuery({
    queryKey: ['harvest-grades'],
    queryFn: () => apiRequest('/api/harvest-grades/batches/1'),
  })

  const columns = [
    { key: 'grade', label: 'Grade' },
    { key: 'quantity_kg', label: 'Quantity (kg)' },
    { key: 'price_per_kg', label: 'Price/kg (Rs.)' },
    { 
      key: 'total', 
      label: 'Total Revenue',
      render: (item: any) => (item.quantity_kg * item.price_per_kg).toFixed(0)
    },
  ]

  return (
    <div>
      <h1 className="text-3xl font-semibold tracking-tight mb-8">Harvest Quality Control</h1>
      <DataTable data={grades} columns={columns} searchable exportable />
    </div>
  )
}