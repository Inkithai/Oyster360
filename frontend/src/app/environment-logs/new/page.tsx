'use client'

import { useForm } from 'react-hook-form'
import { zodResolver } from '@hookform/resolvers/zod'
import { z } from 'zod'
import { useMutation } from '@tanstack/react-query'
import { apiRequest } from '@/lib/api'
import { useRouter } from 'next/navigation'
import { useToast } from '@/components/ui/use-toast'
import { Button } from '@/components/ui/button'

const envLogSchema = z.object({
  room_id: z.number().min(1),
  temperature: z.number().min(-10).max(60),
  humidity: z.number().min(0).max(100),
  co2: z.number().min(200).max(5000),
})

type EnvLogForm = z.infer<typeof envLogSchema>

export default function NewEnvLogPage() {
  const router = useRouter()
  const { toast } = useToast()

  const { register, handleSubmit, formState: { errors, isSubmitting } } = useForm<EnvLogForm>({
    resolver: zodResolver(envLogSchema),
  })

  const createLog = useMutation({
    mutationFn: (data: EnvLogForm) => apiRequest('/api/rooms/1/environment', {
      method: 'POST',
      body: JSON.stringify(data),
    }),
    onSuccess: () => {
      toast({ title: 'Environmental data recorded', variant: 'success' })
      router.push('/rooms')
    },
  })

  const onSubmit = (data: EnvLogForm) => createLog.mutate(data)

  return (
    <div className="max-w-xl">
      <h1 className="text-3xl font-semibold tracking-tight mb-8">Record Environmental Data</h1>

      <form onSubmit={handleSubmit(onSubmit)} className="space-y-6">
        <div>
          <label className="text-sm font-medium">Temperature (°C)</label>
          <input type="number" step="0.1" {...register('temperature', { valueAsNumber: true })} className="mt-1 w-full rounded-lg border px-4 py-3" />
          {errors.temperature && <p className="text-sm text-destructive mt-1">{errors.temperature.message}</p>}
        </div>

        <div>
          <label className="text-sm font-medium">Humidity (%)</label>
          <input type="number" step="0.1" {...register('humidity', { valueAsNumber: true })} className="mt-1 w-full rounded-lg border px-4 py-3" />
          {errors.humidity && <p className="text-sm text-destructive mt-1">{errors.humidity.message}</p>}
        </div>

        <div>
          <label className="text-sm font-medium">CO₂ (ppm)</label>
          <input type="number" {...register('co2', { valueAsNumber: true })} className="mt-1 w-full rounded-lg border px-4 py-3" />
          {errors.co2 && <p className="text-sm text-destructive mt-1">{errors.co2.message}</p>}
        </div>

        <div className="flex gap-4 pt-4">
          <Button type="button" variant="outline" onClick={() => router.back()}>Cancel</Button>
          <Button type="submit" disabled={isSubmitting}>
            {isSubmitting ? 'Saving...' : 'Save Reading'}
          </Button>
        </div>
      </form>
    </div>
  )
}