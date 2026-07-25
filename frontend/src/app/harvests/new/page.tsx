'use client'

import { useForm } from 'react-hook-form'
import { zodResolver } from '@hookform/resolvers/zod'
import { z } from 'zod'
import { useMutation } from '@tanstack/react-query'
import { apiRequest } from '@/lib/api'
import { useRouter } from 'next/navigation'
import { useToast } from '@/components/ui/use-toast'
import { Button } from '@/components/ui/button'

const harvestSchema = z.object({
  batch_id: z.number().min(1, 'Batch is required'),
  quantity_kg: z.number().min(0.1, 'Quantity must be greater than 0'),
  quality_score: z.number().min(0).max(100),
  selling_price: z.number().min(0),
})

type HarvestForm = z.infer<typeof harvestSchema>

export default function NewHarvestPage() {
  const router = useRouter()
  const { toast } = useToast()

  const { register, handleSubmit, formState: { errors, isSubmitting } } = useForm<HarvestForm>({
    resolver: zodResolver(harvestSchema),
  })

  const createHarvest = useMutation({
    mutationFn: (data: HarvestForm) => apiRequest('/api/batches/1/harvest', {
      method: 'POST',
      body: JSON.stringify(data),
    }),
    onSuccess: () => {
      toast({ title: 'Harvest recorded', variant: 'success' })
      router.push('/batches')
    },
  })

  const onSubmit = (data: HarvestForm) => createHarvest.mutate(data)

  return (
    <div className="max-w-xl">
      <h1 className="text-3xl font-semibold tracking-tight mb-8">Record Harvest</h1>

      <form onSubmit={handleSubmit(onSubmit)} className="space-y-6">
        <div>
          <label className="text-sm font-medium">Quantity (kg)</label>
          <input type="number" step="0.1" {...register('quantity_kg', { valueAsNumber: true })} className="mt-1 w-full rounded-lg border px-4 py-3" />
          {errors.quantity_kg && <p className="text-sm text-destructive mt-1">{errors.quantity_kg.message}</p>}
        </div>

        <div>
          <label className="text-sm font-medium">Quality Score (0-100)</label>
          <input type="number" {...register('quality_score', { valueAsNumber: true })} className="mt-1 w-full rounded-lg border px-4 py-3" />
          {errors.quality_score && <p className="text-sm text-destructive mt-1">{errors.quality_score.message}</p>}
        </div>

        <div>
          <label className="text-sm font-medium">Selling Price (Rs/kg)</label>
          <input type="number" step="0.01" {...register('selling_price', { valueAsNumber: true })} className="mt-1 w-full rounded-lg border px-4 py-3" />
          {errors.selling_price && <p className="text-sm text-destructive mt-1">{errors.selling_price.message}</p>}
        </div>

        <div className="flex gap-4 pt-4">
          <Button type="button" variant="outline" onClick={() => router.back()}>Cancel</Button>
          <Button type="submit" disabled={isSubmitting}>
            {isSubmitting ? 'Recording...' : 'Record Harvest'}
          </Button>
        </div>
      </form>
    </div>
  )
}