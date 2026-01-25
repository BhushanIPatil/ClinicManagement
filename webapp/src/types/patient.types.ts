/**
 * Patient Types
 */

export interface Patient {
  id: string
  patient_number: string
  first_name: string
  last_name: string
  date_of_birth: string
  gender: Gender
  email?: string | null
  phone?: string | null
  address?: string | null
  emergency_contact_name?: string | null
  emergency_contact_phone?: string | null
  blood_type?: string | null
  allergies?: string | null
  created_at?: string
  updated_at?: string
}

export type Gender = 'MALE' | 'FEMALE' | 'OTHER'

export interface PatientCreateRequest {
  patient_number?: string
  first_name: string
  last_name: string
  date_of_birth?: string
  gender: Gender
  email?: string
  phone?: string
  address?: string
  emergency_contact_name?: string
  emergency_contact_phone?: string
  blood_type?: string
  allergies?: string
}

export interface PatientUpdateRequest {
  first_name?: string
  last_name?: string
  date_of_birth?: string
  gender?: Gender
  email?: string
  phone?: string
  address?: string
  emergency_contact_name?: string
  emergency_contact_phone?: string
  blood_type?: string
  allergies?: string
}

export interface PatientListResponse {
  patients: Patient[]
  total: number
  page: number
  page_size: number
}
