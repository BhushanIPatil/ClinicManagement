/**
 * Auth Store
 * 
 * Centralized authentication state management.
 * Uses simple state pattern - can be replaced with Zustand/Redux if needed.
 */

import { createContext, useContext, useState, useEffect, ReactNode } from 'react'
import { authService } from '@/services/auth.service'
import type { User, LoginRequest, RegisterRequest } from '@/types/auth.types'
import type { ApiError } from '@/services/api.service'

interface AuthState {
  user: User | null
  isAuthenticated: boolean
  isLoading: boolean
  error: string | null
}

interface AuthContextValue extends AuthState {
  login: (credentials: LoginRequest) => Promise<void>
  register: (data: RegisterRequest) => Promise<void>
  logout: () => void
  refreshUser: () => Promise<void>
  clearError: () => void
}

const AuthContext = createContext<AuthContextValue | undefined>(undefined)

export function AuthProvider({ children }: { children: ReactNode }) {
  const [state, setState] = useState<AuthState>({
    user: null,
    isAuthenticated: false,
    isLoading: true,
    error: null,
  })

  /**
   * Initialize auth state from storage
   */
  useEffect(() => {
    function initializeAuth() {
      try {
        const storedUser = authService.getStoredUser()
        if (storedUser && authService.isAuthenticated()) {
          setState({
            user: storedUser,
            isAuthenticated: true,
            isLoading: false,
            error: null,
          })
        } else {
          setState({
            user: null,
            isAuthenticated: false,
            isLoading: false,
            error: null,
          })
        }
      } catch {
        setState({
          user: null,
          isAuthenticated: false,
          isLoading: false,
          error: null,
        })
      }
    }

    initializeAuth()
  }, [])

  /**
   * Login
   */
  const login = async (credentials: LoginRequest): Promise<void> => {
    setState((prev) => ({ ...prev, isLoading: true, error: null }))

    try {
      const response = await authService.login(credentials)
      setState({
        user: response.user,
        isAuthenticated: true,
        isLoading: false,
        error: null,
      })
    } catch (error: any) {
      const errorMessage =
        error?.detail || error?.message || 'Login failed. Please check your credentials.'
      setState({
        user: null,
        isAuthenticated: false,
        isLoading: false,
        error: errorMessage,
      })
      throw error
    }
  }

  /**
   * Register
   */
  const register = async (data: RegisterRequest): Promise<void> => {
    setState((prev) => ({ ...prev, isLoading: true, error: null }))

    try {
      const response = await authService.register(data)
      setState({
        user: response.user,
        isAuthenticated: true,
        isLoading: false,
        error: null,
      })
    } catch (error: any) {
      const errorMessage =
        error?.detail || error?.message || 'Registration failed. Please try again.'
      setState({
        user: null,
        isAuthenticated: false,
        isLoading: false,
        error: errorMessage,
      })
      throw error
    }
  }

  /**
   * Logout
   */
  const logout = (): void => {
    authService.logout()
    setState({
      user: null,
      isAuthenticated: false,
      isLoading: false,
      error: null,
    })
  }

  /**
   * Refresh user data
   */
  const refreshUser = async (): Promise<void> => {
    try {
      const user = await authService.getCurrentUser()
      setState((prev) => ({
        ...prev,
        user,
        isAuthenticated: true,
        error: null,
      }))
    } catch (error: any) {
      // If refresh fails, user might be logged out
      logout()
    }
  }

  /**
   * Clear error
   */
  const clearError = (): void => {
    setState((prev) => ({ ...prev, error: null }))
  }

  const value: AuthContextValue = {
    ...state,
    login,
    register,
    logout,
    refreshUser,
    clearError,
  }

  return <AuthContext.Provider value={value}>{children}</AuthContext.Provider>
}

/**
 * Hook to use auth context
 */
export function useAuth(): AuthContextValue {
  const context = useContext(AuthContext)
  if (context === undefined) {
    throw new Error('useAuth must be used within an AuthProvider')
  }
  return context
}
