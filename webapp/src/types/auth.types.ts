/**
 * Authentication Types
 */

export interface User {
  id: string
  email: string
  username: string
  first_name: string
  last_name: string
  phone?: string | null
  is_active: boolean
  is_verified: boolean
  last_login?: string | null
  role_names: string[]
  created_at: string
  updated_at: string
  /** Set by backend on login for users with a clinic (e.g. CLINIC_ADMIN). Used when adding employees. */
  primary_clinic_id?: string | null
  primary_clinic_name?: string | null
  /** Set when user has a linked Doctor record (e.g. DOCTOR role). Used for "my schedule" in work queue. */
  doctor_id?: string | null
}

export interface Tokens {
  access_token: string
  refresh_token: string
  token_type: string
}

export interface LoginRequest {
  username: string
  password: string
}

export interface RegisterRequest {
  email: string
  username: string
  password: string
  first_name: string
  last_name: string
  phone?: string
}

export interface AuthResponse {
  user: User
  tokens: Tokens
}

export interface RefreshTokenRequest {
  refresh_token: string
}

export type UserRole =
  | 'SUPER_ADMIN'
  | 'CLINIC_ADMIN'
  | 'NURSE'
  | 'HR_OPERATIONS'
  | 'RECEPTIONIST'
  | 'ADMIN'
  | 'DOCTOR'
  | 'ACCOUNTANT'
  | 'HR'
