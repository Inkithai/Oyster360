'use client'

import { useQuery } from '@tanstack/react-query'
import { apiRequest } from '@/lib/api'
import { DataTable } from '@/components/ui/data-table'

export default function PurchasesPage() {
  const { data: suppliers = [] } = useQuery({
    queryKey: ['suppliers'],
    queryFn: () => apiRequest('/api/purchases/suppliers'),
  })

  const { data: orders = [] } = useQuery({
    queryKey: ['purchase-orders'],
    queryFn: () => apiRequest('/api/purchases/orders'),
  })

  const supplierColumns = [
    { key: 'name', label: 'Supplier' },
    { key: 'contact_person', label: 'Contact' },
    { key: 'phone', label: 'Phone' },
    { key: 'email', label: 'Email' },
  ]

  const orderColumns = [
    { key: 'order_number', label: 'Order #' },
    { key: 'status', label: 'Status' },
    { key: 'total_amount', label: 'Total (Rs.)' },
    { key: 'expected_date', label: 'Expected Date' },
  ]

  return (
    <div className="space-y-8">
      <h1 className="text-3xl font-semibold tracking-tight">Purchases & Suppliers</h1>

      <div>
        <h2 className="text-xl font-semibold mb-4">Suppliers</h2>
        <DataTable data={suppliers} columns={supplierColumns} searchable exportable />
      </div>

      <div>
        <h2 className="text-xl font-semibold mb-4">Purchase Orders</h2>
        <DataTable data={orders} columns={orderColumns} searchable exportable />
      </div>
    </div>
  )
}