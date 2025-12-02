'use client'

import { useQuery } from '@tanstack/react-query'
import { apiRequest } from '@/lib/api'
import { DataTable } from '@/components/ui/data-table'

export default function AnalyticsPage() {
  const { data: strains = [] } = useQuery({
    queryKey: ['analytics-strains'],
    queryFn: () => apiRequest('/api/analytics/strains'),
  })

  const { data: recipes = [] } = useQuery({
    queryKey: ['analytics-recipes'],
    queryFn: () => apiRequest('/api/analytics/recipes'),
  })

  const strainColumns = [
    { key: 'name', label: 'Strain' },
    { key: 'batches', label: 'Batches' },
    { key: 'avg_yield', label: 'Avg Yield (g)' },
    { key: 'success_rate', label: 'Success Rate' },
  ]

  const recipeColumns = [
    { key: 'name', label: 'Recipe' },
    { key: 'versions', label: 'Versions' },
    { key: 'avg_yield', label: 'Avg Yield (g)' },
    { key: 'success_rate', label: 'Success Rate' },
  ]

  return (
    <div className="space-y-8">
      <h1 className="text-3xl font-semibold tracking-tight">Analytics</h1>

      <div className="grid grid-cols-1 lg:grid-cols-2 gap-8">
        <div>
          <h2 className="text-xl font-semibold mb-4">Strain Performance</h2>
          <DataTable data={strains} columns={strainColumns} />
        </div>

        <div>
          <h2 className="text-xl font-semibold mb-4">Recipe Performance</h2>
          <DataTable data={recipes} columns={recipeColumns} />
        </div>
      </div>
    </div>
  )
}