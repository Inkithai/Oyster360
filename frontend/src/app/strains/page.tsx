'use client'

import { useQuery } from '@tanstack/react-query'
import { apiRequest } from '@/lib/api'
import { DataTable } from '@/components/ui/data-table'
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card'

const DEFAULT_DOA_VARIETIES = [
  {
    name: 'American Oyster (Bhutani)',
    local_name_si: 'ඇමරිකන් ඔයිස්ටර් (භූතානි)',
    local_name_ta: 'அமெரிக்கன் சிப்பி காளான்',
    species: 'Pleurotus ostreatus',
    optimal_temp_c: '24–28°C',
    optimal_humidity_pct: '85–90%',
    expected_yield_g_per_bag: 350,
    doa_notes: 'Standard commercial variety in Sri Lanka on rubber/mango sawdust + rice bran.',
  },
  {
    name: 'Abalone Mushroom',
    local_name_si: 'ඇබලෝනි බිම්මල්',
    local_name_ta: 'அபலோன் காளான்',
    species: 'Pleurotus cystidiosus',
    optimal_temp_c: '26–30°C',
    optimal_humidity_pct: '85–92%',
    expected_yield_g_per_bag: 300,
    doa_notes: 'Thick caps with longer shelf life for supermarkets and hotels.',
  },
  {
    name: 'Pink Oyster',
    local_name_si: 'රෝස ඔයිස්ටර්',
    local_name_ta: 'இளஞ்சிவப்பு சிப்பி காளான்',
    species: 'Pleurotus djamor',
    optimal_temp_c: '26–32°C',
    optimal_humidity_pct: '85–90%',
    expected_yield_g_per_bag: 280,
    doa_notes: 'Fast-growing warm-zone variety; best sold fresh on the same day.',
  },
]

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
    <div className="space-y-8">
      <div>
        <h1 className="text-3xl font-semibold tracking-tight mb-2">Oyster Mushroom Strains</h1>
        <p className="text-sm text-muted-foreground">
          Locally cultivated varieties and Department of Agriculture (DOA) Sri Lanka growing parameters
        </p>
      </div>

      <DataTable data={strainList} columns={columns} searchable exportable />

      <div>
        <h2 className="text-xl font-semibold mb-4">
          Sri Lanka Department of Agriculture (DOA) Variety Reference
        </h2>
        <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
          {DEFAULT_DOA_VARIETIES.map((v) => (
            <Card key={v.name}>
              <CardHeader className="pb-2">
                <CardTitle className="text-base">{v.name}</CardTitle>
                <div className="text-xs text-muted-foreground">
                  {v.local_name_si} • {v.local_name_ta}
                </div>
              </CardHeader>
              <CardContent className="space-y-1.5 text-xs">
                <div>{`Botanical Species: ${v.species}`}</div>
                <div>{`Optimal Temp / RH: ${v.optimal_temp_c} at ${v.optimal_humidity_pct}`}</div>
                <div>{`Target Yield: ~${v.expected_yield_g_per_bag}g per bag`}</div>
                <p className="text-muted-foreground pt-1">{v.doa_notes}</p>
              </CardContent>
            </Card>
          ))}
        </div>
      </div>
    </div>
  )
}
