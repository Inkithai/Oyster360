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
  bags_prepared: z.number().min(1, 'Enter number of grow bags prepared'),
  notes: z.string().optional(),
})

type BatchForm = z.infer<typeof batchSchema>

export default function NewBatchPage() {
  const router = useRouter()
  const { toast } = useToast()

  const { register, handleSubmit, setValue, formState: { errors, isSubmitting } } = useForm<BatchForm>({
    resolver: zodResolver(batchSchema),
    defaultValues: {
      bags_prepared: 500,
    },
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
    mutationFn: (data: BatchForm) =>
      apiRequest('/api/batches', {
        method: 'POST',
        body: JSON.stringify({
          ...data,
          bags_inoculated: data.bags_prepared,
        }),
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
      <h1 className="text-3xl font-semibold tracking-tight mb-2">Create New Batch</h1>
      <p className="text-sm text-muted-foreground mb-8">
        Start a new cultivation batch and record the number of polypropylene grow bags prepared
      </p>

      <form onSubmit={handleSubmit(onSubmit)} className="space-y-6">
        <div className="grid grid-cols-1 sm:grid-cols-2 gap-4">
          <div>
            <label className="text-sm font-medium">Batch Number</label>
            <input
              {...register('batch_number')}
              className="mt-1 w-full rounded-lg border px-4 py-3"
              placeholder="OY-2026-001"
            />
            {errors.batch_number && <p className="text-sm text-destructive mt-1">{errors.batch_number.message}</p>}
          </div>

          <div>
            <label className="text-sm font-medium">Grow Bags Prepared</label>
            <input
              type="number"
              {...register('bags_prepared', { valueAsNumber: true })}
              className="mt-1 w-full rounded-lg border px-4 py-3"
            />
            <div className="flex gap-2 mt-2">
              {[250, 500, 1000, 1500].map((count) => (
                <button
                  key={count}
                  type="button"
                  onClick={() => setValue('bags_prepared', count)}
                  className="rounded-md border px-2.5 py-1 text-xs hover:bg-muted"
                >
                  {count} bags
                </button>
              ))}
            </div>
            {errors.bags_prepared && <p className="text-sm text-destructive mt-1">{errors.bags_prepared.message}</p>}
          </div>
        </div>

        <div>
          <label className="text-sm font-medium">Mushroom Variety / Strain (DOA Sri Lanka)</label>
          <select {...register('strain_id', { valueAsNumber: true })} className="mt-1 w-full rounded-lg border px-4 py-3">
            <option value="">Select strain</option>
            {strains.map((strain: any) => (
              <option key={strain.id} value={strain.id}>
                {strain.name} ({strain.species})
              </option>
            ))}
          </select>
          {errors.strain_id && <p className="text-sm text-destructive mt-1">{errors.strain_id.message}</p>}
        </div>

        <div className="grid grid-cols-1 sm:grid-cols-2 gap-4">
          <div>
            <label className="text-sm font-medium">Grow Room / Shed</label>
            <select {...register('room_id', { valueAsNumber: true })} className="mt-1 w-full rounded-lg border px-4 py-3">
              <option value="">Select room</option>
              {rooms.map((room: any) => (
                <option key={room.id} value={room.id}>{room.name}</option>
              ))}
            </select>
            {errors.room_id && <p className="text-sm text-destructive mt-1">{errors.room_id.message}</p>}
          </div>

          <div>
            <label className="text-sm font-medium">Substrate Recipe</label>
            <select {...register('recipe_version_id', { valueAsNumber: true })} className="mt-1 w-full rounded-lg border px-4 py-3">
              <option value="">Select recipe</option>
              {recipes.map((recipe: any) => (
                <option key={recipe.id} value={recipe.latest_version_id ?? recipe.id}>
                  {recipe.name}
                </option>
              ))}
            </select>
            {errors.recipe_version_id && <p className="text-sm text-destructive mt-1">{errors.recipe_version_id.message}</p>}
          </div>
        </div>

        <div>
          <label className="text-sm font-medium">Batch Notes (Optional)</label>
          <input
            {...register('notes')}
            className="mt-1 w-full rounded-lg border px-4 py-3"
            placeholder="e.g. Gannoruwa DOA spawn batch, steamed 3.5 hrs"
          />
        </div>

        <div className="flex gap-4">
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
