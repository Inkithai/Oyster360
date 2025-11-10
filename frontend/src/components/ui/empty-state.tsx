import { ReactNode } from 'react'
import { Button } from './button'

interface EmptyStateProps {
  icon?: ReactNode
  title: string
  description?: string
  action?: ReactNode
  actionLabel?: string
  onAction?: () => void
}

export function EmptyState({ 
  icon, 
  title, 
  description, 
  action, 
  actionLabel, 
  onAction 
}: EmptyStateProps) {
  return (
    <div className="flex flex-col items-center justify-center py-16 text-center px-4">
      {icon && (
        <div className="mb-6 text-muted-foreground opacity-50">
          {icon}
        </div>
      )}
      <h3 className="text-xl font-semibold mb-2">{title}</h3>
      {description && (
        <p className="text-muted-foreground max-w-sm mb-6">{description}</p>
      )}
      {(action || (actionLabel && onAction)) && (
        <div className="mt-2">
          {action || (
            <Button onClick={onAction}>{actionLabel}</Button>
          )}
        </div>
      )}
    </div>
  )
}