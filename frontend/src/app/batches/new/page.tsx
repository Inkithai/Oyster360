'use client'

import { useForm } from 'react-hook-form'
import { zodResolver } from '@hookform/resolvers/zod'
import { z } from 'zod'
import { useMutation, useQuery } from '@tanstack/react-query'
import { apiRequest } from '@/lib/api'
import { useRouter } from 'next/navigation'
import { useToast } from '@/components/ui/use-toast'
import { Button } from '@/components/ui/button'

const batchSchema = z.object({
  batch_number: z.string().min(3, 'Batch number must be at least 3 characters'),
  strain_id: z.number().min(1, 'Please select a strain'),
  recipe_version_id: z.number().min(1, 'Please select a recipe'),
  room_id: z.number().min(1, 'Please select a room'),
})

type BatchForm = z.infer<typeof batchSchema>

export default function NewBatchPage() {
  const router = useRouter()
  const { toast } = useToast()

  const { register, handleSubmit, formState: { errors, isSubmitting } } = useForm<BatchForm>({
    resolver: zodResolver(batchSchema),
  })

  const { data: strains = [] } = useQuery({
    queryKey: ['strains'],
    queryFn: () => apiRequest('/api/strains'),
  })

  const { data: rooms = [] } = useQuery({
    queryKey: ['rooms'],
    queryFn: () => apiRequest('/api/rooms'),
  })

  const { data: recipes = [] } = useQuery({
    queryKey: ['recipes'],
    queryFn: () => apiRequest('/api/recipes'),
  })

  const createBatch = useMutation({
    mutationFn: (data: BatchForm) => apiRequest('/api/batches', {
      method: 'POST',
      body: JSON.stringify(data),
    }),
    onSuccess: () => {
      toast({ title: 'Batch created successfully', variant: 'success' })
      router.push('/batches')
    },
    onError: () => {
      toast({ title: 'Failed to create batch', variant: 'error' })
    },
  })

  const onSubmit = (data: BatchForm) => {
    createBatch.mutate(data)
  }

  return (
    <div className="max-w-2xl">
      <h1 className="text-3xl font-semibold tracking-tight mb-8">Create New Batch</h1>

      <form onSubmit={handleSubmit(onSubmit)} className="space-y-6">
        <div>
          <label className="text-sm font-medium">Batch Number</label>
          <input
            {...register('batch_number')}
            className="mt-1 w-full rounded-lg border px-4 py-3"
            placeholder="OY-2026-XXX"
          />
          {errors.batch_number && <p className="text-sm text-destructive mt-1">{errors.batch_number.message}</p>}
        </div>

        <div>
          <label className="text-sm font-medium">Strain</label>
          <select {...register('strain_id', { valueAsNumber: true })} className="mt-1 w-full rounded-lg border px-4 py-3">
            <option value="">Select strain</option>
            {strains.map((s: any) => (
              <option key={s.id} value={s.id}>{s.name}</option>
            ))}
          </select>
          {errors.strain_id && <p className="text-sm text-destructive mt-1">{errors.strain_id.message}</p>}
        </div>

        <div>
          <label className="text-sm font-medium">Room</label>
          <select {...register('room_id', { valueAsNumber: true })} className="mt-1 w-full rounded-lg border px-4 py-3">
            <option value="">Select room</option>
            {rooms.map((r: any) => (
              <option key={r.id} value={r.id}>{r.name}</option>
            ))}
          </select>
          {errors.room_id && <p className="text-sm text-destructive mt-1">{errors.room_id.message}</p>}
        </div>

        <div>
          <label className="text-sm font-medium">Recipe Version</label>
          <select {...register('recipe_version_id', { valueAsNumber: true })} className="mt-1 w-full rounded-lg border px-4 py-3">
            <option value="">Select recipe</option>
            {recipes.map((r: any) => (
              <option key={r.id} value={r.id}>{r.name}</option>
            ))}
          </select>
          {errors.recipe_version_id && <p className="text-sm text-destructive mt-1">{errors.recipe_version_id.message}</p>}
        </div>

        <div className="flex gap-4 pt-4">
          <Button type="button" variant="outline" onClick={() => router.back()}>
            Cancel
          </Button>
          <Button type="submit" disabled={isSubmitting}>
            {isSubmitting ? 'Creating...' : 'Create Batch'}
          </Button>
        </div>
      </form>
    </div>
  )
}