'use client'

import { useForm } from 'react-hook-form'
import { zodResolver } from '@hookform/resolvers/zod'
import { z } from 'zod'
import { useMutation } from '@tanstack/react-query'
import { apiRequest } from '@/lib/api'
import { useRouter } from 'next/navigation'
import { useToast } from '@/components/ui/use-toast'
import { Button } from '@/components/ui/button'

const growthLogSchema = z.object({
  batch_id: z.number().min(1),
  stage: z.string().min(1),
  notes: z.string().min(5, 'Notes are required'),
  health_score: z.number().min(0).max(100),
})

type GrowthLogForm = z.infer<typeof growthLogSchema>

export default function NewGrowthLogPage() {
  const router = useRouter()
  const { toast } = useToast()

  const { register, handleSubmit, formState: { errors, isSubmitting } } = useForm<GrowthLogForm>({
    resolver: zodResolver(growthLogSchema),
    defaultValues: { health_score: 85 }
  })

  const createLog = useMutation({
    mutationFn: (data: GrowthLogForm) => apiRequest('/api/batches/1/growth-logs', {
      method: 'POST',
      body: JSON.stringify(data),
    }),
    onSuccess: () => {
      toast({ title: 'Growth log recorded', variant: 'success' })
      router.push('/batches')
    },
  })

  const onSubmit = (data: GrowthLogForm) => createLog.mutate(data)

  return (
    <div className="max-w-xl">
      <h1 className="text-3xl font-semibold tracking-tight mb-8">Add Growth Log</h1>

      <form onSubmit={handleSubmit(onSubmit)} className="space-y-6">
        <div>
          <label className="text-sm font-medium">Stage</label>
          <select {...register('stage')} className="mt-1 w-full rounded-lg border px-4 py-3">
            <option value="">Select stage</option>
            <option value="PREPARATION">Preparation</option>
            <option value="INOCULATION">Inoculation</option>
            <option value="COLONIZATION">Colonization</option>
            <option value="FRUITING">Fruiting</option>
          </select>
          {errors.stage && <p className="text-sm text-destructive mt-1">{errors.stage.message}</p>}
        </div>

        <div>
          <label className="text-sm font-medium">Health Score (0-100)</label>
          <input type="number" {...register('health_score', { valueAsNumber: true })} className="mt-1 w-full rounded-lg border px-4 py-3" />
          {errors.health_score && <p className="text-sm text-destructive mt-1">{errors.health_score.message}</p>}
        </div>

        <div>
          <label className="text-sm font-medium">Notes</label>
          <textarea {...register('notes')} className="mt-1 w-full rounded-lg border px-4 py-3 h-24" placeholder="Observations..." />
          {errors.notes && <p className="text-sm text-destructive mt-1">{errors.notes.message}</p>}
        </div>

        <div className="flex gap-4 pt-4">
          <Button type="button" variant="outline" onClick={() => router.back()}>Cancel</Button>
          <Button type="submit" disabled={isSubmitting}>
            {isSubmitting ? 'Saving...' : 'Save Log'}
          </Button>
        </div>
      </form>
    </div>
  )
}