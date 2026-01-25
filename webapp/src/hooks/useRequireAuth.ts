/**
 * useRequireAuth Hook
 * 
 * Hook that redirects to login if user is not authenticated.
 */

import { useEffect } from 'react'
import { useNavigate } from 'react-router-dom'
import { useAuth } from './useAuth'

export function useRequireAuth() {
  const { isAuthenticated, isLoading } = useAuth()
  const navigate = useNavigate()

  useEffect(() => {
    if (!isLoading && !isAuthenticated) {
      navigate('/login', { replace: true })
    }
  }, [isAuthenticated, isLoading, navigate])

  return { isAuthenticated, isLoading }
}
