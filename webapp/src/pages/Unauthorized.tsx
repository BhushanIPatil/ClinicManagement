/**
 * Unauthorized Page
 * 
 * Shown when user doesn't have required permissions.
 */

import { useNavigate } from 'react-router-dom'
import { AlertCircle, ArrowLeft } from 'lucide-react'
import { Button } from '@/components/ui/button'
import { glassmorphism } from '@/lib/glassmorphism'
import { cn } from '@/lib/utils'

export default function Unauthorized() {
  const navigate = useNavigate()

  return (
    <div className="min-h-screen bg-gradient-to-br from-slate-900 via-purple-900 to-slate-900 flex items-center justify-center p-4">
      <div
        className={cn(
          glassmorphism('dark', true, true),
          'rounded-2xl p-8 max-w-md w-full text-center'
        )}
      >
        <AlertCircle className="w-16 h-16 text-destructive mx-auto mb-4" />
        <h1 className="text-3xl font-bold mb-2">Access Denied</h1>
        <p className="text-muted-foreground mb-6">
          You don't have permission to access this resource.
        </p>
        <Button onClick={() => navigate(-1)} variant="outline" className="gap-2">
          <ArrowLeft className="w-4 h-4" />
          Go Back
        </Button>
      </div>
    </div>
  )
}
