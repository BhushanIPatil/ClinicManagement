/**
 * Role-Based Route Component
 * 
 * Wraps routes that require specific role(s).
 */

import { ReactNode } from 'react'
import { Navigate } from 'react-router-dom'
import { useAuth } from '@/hooks/useAuth'
import type { UserRole } from '@/types/auth.types'

interface RoleRouteProps {
  children: ReactNode
  requiredRoles: UserRole | UserRole[]
}

export function RoleRoute({ children, requiredRoles }: RoleRouteProps) {
  const { user, isAuthenticated, isLoading } = useAuth()

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
