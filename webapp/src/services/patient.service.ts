/**
 * Patient Service
 * 
 * Handles all patient-related API calls.
 */

import { apiService } from './api.service'
import type {
  Patient,
  PatientCreateRequest,
  PatientUpdateRequest,
  PatientListResponse,
} from '@/types/patient.types'

class PatientService {
  /**
   * Create a new patient
   */
  async createPatient(data: PatientCreateRequest): Promise<Patient> {
    return apiService.post<Patient>('/patients', data)
  }

  /**
   * Get patient by ID
   */
  async getPatient(id: string): Promise<Patient> {
    return apiService.get<Patient>(`/patients/${id}`)
  }

  /**
   * Update patient
   */
  async updatePatient(
    id: string,
    data: PatientUpdateRequest
  ): Promise<Patient> {
    return apiService.put<Patient>(`/patients/${id}`, data)
  }

  /**
   * List patients. Normalizes API response so patients is always an array and total a number.
   */
  async listPatients(params?: {
    page?: number
    page_size?: number
    search?: string
  }): Promise<PatientListResponse> {
    const queryParams = new URLSearchParams()
    if (params?.page) queryParams.append('page', params.page.toString())
    if (params?.page_size)
      queryParams.append('page_size', params.page_size.toString())
    if (params?.search) queryParams.append('search', params.search)

    const query = queryParams.toString()
    const res = await apiService.get<PatientListResponse & { items?: Patient[] }>(
      `/patients${query ? `?${query}` : ''}`
    )
    const patients = Array.isArray(res?.patients) ? res.patients : (Array.isArray((res as any)?.items) ? (res as any).items : [])
    return {
      patients,
      total: typeof (res?.total) === 'number' ? res.total : 0,
      page: typeof (res?.page) === 'number' ? res.page : 1,
      page_size: typeof (res?.page_size) === 'number' ? res.page_size : 20,
    }
  }

  /**
   * Search patients
   */
  async searchPatients(query: string): Promise<Patient[]> {
    return apiService.get<Patient[]>(`/patients/search?q=${encodeURIComponent(query)}`)
  }
}

export const patientService = new PatientService()
