'use client'

import { useQuery } from '@tanstack/react-query'
import { apiRequest } from '@/lib/api'
import { DataTable } from '@/components/ui/data-table'

export default function InventoryPage() {
  const { data: items = [] } = useQuery({
    queryKey: ['inventory-items'],
    queryFn: () => apiRequest('/api/inventory/items'),
  })

  const columns = [
    { key: 'name', label: 'Item' },
    { key: 'category', label: 'Category' },
    { key: 'current_stock', label: 'Stock' },
    { key: 'unit', label: 'Unit' },
    { 
      key: 'reorder_level', 
      label: 'Reorder Level',
      render: (item: any) => (
        <span className={item.current_stock <= item.reorder_level ? 'text-orange-600 font-medium' : ''}>
          {item.reorder_level}
        </span>
      )
    },
  ]

  return (
    <div>
      <h1 className="text-3xl font-semibold tracking-tight mb-8">Inventory</h1>
      <DataTable data={items} columns={columns} searchable exportable />
    </div>
  )
}