/**
 * useRequireRole Hook
 * 
 * Hook that checks if user has required role(s).
 */

import { useEffect } from 'react'
import { useNavigate } from 'react-router-dom'
import { useAuth } from './useAuth'
import type { UserRole } from '@/types/auth.types'

export function useRequireRole(requiredRoles: UserRole | UserRole[]) {
  const { user, isAuthenticated, isLoading } = useAuth()
  const navigate = useNavigate()

  const roles = Array.isArray(requiredRoles) ? requiredRoles : [requiredRoles]

  useEffect(() => {
    if (!isLoading) {
      if (!isAuthenticated) {
        navigate('/login', { replace: true })
        return
      }

      if (user) {
        const userRoles = user.role_names.map((r) => r.toUpperCase())
        const hasRequiredRole = roles.some((role) =>
          userRoles.includes(role.toUpperCase())
        )

        if (!hasRequiredRole) {
          navigate('/unauthorized', { replace: true })
        }
      }
    }
  }, [user, isAuthenticated, isLoading, roles, navigate])

  return { user, isAuthenticated, isLoading }
}
