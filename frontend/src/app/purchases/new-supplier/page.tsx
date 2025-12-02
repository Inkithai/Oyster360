'use client'

import { useForm } from 'react-hook-form'
import { zodResolver } from '@hookform/resolvers/zod'
import { z } from 'zod'
import { useMutation } from '@tanstack/react-query'
import { apiRequest } from '@/lib/api'
import { useRouter } from 'next/navigation'
import { useToast } from '@/components/ui/use-toast'
import { Button } from '@/components/ui/button'

const supplierSchema = z.object({
  name: z.string().min(2, 'Name is required'),
  contact_person: z.string().optional(),
  phone: z.string().optional(),
  email: z.string().email().optional(),
})

type SupplierForm = z.infer<typeof supplierSchema>

export default function NewSupplierPage() {
  const router = useRouter()
  const { toast } = useToast()

  const { register, handleSubmit, formState: { errors, isSubmitting } } = useForm<SupplierForm>({
    resolver: zodResolver(supplierSchema),
  })

  const createSupplier = useMutation({
    mutationFn: (data: SupplierForm) => apiRequest('/api/purchases/suppliers', {
      method: 'POST',
      body: JSON.stringify(data),
    }),
    onSuccess: () => {
      toast({ title: 'Supplier created', variant: 'success' })
      router.push('/purchases')
    },
  })

  const onSubmit = (data: SupplierForm) => createSupplier.mutate(data)

  return (
    <div className="max-w-xl">
      <h1 className="text-3xl font-semibold tracking-tight mb-8">Add New Supplier</h1>

      <form onSubmit={handleSubmit(onSubmit)} className="space-y-6">
        <div>
          <label className="text-sm font-medium">Supplier Name</label>
          <input {...register('name')} className="mt-1 w-full rounded-lg border px-4 py-3" />
          {errors.name && <p className="text-sm text-destructive mt-1">{errors.name.message}</p>}
        </div>

        <div>
          <label className="text-sm font-medium">Contact Person</label>
          <input {...register('contact_person')} className="mt-1 w-full rounded-lg border px-4 py-3" />
        </div>

        <div className="grid grid-cols-2 gap-4">
          <div>
            <label className="text-sm font-medium">Phone</label>
            <input {...register('phone')} className="mt-1 w-full rounded-lg border px-4 py-3" />
          </div>
          <div>
            <label className="text-sm font-medium">Email</label>
            <input {...register('email')} type="email" className="mt-1 w-full rounded-lg border px-4 py-3" />
            {errors.email && <p className="text-sm text-destructive mt-1">{errors.email.message}</p>}
          </div>
        </div>

        <div className="flex gap-4 pt-4">
          <Button type="button" variant="outline" onClick={() => router.back()}>Cancel</Button>
          <Button type="submit" disabled={isSubmitting}>
            {isSubmitting ? 'Creating...' : 'Add Supplier'}
          </Button>
        </div>
      </form>
    </div>
  )
}