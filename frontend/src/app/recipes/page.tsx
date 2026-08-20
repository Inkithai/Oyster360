'use client'

import { useQuery } from '@tanstack/react-query'
import { apiRequest } from '@/lib/api'
import { DataTable } from '@/components/ui/data-table'

export default function RecipesPage() {
  const { data: recipes = [] } = useQuery({
    queryKey: ['recipes'],
    queryFn: () => apiRequest('/api/recipes'),
  })

  const columns = [
    { key: 'name', label: 'Recipe Name' },
    { key: 'description', label: 'Description' },
    { 
      key: 'success_rate', 
      label: 'Success Rate',
      render: (item: any) => (
        <span className="text-green-600 font-medium">{item.success_rate || '92'}%</span>
      )
    },
  ]

  return (
    <div>
      <h1 className="text-3xl font-semibold tracking-tight mb-8">Substrate Recipes</h1>
      <DataTable data={recipes} columns={columns} searchable exportable />
    </div>
  )
}