'use client'

import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card'

export default function WorkerDashboard() {
  return (
    <div className="max-w-5xl mx-auto space-y-8">
      <div>
        <h1 className="text-3xl font-semibold tracking-tight">Worker Dashboard</h1>
        <p className="text-muted-foreground">Bim Mal Plantation • Today: July 7, 2026</p>
      </div>

      <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
        <Card>
          <CardHeader>
            <CardTitle>Today's Tasks</CardTitle>
          </CardHeader>
          <CardContent className="space-y-3 text-sm">
            <div className="flex justify-between items-center border-b pb-2">
              <div>Check humidity - Room A</div>
              <div className="text-green-600">Done</div>
            </div>
            <div className="flex justify-between items-center border-b pb-2">
              <div>Add growth log - Batch OY-019</div>
              <div className="text-orange-600">Pending</div>
            </div>
            <div className="flex justify-between items-center">
              <div>Inspect pins - Room B</div>
              <div className="text-orange-600">Pending</div>
            </div>
          </CardContent>
        </Card>

        <Card>
          <CardHeader>
            <CardTitle>Active Batches</CardTitle>
          </CardHeader>
          <CardContent>
            <div className="text-4xl font-bold">8</div>
            <p className="text-sm text-muted-foreground">Assigned to you</p>
          </CardContent>
        </Card>

        <Card>
          <CardHeader>
            <CardTitle>Alerts</CardTitle>
          </CardHeader>
          <CardContent className="space-y-2 text-sm">
            <div className="text-orange-600">• 2 items low stock</div>
            <div className="text-red-600">• 1 contamination flagged</div>
            <div className="text-green-600">• 3 batches ready for inspection</div>
          </CardContent>
        </Card>
      </div>
    </div>
  )
}