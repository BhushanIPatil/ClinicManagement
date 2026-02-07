/**
 * Role-Based Route Component
 *
 * Access is controlled only by clinic admin settings for feature-gated paths.
 * - Feature-gated (/patients, /work-queue, /payroll, /finance): allow if featureAccess[featureKey] is true (no role check).
 * - Other paths: require one of requiredRoles.
 */

import { ReactNode } from 'react'
import { Navigate, useLocation } from 'react-router-dom'
import { useAuth } from '@/hooks/useAuth'
import type { UserRole } from '@/types/auth.types'

const PATH_TO_FEATURE: Record<string, string> = {
  '/patients': 'PATIENTS',
  '/work-queue': 'WORK_QUEUE',
  '/payroll': 'PAYROLL',
  '/finance': 'FINANCE',
}

interface RoleRouteProps {
  children: ReactNode
  requiredRoles: UserRole | UserRole[]
}

export function RoleRoute({ children, requiredRoles }: RoleRouteProps) {
  const { user, isAuthenticated, isLoading, featureAccess } = useAuth()
  const location = useLocation()
  const path = location.pathname

  if (isLoading) {
    return (
      <div className="flex items-center justify-center min-h-screen">
        <div className="text-center">
          <div className="w-16 h-16 border-4 border-primary border-t-transparent rounded-full animate-spin mx-auto mb-4" />
          <p className="text-muted-foreground">Loading...</p>
        </div>
      </div>
    )
  }

  if (!isAuthenticated) {
    return <Navigate to="/login" replace />
  }

  if (!user) {
    return <Navigate to="/login" replace />
  }

  const featureKey = PATH_TO_FEATURE[path]
  if (featureKey) {
    if (featureAccess == null || !featureAccess[featureKey]) {
      return <Navigate to="/unauthorized" replace />
    }
    return <>{children}</>
  }

  const roles = Array.isArray(requiredRoles) ? requiredRoles : [requiredRoles]
  const userRoles = user.role_names.map((r) => r.toUpperCase())
  const hasRequiredRole = roles.some((role) =>
    userRoles.includes(role.toUpperCase())
  )

  if (!hasRequiredRole) {
    return <Navigate to="/unauthorized" replace />
  }

  return <>{children}</>
}
