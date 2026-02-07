/**
 * Clinic Admin API
 *
 * Add employees (users with roles NURSE, HR_OPERATIONS, RECEPTIONIST) to a clinic.
 */

import { apiService } from './api.service'

export type ClinicEmployeeRole = 'NURSE' | 'HR_OPERATIONS' | 'RECEPTIONIST' | 'DOCTOR'

export type AddAsType = 'user' | 'employee'

export interface AddClinicEmployeeRequest {
  email: string
  username: string
  password: string
  first_name: string
  last_name: string
  phone?: string | null
  role: ClinicEmployeeRole
  /** user = only users + linked_clinics; employee = users + linked_clinics + employees */
  add_as?: AddAsType
}

export interface ClinicEmployeeResponse {
  user: {
    id: string
    email: string
    username: string
    first_name: string | null
    last_name: string | null
    clinic_role: string
  }
  employee: {
    id: string
    employee_number: string
    first_name: string
    last_name: string
    email: string
    employee_role: string
    clinic_id: string
  } | null
}

export type RecordType = 'user' | 'employee'

export interface ClinicEmployeeListItem {
  id: string
  email: string
  username: string
  first_name: string | null
  last_name: string | null
  is_active: boolean
  clinic_role: string
  /** 'employee' if has employees row, else 'user' */
  record_type?: RecordType
  employee_id?: string | null
  employee_number?: string | null
  is_active_empl?: boolean
}

/** Per-user feature access: FINANCE, PATIENTS, WORK_QUEUE, PAYROLL -> boolean */
export type UserFeatures = Record<string, boolean>

export interface ClinicSettingsUserItem {
  id: string
  email: string
  username: string
  first_name: string | null
  last_name: string | null
  clinic_role: string
  features: UserFeatures
}

/** GET /clinic-admin/settings returns { users: ClinicSettingsUserItem[] } */
export interface ClinicSettingsResponse {
  users: ClinicSettingsUserItem[]
}

/** PUT body: list of user id + features, or map user_id -> features */
export type ClinicSettingsPutBody =
  | { users: Array<{ user_id?: string; id?: string; features: UserFeatures }> }
  | Record<string, UserFeatures>

class ClinicAdminService {
  /**
   * Add an employee to the current user's clinic. Uses JWT; clinic is taken from the logged-in CLINIC_ADMIN.
   * Prefer this over addClinicEmployee when the caller is the clinic admin (no need to pass clinic ID).
   */
  async addClinicEmployeeCurrentUser(body: AddClinicEmployeeRequest): Promise<ClinicEmployeeResponse> {
    return apiService.post<ClinicEmployeeResponse>('/clinic-admin/employees', body)
  }

  async addClinicEmployee(
    clinicId: string,
    body: AddClinicEmployeeRequest
  ): Promise<ClinicEmployeeResponse> {
    return apiService.post<ClinicEmployeeResponse>(
      `/clinic-admin/clinics/${clinicId}/employees`,
      body
    )
  }

  /**
   * List employees for the current user's clinic. Uses JWT; no clinic ID needed.
   */
  async listClinicEmployeesCurrentUser(params?: {
    skip?: number
    limit?: number
  }): Promise<{ items: ClinicEmployeeListItem[]; total: number; skip: number; limit: number }> {
    const q = new URLSearchParams()
    if (params?.skip != null) q.set('skip', String(params.skip))
    if (params?.limit != null) q.set('limit', String(params.limit))
    const query = q.toString()
    return apiService.get<{ items: ClinicEmployeeListItem[]; total: number; skip: number; limit: number }>(
      `/clinic-admin/employees${query ? `?${query}` : ''}`
    )
  }

  async listClinicEmployees(
    clinicId: string,
    params?: { skip?: number; limit?: number }
  ): Promise<{ items: ClinicEmployeeListItem[]; total: number; skip: number; limit: number }> {
    const q = new URLSearchParams()
    if (params?.skip != null) q.set('skip', String(params.skip))
    if (params?.limit != null) q.set('limit', String(params.limit))
    const query = q.toString()
    return apiService.get<{ items: ClinicEmployeeListItem[]; total: number; skip: number; limit: number }>(
      `/clinic-admin/clinics/${clinicId}/employees${query ? `?${query}` : ''}`
    )
  }

  /**
   * Users and their feature access for the current clinic. Returns { users: [ { id, email, username, first_name, last_name, clinic_role, features }, ... ] }.
   */
  async getClinicSettings(): Promise<ClinicSettingsResponse> {
    return apiService.get<ClinicSettingsResponse>('/clinic-admin/settings')
  }

  /**
   * Update per-user feature access. Body: { users: [ { user_id, features: { FINANCE, PATIENTS, WORK_QUEUE, PAYROLL } }, ... ] } or { "user_id": { FINANCE: true, ... }, ... }.
   */
  async putClinicSettings(body: ClinicSettingsPutBody): Promise<ClinicSettingsResponse> {
    return apiService.put<ClinicSettingsResponse>('/clinic-admin/settings', body)
  }
}

export const clinicAdminService = new ClinicAdminService()
