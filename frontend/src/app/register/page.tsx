'use client'

import { useForm } from 'react-hook-form'
import { zodResolver } from '@hookform/resolvers/zod'
import { z } from 'zod'
import { useMutation } from '@tanstack/react-query'
import { apiRequest } from '@/lib/api'
import { useRouter } from 'next/navigation'
import { useToast } from '@/components/ui/use-toast'
import { Button } from '@/components/ui/button'
import Link from 'next/link'

const registerSchema = z.object({
  name: z.string().min(2, 'Name is required'),
  email: z.string().email('Invalid email address'),
  password: z.string().min(6, 'Password must be at least 6 characters'),
  farmName: z.string().min(2, 'Farm name is required'),
})

type RegisterForm = z.infer<typeof registerSchema>

export default function RegisterPage() {
  const router = useRouter()
  const { toast } = useToast()

  const { register, handleSubmit, formState: { errors, isSubmitting } } = useForm<RegisterForm>({
    resolver: zodResolver(registerSchema),
  })

  const registerMutation = useMutation({
    mutationFn: (data: RegisterForm) => apiRequest('/api/auth/register', {
      method: 'POST',
      body: JSON.stringify({
        name: data.name,
        email: data.email,
        password: data.password,
        role: 'FARM_MANAGER', // Default role
      }),
    }),
    onSuccess: () => {
      toast({ title: 'Account created successfully', variant: 'success' })
      router.push('/login')
    },
    onError: () => {
      toast({ title: 'Registration failed', variant: 'error' })
    },
  })

  const onSubmit = (data: RegisterForm) => {
    registerMutation.mutate(data)
  }

  return (
    <div className="min-h-screen flex items-center justify-center bg-muted/30 px-4">
      <div className="w-full max-w-md space-y-8">
        <div className="text-center">
          <div className="flex justify-center mb-4">
            <div className="h-12 w-12 rounded-2xl bg-black flex items-center justify-center">
              <span className="text-white font-bold text-2xl">O</span>
            </div>
          </div>
          <h1 className="text-3xl font-semibold tracking-tight">Create your account</h1>
          <p className="text-muted-foreground mt-2">Start your 14-day free trial</p>
        </div>

        <div className="bg-white p-8 rounded-2xl border">
          <form onSubmit={handleSubmit(onSubmit)} className="space-y-4">
            <div>
              <label className="text-sm font-medium">Full Name</label>
              <input {...register('name')} className="mt-1 w-full rounded-lg border px-4 py-3" />
              {errors.name && <p className="text-sm text-destructive mt-1">{errors.name.message}</p>}
            </div>

            <div>
              <label className="text-sm font-medium">Email</label>
              <input type="email" {...register('email')} className="mt-1 w-full rounded-lg border px-4 py-3" />
              {errors.email && <p className="text-sm text-destructive mt-1">{errors.email.message}</p>}
            </div>

            <div>
              <label className="text-sm font-medium">Password</label>
              <input type="password" {...register('password')} className="mt-1 w-full rounded-lg border px-4 py-3" />
              {errors.password && <p className="text-sm text-destructive mt-1">{errors.password.message}</p>}
            </div>

            <div>
              <label className="text-sm font-medium">Farm Name</label>
              <input {...register('farmName')} className="mt-1 w-full rounded-lg border px-4 py-3" />
              {errors.farmName && <p className="text-sm text-destructive mt-1">{errors.farmName.message}</p>}
            </div>

            <Button type="submit" className="w-full" disabled={isSubmitting}>
              {isSubmitting ? 'Creating account...' : 'Create Account'}
            </Button>
          </form>
        </div>

        <p className="text-center text-sm text-muted-foreground">
          Already have an account?{' '}
          <Link href="/login" className="text-primary hover:underline">Sign in</Link>
        </p>
      </div>
    </div>
  )
}