'use client'

import { ReactNode } from 'react'
import { FieldError } from 'react-hook-form'

interface FormFieldProps {
  label: string
  error?: FieldError
  children: ReactNode
}

export function FormField({ label, error, children }: FormFieldProps) {
  return (
    <div className="space-y-2">
      <label className="text-sm font-medium">{label}</label>
      {children}
      {error && <p className="text-sm text-destructive">{error.message}</p>}
    </div>
  )
}