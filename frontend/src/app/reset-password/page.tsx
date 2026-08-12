'use client'

import { useState } from 'react'
import { useMutation } from '@tanstack/react-query'
import { apiRequest } from '@/lib/api'
import { useToast } from '@/components/ui/use-toast'
import { Button } from '@/components/ui/button'
import Link from 'next/link'
import { useSearchParams } from 'next/navigation'

export default function ResetPasswordPage() {
  const [newPassword, setNewPassword] = useState('')
  const [confirmPassword, setConfirmPassword] = useState('')
  const { toast } = useToast()
  const searchParams = useSearchParams()
  const token = searchParams.get('token')

  const resetPasswordMutation = useMutation({
    mutationFn: (data: { token: string; new_password: string }) =>
      apiRequest('/api/auth/reset-password', {
        method: 'POST',
        body: JSON.stringify(data),
      }),
    onSuccess: (data) => {
      toast({ 
        title: 'Password reset successful', 
        description: data.message,
        variant: 'success' 
      })
      // Redirect to login after 2 seconds
      setTimeout(() => {
        window.location.href = '/login'
      }, 2000)
    },
    onError: () => {
      toast({ 
        title: 'Error', 
        description: 'Failed to reset password. Please try again.',
        variant: 'error' 
      })
    },
  })

  const handleSubmit = (e: React.FormEvent) => {
    e.preventDefault()
    
    if (newPassword !== confirmPassword) {
      toast({ 
        title: 'Error', 
        description: 'Passwords do not match',
        variant: 'error' 
      })
      return
    }

    if (!token) {
      toast({ 
        title: 'Error', 
        description: 'Invalid reset link',
        variant: 'error' 
      })
      return
    }

    resetPasswordMutation.mutate({
      token,
      new_password: newPassword,
    })
  }

  if (!token) {
    return (
      <div className="min-h-screen flex items-center justify-center bg-muted/30 px-4">
        <div className="text-center">
          <h1 className="text-2xl font-semibold">Invalid Reset Link</h1>
          <p className="text-muted-foreground mt-2">This password reset link is invalid or has expired.</p>
          <Link href="/forgot-password" className="text-primary hover:underline mt-4 inline-block">
            Request a new reset link
          </Link>
        </div>
      </div>
    )
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
          <h1 className="text-3xl font-semibold tracking-tight">Reset Password</h1>
          <p className="text-muted-foreground mt-2">Enter your new password below</p>
        </div>

        <div className="bg-white p-8 rounded-2xl border">
          <form onSubmit={handleSubmit} className="space-y-4">
            <div>
              <label className="text-sm font-medium">New Password</label>
              <input
                type="password"
                value={newPassword}
                onChange={(e) => setNewPassword(e.target.value)}
                className="mt-1 w-full rounded-lg border px-4 py-3"
                placeholder="••••••••"
                required
                minLength={6}
              />
            </div>

            <div>
              <label className="text-sm font-medium">Confirm New Password</label>
              <input
                type="password"
                value={confirmPassword}
                onChange={(e) => setConfirmPassword(e.target.value)}
                className="mt-1 w-full rounded-lg border px-4 py-3"
                placeholder="••••••••"
                required
                minLength={6}
              />
            </div>

            <Button 
              type="submit" 
              className="w-full" 
              disabled={resetPasswordMutation.isPending}
            >
              {resetPasswordMutation.isPending ? 'Resetting...' : 'Reset Password'}
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