'use client'

import { useState } from 'react'
import { useMutation } from '@tanstack/react-query'
import { apiRequest } from '@/lib/api'
import { useToast } from '@/components/ui/use-toast'
import { Button } from '@/components/ui/button'
import Link from 'next/link'

export default function ForgotPasswordPage() {
  const [email, setEmail] = useState('')
  const { toast } = useToast()

  const forgotPasswordMutation = useMutation({
    mutationFn: (email: string) => 
      apiRequest('/api/auth/forgot-password', {
        method: 'POST',
        body: JSON.stringify({ email }),
      }),
    onSuccess: (data) => {
      toast({ 
        title: 'Request submitted', 
        description: data.message,
        variant: 'success' 
      })
      setEmail('')
    },
    onError: () => {
      toast({ 
        title: 'Error', 
        description: 'Something went wrong. Please try again.',
        variant: 'error' 
      })
    },
  })

  const handleSubmit = (e: React.FormEvent) => {
    e.preventDefault()
    if (email) {
      forgotPasswordMutation.mutate(email)
    }
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
          <h1 className="text-3xl font-semibold tracking-tight">Forgot Password?</h1>
          <p className="text-muted-foreground mt-2">
            Enter your email and we&apos;ll send you a reset link
          </p>
        </div>

        <div className="bg-white p-8 rounded-2xl border">
          <form onSubmit={handleSubmit} className="space-y-4">
            <div>
              <label className="text-sm font-medium">Email Address</label>
              <input
                type="email"
                value={email}
                onChange={(e) => setEmail(e.target.value)}
                className="mt-1 w-full rounded-lg border px-4 py-3"
                placeholder="your@email.com"
                required
              />
            </div>

            <Button 
              type="submit" 
              className="w-full" 
              disabled={forgotPasswordMutation.isPending}
            >
              {forgotPasswordMutation.isPending ? 'Sending...' : 'Send Reset Link'}
            </Button>
          </form>
        </div>

        <p className="text-center text-sm text-muted-foreground">
          Remember your password?{' '}
          <Link href="/login" className="text-primary hover:underline">
            Back to Sign In
          </Link>
        </p>
      </div>
    </div>
  )
}