/**
 * Authentication Service
 * 
 * Handles all authentication-related API calls.
 * No business logic - pure API communication.
 */

import { apiService } from './api.service'
import { tokenStorage } from '@/lib/token-storage'
import type {
  LoginRequest,
  RegisterRequest,
  AuthResponse,
  User,
  RefreshTokenRequest,
  Tokens,
} from '@/types/auth.types'

/** Shape returned by POST /auth/login */
interface LoginApiResponse {
  access_token: string
  token_type: string
  expires_in: number
  user: Record<string, unknown> & { roles?: string[] }
  refresh_token?: string
}

/** Normalize API user to frontend User (API sends "roles", frontend uses "role_names"; primary_clinic_* from login). */
function normalizeUser(apiUser: Record<string, unknown> & { roles?: string[] }): User {
  const role_names = apiUser.roles ?? (apiUser.role_names as string[] | undefined) ?? []
  return {
    ...apiUser,
    role_names: Array.isArray(role_names) ? role_names : [],
    is_verified: (apiUser.is_verified as boolean) ?? false,
    created_at: (apiUser.created_at as string) ?? new Date().toISOString(),
    updated_at: (apiUser.updated_at as string) ?? new Date().toISOString(),
    primary_clinic_id: (apiUser.primary_clinic_id as string | null | undefined) ?? null,
    primary_clinic_name: (apiUser.primary_clinic_name as string | null | undefined) ?? null,
  } as User
}

class AuthService {
  /**
   * Login user
   * Backend returns { access_token, token_type, expires_in, user } — normalize and store.
   */
  async login(credentials: LoginRequest): Promise<AuthResponse> {
    const response = await apiService.post<LoginApiResponse>(
      '/auth/login',
      credentials,
      false // Don't include auth token for login
    )

    const user = normalizeUser(response.user)

    // Store login details in localStorage and in a cookie as JSON
    tokenStorage.setLoginDetailsCookie({
      user: user as unknown as Record<string, unknown>,
      access_token: response.access_token,
      refresh_token: response.refresh_token ?? '',
    })

    return {
      user,
      tokens: {
        access_token: response.access_token,
        refresh_token: '', // backend does not provide refresh token
        token_type: response.token_type ?? 'bearer',
      },
    }
  }

  /**
   * Register new user
   */
  async register(data: RegisterRequest): Promise<AuthResponse> {
    const response = await apiService.post<AuthResponse>(
      '/auth/register',
      data,
      false // Don't include auth token for registration
    )

    // Store tokens and user
    tokenStorage.setTokens(response.tokens)
    tokenStorage.setUser(response.user)

    return response
  }

  /**
   * Logout user
   */
  logout(): void {
    tokenStorage.clear()
  }

  /**
   * Refresh access token
   */
  async refreshToken(): Promise<Tokens> {
    const refreshToken = tokenStorage.getRefreshToken()
    if (!refreshToken) {
      throw new Error('No refresh token available')
    }

    const request: RefreshTokenRequest = { refresh_token: refreshToken }
    const tokens = await apiService.post<Tokens>(
      '/auth/refresh',
      request,
      false // Don't include auth token for refresh
    )

    // Update stored tokens
    tokenStorage.setTokens(tokens)

    return tokens
  }

  /**
   * Get current user
   */
  async getCurrentUser(): Promise<User> {
    return apiService.get<User>('/auth/me')
  }

  /**
   * Check if user is authenticated
   */
  isAuthenticated(): boolean {
    return tokenStorage.isAuthenticated()
  }

  /**
   * Get stored user
   */
  getStoredUser(): User | null {
    return tokenStorage.getUser()
  }

  /**
   * Get stored access token
   */
  getAccessToken(): string | null {
    return tokenStorage.getAccessToken()
  }
}

// Export singleton instance
export const authService = new AuthService()
