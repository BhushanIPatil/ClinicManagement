/**
 * Super Admin API: clinics count, list, clinic users, onboard clinic with user.
 */

import { apiService } from './api.service'

export interface ClinicDto {
  id: string
  name: string
  code: string
  address?: string | null
  phone?: string | null
  is_active: boolean
  created_at: string | null
}

export interface ClinicUserDto {
  id: string
  email: string
  username: string
  first_name: string
  last_name: string
  is_active: boolean
  clinic_role: string
}

export interface OnboardClinicRequest {
  clinic: { name: string; code: string; address?: string; phone?: string }
  user: {
    email: string
    username: string
    password: string
    first_name: string
    last_name: string
    phone?: string
  }
}

export const superAdminService = {
  async getClinicsCount(): Promise<{ count: number }> {
    return apiService.get<{ count: number }>('/super-admin/clinics/count')
  },
  async listClinics(skip = 0, limit = 50): Promise<{
    items: ClinicDto[]
    total: number
    skip: number
    limit: number
  }> {
    return apiService.get<{ items: ClinicDto[]; total: number; skip: number; limit: number }>(
      `/super-admin/clinics?skip=${skip}&limit=${limit}`
    )
  },
  async listClinicUsers(clinicId: string): Promise<{ users: ClinicUserDto[] }> {
    return apiService.get<{ users: ClinicUserDto[] }>(`/super-admin/clinics/${clinicId}/users`)
  },
  async onboardClinic(data: OnboardClinicRequest): Promise<{
    clinic: { id: string; name: string; code: string }
    user: { id: string; email: string; username: string; first_name: string; last_name: string; clinic_role: string }
  }> {
    return apiService.post('/super-admin/clinics/onboard', data)
  },
}
