/**
 * Appointment Service
 * 
 * Handles all appointment-related API calls.
 */

import { apiService } from './api.service'
import type {
  Appointment,
  BookAppointmentRequest,
  UpdateAppointmentRequest,
  RescheduleAppointmentRequest,
  CancelAppointmentRequest,
  UpdateStatusRequest,
  AvailabilitySlot,
  AvailabilityQuery,
  DoctorOption,
  PatientOption,
} from '@/types/appointment.types'

class AppointmentService {
  /**
   * Book a new appointment
   */
  async bookAppointment(data: BookAppointmentRequest): Promise<Appointment> {
    return apiService.post<Appointment>('/appointments', data)
  }

  /**
   * Get appointment by ID
   */
  async getAppointment(id: string): Promise<Appointment> {
    return apiService.get<Appointment>(`/appointments/${id}`)
  }

  /**
   * List appointments. API returns { items, total, skip, limit }; this returns items, or [] when missing.
   */
  async listAppointments(params?: {
    patient_id?: string
    doctor_id?: string
    skip?: number
    limit?: number
    status?: string
    date_from?: string
    date_to?: string
  }): Promise<Appointment[]> {
    const queryParams = new URLSearchParams()
    if (params?.patient_id) queryParams.append('patient_id', params.patient_id)
    if (params?.doctor_id) queryParams.append('doctor_id', params.doctor_id)
    if (params?.skip != null) queryParams.append('skip', String(params.skip))
    if (params?.limit != null) queryParams.append('limit', String(params.limit))
    if (params?.status) queryParams.append('status', params.status)
    if (params?.date_from) queryParams.append('date_from', params.date_from)
    if (params?.date_to) queryParams.append('date_to', params.date_to)

    const query = queryParams.toString()
    const res = await apiService.get<{ items?: Appointment[]; total?: number }>(
      `/appointments${query ? `?${query}` : ''}`
    )
    return Array.isArray(res?.items) ? res.items : []
  }

  /**
   * Update appointment (backend PUT /appointments/:id). Use for reschedule, status, or field edits.
   */
  async updateAppointment(
    id: string,
    data: UpdateAppointmentRequest
  ): Promise<Appointment> {
    return apiService.put<Appointment>(`/appointments/${id}`, data)
  }

  /**
   * Reschedule appointment (convenience: calls updateAppointment with date/duration)
   */
  async rescheduleAppointment(
    id: string,
    data: RescheduleAppointmentRequest
  ): Promise<Appointment> {
    return this.updateAppointment(id, {
      appointment_date: data.appointment_date,
      duration_minutes: data.duration_minutes,
      notes: data.notes,
    })
  }

  /**
   * Cancel appointment (backend DELETE /appointments/:id with optional body)
   */
  async cancelAppointment(
    id: string,
    data?: CancelAppointmentRequest
  ): Promise<Appointment> {
    return apiService.delete<Appointment>(`/appointments/${id}`, data ?? undefined)
  }

  /**
   * Add a patient payment for an appointment (Patient Payments). Creates invoice if needed.
   */
  async addPatientPayment(
    appointmentId: string,
    data: { amount: number; payment_method: string; payment_date: string }
  ): Promise<{ id: string; payment_number: string; amount: number; payment_method: string; payment_date: string | null }> {
    return apiService.post(`/appointments/${appointmentId}/payments`, data)
  }

  /**
   * Update appointment status (convenience: calls updateAppointment)
   */
  async updateStatus(
    id: string,
    data: UpdateStatusRequest
  ): Promise<Appointment> {
    return this.updateAppointment(id, { status: data.status })
  }

  /**
   * List doctors for the given clinic (add-appointment form). Uses primary_clinic_id from user login/cookies.
   * Calls GET /doctors?clinic_id=... which returns only doctors for that clinic.
   */
  async getDoctorsByClinic(clinicId: string, limit = 200): Promise<DoctorOption[]> {
    const params = new URLSearchParams({ clinic_id: clinicId, limit: String(limit) })
    const res = await apiService.get<{ items?: DoctorOption[] }>(
      `/doctors?${params}`
    )
    return Array.isArray(res?.items) ? res.items : []
  }

  /**
   * List doctors for dropdowns. When clinicId (primary_clinic_id) is present, uses GET /doctors?clinic_id=...
   */
  async getDoctorsOptions(limit = 200, clinicId?: string | null): Promise<DoctorOption[]> {
    if (clinicId) {
      return this.getDoctorsByClinic(clinicId, limit)
    }
    const res = await apiService.get<{ items?: DoctorOption[] }>(
      `/appointments/options/doctors?limit=${limit}`
    )
    return Array.isArray(res?.items) ? res.items : []
  }

  /**
   * List patients for dropdowns (add-appointment form)
   */
  async getPatientsOptions(limit = 200, search?: string): Promise<PatientOption[]> {
    const params = new URLSearchParams({ limit: String(limit) })
    if (search) params.set('search', search)
    const res = await apiService.get<{ items?: PatientOption[] }>(
      `/appointments/options/patients?${params}`
    )
    return Array.isArray(res?.items) ? res.items : []
  }

  /**
   * Get current user's schedule (doctor only). Requires auth. Returns today and future appointments with fees_paid.
   */
  async getMySchedule(limit = 50): Promise<Appointment[]> {
    const res = await apiService.get<{ items?: Appointment[] }>(
      `/appointments/my-schedule?limit=${limit}`
    )
    return Array.isArray(res?.items) ? res.items : []
  }

  /**
   * Get doctor availability
   */
  async getAvailability(
    query: AvailabilityQuery
  ): Promise<AvailabilitySlot[]> {
    return apiService.post<AvailabilitySlot[]>(
      '/appointments/availability',
      query
    )
  }
}

export const appointmentService = new AppointmentService()
