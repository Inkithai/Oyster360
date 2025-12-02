'use client'

import { useQuery } from '@tanstack/react-query'
import { apiRequest } from '@/lib/api'
import { DataTable } from '@/components/ui/data-table'

export default function StrainsPage() {
  const { data: strainList = [] } = useQuery({
    queryKey: ['strains'],
    queryFn: () => apiRequest('/api/strains'),
  })

  const columns = [
    { key: 'name', label: 'Strain' },
    { key: 'species', label: 'Species' },
    { key: 'difficulty', label: 'Difficulty' },
    { key: 'colonization_days', label: 'Colonization (days)' },
    { key: 'fruiting_days', label: 'Fruiting (days)' },
  ]

  return (
    <div>
      <h1 className="text-3xl font-semibold tracking-tight mb-8">Oyster Mushroom Strains</h1>
      <DataTable data={strainList} columns={columns} searchable exportable />
    </div>
  )
}