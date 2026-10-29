'use client'

import { useState } from 'react'
import { useForm } from 'react-hook-form'
import { zodResolver } from '@hookform/resolvers/zod'
import { z } from 'zod'
import { useMutation, useQuery } from '@tanstack/react-query'
import { apiRequest } from '@/lib/api'
import { useRouter } from 'next/navigation'
import { useToast } from '@/components/ui/use-toast'
import { Button } from '@/components/ui/button'

const harvestSchema = z.object({
  batch_id: z.number().min(1, 'Batch is required'),
  flush_number: z.number().min(1).max(10),
  quantity_kg: z.number().min(0.1, 'Quantity must be greater than 0'),
  unsold_kg: z.number().min(0),
  spoiled_kg: z.number().min(0),
  quality_score: z.number().min(0).max(100),
  selling_price: z.number().min(0),
  complete_batch: z.boolean(),
  notes: z.string().optional(),
})

type HarvestForm = z.infer<typeof harvestSchema>

export default function NewHarvestPage() {
  const router = useRouter()
  const { toast } = useToast()
  const [unit, setUnit] = useState<'kg' | 'g'>('kg')
  const [gramsValue, setGramsValue] = useState<string>('10000')
  const [selectedFlush, setSelectedFlush] = useState<number>(1)
  const [quantityKg, setQuantityKg] = useState<number>(10)
  const [pricePerKg, setPricePerKg] = useState<number>(650)

  const { data: batchList = [] } = useQuery({
    queryKey: ['batches'],
    queryFn: () => apiRequest('/api/batches'),
  })

  const { register, handleSubmit, setValue, formState: { errors, isSubmitting } } = useForm<HarvestForm>({
    resolver: zodResolver(harvestSchema),
    defaultValues: {
      batch_id: 1,
      flush_number: 1,
      quantity_kg: 10,
      unsold_kg: 0,
      spoiled_kg: 0,
      quality_score: 92,
      selling_price: 650,
      complete_batch: false,
    },
  })

  const estimatedLkr = Math.max(0, quantityKg) * pricePerKg

  const createHarvest = useMutation({
    mutationFn: (data: HarvestForm) =>
      apiRequest(`/api/batches/${data.batch_id}/harvest`, {
        method: 'POST',
        body: JSON.stringify(data),
      }),
    onSuccess: () => {
      toast({ title: 'Harvest flush recorded in LKR', variant: 'success' })
      router.push('/harvests')
    },
    onError: (err: Error) => {
      toast({ title: err.message || 'Failed to record harvest', variant: 'error' })
    },
  })

  const onSubmit = (data: HarvestForm) => createHarvest.mutate(data)

  return (
    <div className="max-w-xl mx-auto">
      <div className="mb-6">
        <span className="inline-block rounded-full bg-emerald-100 px-3 py-1 text-xs font-semibold text-emerald-800 mb-2">
          Mobile Quick-Entry • අස්වැන්න / அறுவடை
        </span>
        <h1 className="text-3xl font-semibold tracking-tight">Record Harvest (60-Second Entry)</h1>
        <p className="text-sm text-muted-foreground">
          Large tap buttons for recording harvest weight per batch and per flush in kg or grams
        </p>
      </div>

      <form onSubmit={handleSubmit(onSubmit)} className="space-y-6 rounded-2xl border bg-white p-6 shadow-xs">
        <div className="grid grid-cols-1 sm:grid-cols-2 gap-4">
          <div>
            <label className="text-sm font-medium">Select Batch</label>
            {Array.isArray(batchList) && batchList.length > 0 ? (
              <select
                {...register('batch_id', { valueAsNumber: true })}
                className="mt-1 w-full rounded-xl border px-4 py-3 text-base"
              >
                {batchList.map((b: any) => (
                  <option key={b.id} value={b.id}>
                    {b.batch_number} ({b.current_stage})
                  </option>
                ))}
              </select>
            ) : (
              <input
                type="number"
                {...register('batch_id', { valueAsNumber: true })}
                className="mt-1 w-full rounded-xl border px-4 py-3 text-base"
              />
            )}
          </div>

          <div>
            <label className="text-sm font-medium">Harvest Flush Number</label>
            <div className="mt-1 grid grid-cols-4 gap-2">
              {[1, 2, 3, 4].map((flush) => (
                <button
                  key={flush}
                  type="button"
                  onClick={() => {
                    setSelectedFlush(flush)
                    setValue('flush_number', flush)
                  }}
                  className={`rounded-xl border py-3 text-sm font-semibold ${
                    selectedFlush === flush ? 'bg-black text-white' : 'bg-gray-50 hover:bg-gray-100'
                  }`}
                >
                  Flush {flush}
                </button>
              ))}
            </div>
          </div>
        </div>

        <div>
          <div className="flex items-center justify-between">
            <label className="text-sm font-medium">Harvested Weight ({unit})</label>
            <div className="flex rounded-lg border p-0.5 text-xs">
              <button
                type="button"
                onClick={() => setUnit('kg')}
                className={`rounded-md px-2.5 py-1 font-medium ${unit === 'kg' ? 'bg-black text-white' : ''}`}
              >
                Kilograms (kg)
              </button>
              <button
                type="button"
                onClick={() => {
                  setUnit('g')
                  setGramsValue(String(Math.round((quantityKg || 0) * 1000)))
                }}
                className={`rounded-md px-2.5 py-1 font-medium ${unit === 'g' ? 'bg-black text-white' : ''}`}
              >
                Grams (g)
              </button>
            </div>
          </div>

          {unit === 'kg' ? (
            <input
              type="number"
              step="0.1"
              {...register('quantity_kg', {
                valueAsNumber: true,
                onChange: (e) => setQuantityKg(Number(e.target.value) || 0),
              })}
              className="mt-1 w-full rounded-xl border px-4 py-3 text-lg font-semibold"
            />
          ) : (
            <input
              type="number"
              step="50"
              value={gramsValue}
              onChange={(e) => {
                setGramsValue(e.target.value)
                const g = Number(e.target.value) || 0
                const kg = Number((g / 1000).toFixed(2))
                setQuantityKg(kg)
                setValue('quantity_kg', kg)
              }}
              placeholder="e.g. 12500 (grams)"
              className="mt-1 w-full rounded-xl border px-4 py-3 text-lg font-semibold"
            />
          )}

          {/* One-tap weight presets */}
          <div className="mt-2 flex flex-wrap gap-2">
            {[2, 5, 10, 20, 50].map((kg) => (
              <button
                key={kg}
                type="button"
                onClick={() => {
                  setQuantityKg(kg)
                  setValue('quantity_kg', kg)
                  setGramsValue(String(kg * 1000))
                }}
                className="rounded-lg border bg-gray-50 px-3 py-1.5 text-xs font-medium hover:bg-gray-100"
              >
                {kg} kg ({kg * 5} × 200g packs)
              </button>
            ))}
          </div>
          {errors.quantity_kg && <p className="text-sm text-destructive mt-1">{errors.quantity_kg.message}</p>}
        </div>

        <div className="grid grid-cols-1 sm:grid-cols-2 gap-4">
          <div>
            <label className="text-sm font-medium">Selling Price (Rs/kg)</label>
            <input
              type="number"
              step="10"
              {...register('selling_price', {
                valueAsNumber: true,
                onChange: (e) => setPricePerKg(Number(e.target.value) || 0),
              })}
              className="mt-1 w-full rounded-xl border px-4 py-3 text-base"
            />
            <div className="mt-1.5 flex gap-1.5">
              {[500, 600, 650, 800].map((rs) => (
                <button
                  key={rs}
                  type="button"
                  onClick={() => {
                    setPricePerKg(rs)
                    setValue('selling_price', rs)
                  }}
                  className="rounded border px-2 py-1 text-xs hover:bg-gray-100"
                >
                  Rs.{rs}
                </button>
              ))}
            </div>
          </div>

          <div>
            <label className="text-sm font-medium">Quality Score (0-100)</label>
            <input
              type="number"
              {...register('quality_score', { valueAsNumber: true })}
              className="mt-1 w-full rounded-xl border px-4 py-3 text-base"
            />
          </div>
        </div>

        <div className="grid grid-cols-2 gap-4">
          <div>
            <label className="text-xs font-medium text-muted-foreground">Unsold Stock (kg)</label>
            <input
              type="number"
              step="0.1"
              {...register('unsold_kg', { valueAsNumber: true })}
              className="mt-1 w-full rounded-xl border px-3 py-2 text-sm"
            />
          </div>
          <div>
            <label className="text-xs font-medium text-muted-foreground">Spoiled / Discarded (kg)</label>
            <input
              type="number"
              step="0.1"
              {...register('spoiled_kg', { valueAsNumber: true })}
              className="mt-1 w-full rounded-xl border px-3 py-2 text-sm"
            />
          </div>
        </div>

        <div className="flex items-center justify-between rounded-xl bg-emerald-50 border border-emerald-200 p-4">
          <div>
            <div className="text-xs text-emerald-900">Estimated Flush Value (LKR)</div>
            <div className="text-2xl font-bold text-emerald-800">Rs. {estimatedLkr.toLocaleString()}</div>
          </div>
          <label className="flex items-center gap-2 text-xs font-medium">
            <input type="checkbox" {...register('complete_batch')} className="h-4 w-4" />
            Final flush (mark batch completed)
          </label>
        </div>

        <div className="flex gap-4 pt-2">
          <Button type="button" variant="outline" onClick={() => router.back()}>Cancel</Button>
          <Button type="submit" disabled={isSubmitting} className="flex-1 bg-emerald-700 hover:bg-emerald-800">
            {isSubmitting ? 'Recording...' : 'Record Harvest'}
          </Button>
        </div>
      </form>
    </div>
  )
}
