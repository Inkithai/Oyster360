'use client'

import { useState } from 'react'
import { useMutation } from '@tanstack/react-query'
import { apiRequest } from '@/lib/api'
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card'
import { Button } from '@/components/ui/button'

export default function ImageAnalysisPage() {
  const [batchId, setBatchId] = useState(1)
  const [imageUrl, setImageUrl] = useState('')
  const [inspectionId, setInspectionId] = useState<number | null>(null)
  const [analysisResult, setAnalysisResult] = useState<any>(null)

  const uploadMutation = useMutation({
    mutationFn: () =>
      apiRequest('/api/inspections/upload', {
        method: 'POST',
        body: JSON.stringify({ batch_id: batchId, room_id: 1, image_url: imageUrl }),
      }),
    onSuccess: (data) => setInspectionId(data.inspection_id),
  })

  const analyzeMutation = useMutation({
    mutationFn: () =>
      apiRequest(`/api/inspections/${inspectionId}/analyze`, { method: 'POST' }),
    onSuccess: (data) => setAnalysisResult(data),
  })

  return (
    <div className="max-w-4xl mx-auto space-y-8">
      <div>
        <h1 className="text-3xl font-semibold tracking-tight">Oyster360 Image Analysis</h1>
        <p className="text-muted-foreground">AI-Powered Mushroom Quality Inspection</p>
      </div>

      <Card>
        <CardHeader>
          <CardTitle>New Inspection</CardTitle>
        </CardHeader>
        <CardContent className="space-y-4">
          <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
            <div>
              <label className="text-sm font-medium">Batch ID</label>
              <input type="number" value={batchId} onChange={e => setBatchId(Number(e.target.value))} className="mt-1 w-full rounded-lg border px-4 py-2" />
            </div>
            <div className="md:col-span-2">
              <label className="text-sm font-medium">Image URL</label>
              <input type="text" value={imageUrl} onChange={e => setImageUrl(e.target.value)} placeholder="https://..." className="mt-1 w-full rounded-lg border px-4 py-2" />
            </div>
          </div>

          <Button onClick={() => uploadMutation.mutate()} disabled={!imageUrl}>
            Upload Image
          </Button>
        </CardContent>
      </Card>

      {inspectionId && (
        <Card>
          <CardHeader>
            <CardTitle>Run AI Analysis</CardTitle>
          </CardHeader>
          <CardContent>
            <Button onClick={() => analyzeMutation.mutate()} className="bg-blue-600">
              Analyze with AI
            </Button>

            {analysisResult && (
              <div className="mt-6 border rounded-xl p-6 bg-muted/30">
                <div className="grid grid-cols-2 md:grid-cols-4 gap-4 mb-6">
                  <div>
                    <div className="text-sm text-muted-foreground">Health Score</div>
                    <div className="text-3xl font-bold">{analysisResult.health_score}%</div>
                  </div>
                  <div>
                    <div className="text-sm text-muted-foreground">Contamination Risk</div>
                    <div className="text-3xl font-bold">{analysisResult.contamination_probability}%</div>
                  </div>
                  <div>
                    <div className="text-sm text-muted-foreground">Stage</div>
                    <div className="text-2xl font-semibold mt-1">{analysisResult.detected_stage}</div>
                  </div>
                </div>

                <div>
                  <div className="font-medium mb-2">Recommendations</div>
                  <ul className="list-disc pl-5 space-y-1 text-sm">
                    {analysisResult.recommendations?.map((rec: string, i: number) => (
                      <li key={i}>{rec}</li>
                    ))}
                  </ul>
                </div>
              </div>
            )}
          </CardContent>
        </Card>
      )}
    </div>
  )
}