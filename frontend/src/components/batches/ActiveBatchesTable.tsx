'use client'

export function ActiveBatchesTable() {
  const mockBatches = [
    { id: 1, batch_number: "B-2025-042", strain: "Pearl Oyster", stage: "COLONIZATION" },
    { id: 2, batch_number: "B-2025-043", strain: "Blue Oyster", stage: "FRUITING" },
  ]

  return (
    <div className="rounded-xl border bg-card p-6">
      <h3 className="font-semibold mb-4">Active Batches</h3>
      <div className="space-y-4">
        {mockBatches.map(batch => (
          <div key={batch.id} className="flex justify-between border-b pb-3">
            <div>
              <div className="font-medium">{batch.batch_number}</div>
              <div className="text-sm text-muted-foreground">{batch.strain}</div>
            </div>
            <div className="text-sm font-medium text-blue-600">{batch.stage}</div>
          </div>
        ))}
      </div>
    </div>
  )
}