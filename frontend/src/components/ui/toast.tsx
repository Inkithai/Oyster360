"use client"

import * as React from "react"
import { X } from "lucide-react"
import { cn } from "@/lib/utils"

interface ToastProps {
  id: string
  title: string
  description?: string
  variant?: "default" | "success" | "error" | "warning"
  onClose: (id: string) => void
}

export function Toast({ id, title, description, variant = "default", onClose }: ToastProps) {
  const variantStyles = {
    default: "bg-background border",
    success: "bg-green-50 border-green-200 text-green-900",
    error: "bg-red-50 border-red-200 text-red-900",
    warning: "bg-amber-50 border-amber-200 text-amber-900",
  }

  return (
    <div className={cn(
      "flex items-start gap-3 rounded-xl border p-4 shadow-lg w-full max-w-sm",
      variantStyles[variant]
    )}>
      <div className="flex-1">
        <div className="font-semibold text-sm">{title}</div>
        {description && (
          <div className="text-sm mt-1 text-muted-foreground">{description}</div>
        )}
      </div>
      <button onClick={() => onClose(id)} className="text-muted-foreground hover:text-foreground">
        <X className="h-4 w-4" />
      </button>
    </div>
  )
}