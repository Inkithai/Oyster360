'use client'

import * as React from 'react'
import { useFormContext } from 'react-hook-form'
import { cn } from '@/lib/utils'

export const Form = ({ children, ...props }: React.FormHTMLAttributes<HTMLFormElement>) => {
  return <form {...props}>{children}</form>
}

export const FormField = ({ name, children }: { name: string; children: React.ReactNode }) => {
  const { formState: { errors } } = useFormContext()
  const error = errors[name]

  return (
    <div className="space-y-2">
      {children}
      {error && <p className="text-sm text-destructive">{error.message as string}</p>}
    </div>
  )
}

export const FormLabel = ({ children, ...props }: React.LabelHTMLAttributes<HTMLLabelElement>) => (
  <label className="text-sm font-medium" {...props}>{children}</label>
)

export const FormInput = React.forwardRef<HTMLInputElement, React.InputHTMLAttributes<HTMLInputElement>>(
  ({ className, ...props }, ref) => (
    <input
      ref={ref}
      className={cn("w-full rounded-lg border px-4 py-3 text-sm", className)}
      {...props}
    />
  )
)
FormInput.displayName = 'FormInput'