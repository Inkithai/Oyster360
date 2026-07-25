'use client'

import { useForm } from 'react-hook-form'
import { zodResolver } from '@hookform/resolvers/zod'
import { z } from 'zod'
import { useMutation } from '@tanstack/react-query'
import { apiRequest } from '@/lib/api'
import { useRouter, useParams } from 'next/navigation'
import { useToast } from '@/components/ui/use-toast'
import { Button } from '@/components/ui/button'

const versionSchema = z.object({
  hydration_percentage: z.number().min(0).max(100),
  spawn_ratio: z.number().min(1).max(20),
  notes: z.string().optional(),
})

type VersionForm = z.infer<typeof versionSchema>

export default function NewRecipeVersionPage() {
  const router = useRouter()
  const params = useParams()
  const { toast } = useToast()
  const recipeId = params.id as string

  const { register, handleSubmit, formState: { errors, isSubmitting } } = useForm<VersionForm>({
    resolver: zodResolver(versionSchema),
    defaultValues: { hydration_percentage: 65, spawn_ratio: 5 }
  })

  const createVersion = useMutation({
    mutationFn: (data: VersionForm) => apiRequest(`/api/recipes/${recipeId}/versions`, {
      method: 'POST',
      body: JSON.stringify(data),
    }),
    onSuccess: () => {
      toast({ title: 'New version created', variant: 'success' })
      router.push('/recipes')
    },
  })

  const onSubmit = (data: VersionForm) => createVersion.mutate(data)

  return (
    <div className="max-w-xl">
      <h1 className="text-3xl font-semibold tracking-tight mb-8">Create New Recipe Version</h1>

      <form onSubmit={handleSubmit(onSubmit)} className="space-y-6">
        <div>
          <label className="text-sm font-medium">Hydration Percentage</label>
          <input type="number" {...register('hydration_percentage', { valueAsNumber: true })} className="mt-1 w-full rounded-lg border px-4 py-3" />
          {errors.hydration_percentage && <p className="text-sm text-destructive mt-1">{errors.hydration_percentage.message}</p>}
        </div>

        <div>
          <label className="text-sm font-medium">Spawn Ratio (%)</label>
          <input type="number" {...register('spawn_ratio', { valueAsNumber: true })} className="mt-1 w-full rounded-lg border px-4 py-3" />
          {errors.spawn_ratio && <p className="text-sm text-destructive mt-1">{errors.spawn_ratio.message}</p>}
        </div>

        <div>
          <label className="text-sm font-medium">Notes</label>
          <textarea {...register('notes')} className="mt-1 w-full rounded-lg border px-4 py-3 h-24" />
        </div>

        <div className="flex gap-4 pt-4">
          <Button type="button" variant="outline" onClick={() => router.back()}>Cancel</Button>
          <Button type="submit" disabled={isSubmitting}>
            {isSubmitting ? 'Creating...' : 'Create Version'}
          </Button>
        </div>
      </form>
    </div>
  )
}