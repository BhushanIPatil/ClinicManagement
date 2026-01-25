/**
 * API Service
 * 
 * Base API client with token handling, interceptors, and error management.
 * All API calls go through this service.
 */

import { tokenStorage } from '@/lib/token-storage'
import { env } from '@/lib/env'

export interface ApiError {
  detail: string
  message?: string
  statusCode?: number
}

export class ApiService {
  private baseURL: string

  constructor(baseURL: string = env.API_BASE_URL) {
    this.baseURL = baseURL
  }

  /**
   * Get default headers with authentication
   */
  private getHeaders(includeAuth = true): HeadersInit {
    const headers: HeadersInit = {
      'Content-Type': 'application/json',
    }

    if (includeAuth) {
      const token = tokenStorage.getAccessToken()
      if (token) {
        headers['Authorization'] = `Bearer ${token}`
      }
    }

    return headers
  }

  /**
   * Handle API response
   */
  private async handleResponse<T>(response: Response, retryRequest?: () => Promise<Response>): Promise<T> {
    if (!response.ok) {
      let error: ApiError
      try {
        const errorData = await response.json()
        error = {
          detail: errorData.detail || errorData.message || 'An error occurred',
          message: errorData.message,
          statusCode: response.status,
        }
      } catch {
        error = {
          detail: `HTTP ${response.status}: ${response.statusText}`,
          statusCode: response.status,
        }
      }

      // Handle 401 Unauthorized - token expired
      if (response.status === 401 && retryRequest) {
        // Try to refresh token
        const refreshed = await this.refreshTokenIfNeeded()
        if (refreshed) {
          // Retry original request with new token
          const retryResponse = await retryRequest()
          return this.handleResponse<T>(retryResponse)
        }
        // Refresh failed, clear auth and throw error
        tokenStorage.clear()
      }

      throw error
    }

    // Handle empty responses
    const contentType = response.headers.get('content-type')
    if (!contentType || !contentType.includes('application/json')) {
      return {} as T
    }

    return response.json()
  }

  /**
   * Refresh token if needed
   */
  private async refreshTokenIfNeeded(): Promise<boolean> {
    const refreshToken = tokenStorage.getRefreshToken()
    if (!refreshToken) {
      return false
    }

    try {
      const response = await fetch(`${this.baseURL}/auth/refresh`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({ refresh_token: refreshToken }),
      })

      if (!response.ok) {
        return false
      }

      const tokens = await response.json()
      tokenStorage.setTokens(tokens)
      return true
    } catch {
      return false
    }
  }

  /**
   * GET request
   */
  async get<T>(endpoint: string, includeAuth = true): Promise<T> {
    const response = await fetch(`${this.baseURL}${endpoint}`, {
      method: 'GET',
      headers: this.getHeaders(includeAuth),
    })

    return this.handleResponse<T>(response)
  }

  /**
   * POST request
   */
  async post<T>(endpoint: string, data?: any, includeAuth = true): Promise<T> {
    const makeRequest = () =>
      fetch(`${this.baseURL}${endpoint}`, {
        method: 'POST',
        headers: this.getHeaders(includeAuth),
        body: data ? JSON.stringify(data) : undefined,
      })

    const response = await makeRequest()
    return this.handleResponse<T>(response, includeAuth ? makeRequest : undefined)
  }

  /**
   * PUT request
   */
  async put<T>(endpoint: string, data?: any, includeAuth = true): Promise<T> {
    const response = await fetch(`${this.baseURL}${endpoint}`, {
      method: 'PUT',
      headers: this.getHeaders(includeAuth),
      body: data ? JSON.stringify(data) : undefined,
    })

    return this.handleResponse<T>(response)
  }

  /**
   * PATCH request
   */
  async patch<T>(endpoint: string, data?: any, includeAuth = true): Promise<T> {
    const response = await fetch(`${this.baseURL}${endpoint}`, {
      method: 'PATCH',
      headers: this.getHeaders(includeAuth),
      body: data ? JSON.stringify(data) : undefined,
    })

    return this.handleResponse<T>(response)
  }

  /**
   * DELETE request
   */
  async delete<T>(endpoint: string, includeAuth = true): Promise<T> {
    const response = await fetch(`${this.baseURL}${endpoint}`, {
      method: 'DELETE',
      headers: this.getHeaders(includeAuth),
    })

    return this.handleResponse<T>(response)
  }
}

// Export singleton instance
export const apiService = new ApiService()
