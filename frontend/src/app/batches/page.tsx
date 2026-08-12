'use client'

import { useQuery } from '@tanstack/react-query'
import { apiRequest } from '@/lib/api'
import { DataTable } from '@/components/ui/data-table'

export default function BatchesPage() {
  const { data: batchList = [] } = useQuery({
    queryKey: ['batches'],
    queryFn: () => apiRequest('/api/batches'),
  })

  const columns = [
    { key: 'batch_number', label: 'Batch ID' },
    { 
      key: 'current_stage', 
      label: 'Stage',
      render: (item: any) => (
        <span className="inline-block px-3 py-1 rounded-full text-xs bg-blue-100 text-blue-800">
          {item.current_stage}
        </span>
      )
    },
    { key: 'status', label: 'Status' },
    { 
      key: 'start_date', 
      label: 'Start Date',
      render: (item: any) => item.start_date ? new Date(item.start_date).toLocaleDateString() : '-'
    },
  ]

  return (
    <div>
      <h1 className="text-3xl font-semibold tracking-tight mb-8">Batches</h1>
      <DataTable 
        data={batchList} 
        columns={columns} 
        searchable 
        exportable 
      />
    </div>
  )
}