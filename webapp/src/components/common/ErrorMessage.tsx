/**
 * Error Message Component
 * 
 * Reusable error display with consistent styling.
 */

import { AlertCircle, X } from 'lucide-react'
import { Button } from '@/components/ui/button'
import { cn } from '@/lib/utils'

interface ErrorMessageProps {
  message: string
  onDismiss?: () => void
  className?: string
}

export function ErrorMessage({ message, onDismiss, className }: ErrorMessageProps) {
  return (
    <div
      className={cn(
        'flex items-start gap-3 p-4 rounded-lg bg-destructive/10 border border-destructive/20',
        className
      )}
    >
      <AlertCircle className="w-5 h-5 text-destructive flex-shrink-0 mt-0.5" />
      <div className="flex-1">
        <p className="text-sm text-destructive font-medium">{message}</p>
      </div>
      {onDismiss && (
        <Button
          variant="ghost"
          size="sm"
          onClick={onDismiss}
          className="h-6 w-6 p-0 text-destructive hover:text-destructive"
        >
          <X className="w-4 h-4" />
        </Button>
      )}
    </div>
  )
}
