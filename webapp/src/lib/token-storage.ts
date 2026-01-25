/**
 * Token Storage Utilities
 *
 * Handles secure storage and retrieval of authentication tokens and user.
 * Uses localStorage and cookies (login details as JSON in a cookie).
 */

const ACCESS_TOKEN_KEY = 'clinic_access_token'
const REFRESH_TOKEN_KEY = 'clinic_refresh_token'
const USER_KEY = 'clinic_user'
const LOGIN_COOKIE_NAME = 'clinic_login'
const LOGIN_COOKIE_MAX_AGE_DAYS = 7

export interface LoginDetails {
  user: Record<string, unknown>
  access_token: string
  refresh_token?: string
}

function getCookie(name: string): string | null {
  if (typeof document === 'undefined') return null
  const matcher = new RegExp(`(?:^|;\\s*)${encodeURIComponent(name)}=([^;]*)`)
  const m = document.cookie.match(matcher)
  if (!m) return null
  try {
    return decodeURIComponent(m[1])
  } catch {
    return null
  }
}

function setCookie(name: string, value: string, maxAgeDays: number): void {
  if (typeof document === 'undefined') return
  const maxAge = maxAgeDays * 24 * 60 * 60
  document.cookie = `${encodeURIComponent(name)}=${encodeURIComponent(value)}; path=/; sameSite=Lax; max-age=${maxAge}`
}

function clearCookie(name: string): void {
  if (typeof document === 'undefined') return
  document.cookie = `${encodeURIComponent(name)}=; path=/; max-age=0`
}

export const tokenStorage = {
  /**
   * Store access token (localStorage; use setLoginDetails to also persist in cookie).
   */
  setAccessToken(token: string): void {
    try {
      localStorage.setItem(ACCESS_TOKEN_KEY, token)
    } catch (error) {
      console.error('Failed to store access token:', error)
    }
  },

  /**
   * Get access token (prefer cookie, then localStorage).
   */
  getAccessToken(): string | null {
    const fromCookie = this.getLoginDetailsFromCookie()
    if (fromCookie?.access_token) return fromCookie.access_token
    try {
      return localStorage.getItem(ACCESS_TOKEN_KEY)
    } catch (error) {
      console.error('Failed to retrieve access token:', error)
      return null
    }
  },

  /**
   * Store refresh token
   */
  setRefreshToken(token: string): void {
    try {
      localStorage.setItem(REFRESH_TOKEN_KEY, token)
    } catch (error) {
      console.error('Failed to store refresh token:', error)
    }
  },

  /**
   * Get refresh token (prefer cookie, then localStorage).
   */
  getRefreshToken(): string | null {
    const fromCookie = this.getLoginDetailsFromCookie()
    if (fromCookie?.refresh_token) return fromCookie.refresh_token
    try {
      return localStorage.getItem(REFRESH_TOKEN_KEY)
    } catch (error) {
      console.error('Failed to retrieve refresh token:', error)
      return null
    }
  },

  /**
   * Store user data (localStorage; use setLoginDetails to also persist in cookie).
   */
  setUser(user: any): void {
    try {
      localStorage.setItem(USER_KEY, JSON.stringify(user))
    } catch (error) {
      console.error('Failed to store user:', error)
    }
  },

  /**
   * Get user data (prefer cookie, then localStorage).
   */
  getUser(): any | null {
    const fromCookie = this.getLoginDetailsFromCookie()
    if (fromCookie?.user && typeof fromCookie.user === 'object') return fromCookie.user as any
    try {
      const userStr = localStorage.getItem(USER_KEY)
      return userStr ? JSON.parse(userStr) : null
    } catch (error) {
      console.error('Failed to retrieve user:', error)
      return null
    }
  },

  /**
   * Store full login details in localStorage and in a cookie as JSON.
   */
  setLoginDetailsCookie(details: LoginDetails): void {
    try {
      const { user, access_token, refresh_token } = details
      localStorage.setItem(USER_KEY, JSON.stringify(user))
      localStorage.setItem(ACCESS_TOKEN_KEY, access_token)
      localStorage.setItem(REFRESH_TOKEN_KEY, refresh_token ?? '')
      const payload = JSON.stringify({
        user,
        access_token,
        refresh_token: refresh_token ?? '',
      })
      setCookie(LOGIN_COOKIE_NAME, payload, LOGIN_COOKIE_MAX_AGE_DAYS)
    } catch (error) {
      console.error('Failed to store login details:', error)
    }
  },

  /**
   * Read login details from cookie (JSON). Returns null if missing or invalid.
   */
  getLoginDetailsFromCookie(): LoginDetails | null {
    try {
      const raw = getCookie(LOGIN_COOKIE_NAME)
      if (!raw) return null
      const parsed = JSON.parse(raw) as unknown
      if (!parsed || typeof parsed !== 'object') return null
      const o = parsed as Record<string, unknown>
      if (typeof o.access_token !== 'string') return null
      return {
        user: (o.user && typeof o.user === 'object' ? o.user : {}) as Record<string, unknown>,
        access_token: o.access_token,
        refresh_token: typeof o.refresh_token === 'string' ? o.refresh_token : undefined,
      }
    } catch {
      return null
    }
  },

  /**
   * Store tokens
   */
  setTokens(tokens: { access_token: string; refresh_token: string }): void {
    this.setAccessToken(tokens.access_token)
    this.setRefreshToken(tokens.refresh_token)
  },

  /**
   * Clear all auth data (localStorage and cookie).
   */
  clear(): void {
    try {
      localStorage.removeItem(ACCESS_TOKEN_KEY)
      localStorage.removeItem(REFRESH_TOKEN_KEY)
      localStorage.removeItem(USER_KEY)
      clearCookie(LOGIN_COOKIE_NAME)
    } catch (error) {
      console.error('Failed to clear tokens:', error)
    }
  },

  /**
   * Check if user is authenticated
   */
  isAuthenticated(): boolean {
    return !!this.getAccessToken()
  },
}
