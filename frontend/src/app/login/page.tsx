'use client'

import { useForm } from 'react-hook-form'
import { zodResolver } from '@hookform/resolvers/zod'
import { z } from 'zod'
import { useMutation } from '@tanstack/react-query'
import { apiRequest } from '@/lib/api'
import { useRouter } from 'next/navigation'
import { useToast } from '@/components/ui/use-toast'

const loginSchema = z.object({
  email: z.string().email('Invalid email address'),
  password: z.string().min(6, 'Password must be at least 6 characters'),
})

type LoginForm = z.infer<typeof loginSchema>

export default function LoginPage() {
  const router = useRouter()
  const { toast } = useToast()

  const { register, handleSubmit, formState: { errors, isSubmitting } } = useForm<LoginForm>({
    resolver: zodResolver(loginSchema),
  })

  const loginMutation = useMutation({
    mutationFn: (data: LoginForm) => apiRequest('/api/auth/login', {
      method: 'POST',
      body: JSON.stringify(data),
    }),
    onSuccess: (data) => {
      localStorage.setItem('token', data.access_token)
      toast({ title: 'Login successful', variant: 'success' })
      router.push('/dashboard')
    },
    onError: () => {
      toast({ title: 'Login failed', description: 'Invalid credentials', variant: 'error' })
    },
  })

  const onSubmit = (data: LoginForm) => {
    loginMutation.mutate(data)
  }

  return (
    <div className="min-h-screen flex items-center justify-center bg-muted/30">
      <div className="w-full max-w-md space-y-8 p-8">
        <div className="text-center">
          <h1 className="text-3xl font-semibold">Oyster360</h1>
          <p className="text-muted-foreground mt-2">Sign in to your account</p>
        </div>

        <form onSubmit={handleSubmit(onSubmit)} className="space-y-4">
          <div>
            <label className="text-sm font-medium">Email</label>
            <input
              {...register('email')}
              type="email"
              className="mt-1 w-full rounded-lg border px-4 py-3"
              placeholder="admin@myco.farm"
            />
            {errors.email && <p className="text-sm text-destructive mt-1">{errors.email.message}</p>}
          </div>

          <div>
            <label className="text-sm font-medium">Password</label>
            <input
              {...register('password')}
              type="password"
              className="mt-1 w-full rounded-lg border px-4 py-3"
              placeholder="••••••••"
            />
            {errors.password && <p className="text-sm text-destructive mt-1">{errors.password.message}</p>}
          </div>

          <button
            type="submit"
            disabled={isSubmitting}
            className="w-full bg-black text-white py-3 rounded-lg font-medium disabled:opacity-50"
          >
            {isSubmitting ? 'Signing in...' : 'Sign In'}
          </button>

          <div className="text-center">
            <a href="/forgot-password" className="text-sm text-primary hover:underline">
              Forgot your password?
            </a>
          </div>
        </form>
      </div>
    </div>
  )
}