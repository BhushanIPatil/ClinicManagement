/**
 * Appointment Service
 * 
 * Handles all appointment-related API calls.
 */

import { apiService } from './api.service'
import type {
  Appointment,
  BookAppointmentRequest,
  RescheduleAppointmentRequest,
  CancelAppointmentRequest,
  UpdateStatusRequest,
  AvailabilitySlot,
  AvailabilityQuery,
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
   * Reschedule appointment
   */
  async rescheduleAppointment(
    id: string,
    data: RescheduleAppointmentRequest
  ): Promise<Appointment> {
    return apiService.put<Appointment>(`/appointments/${id}/reschedule`, data)
  }

  /**
   * Cancel appointment
   */
  async cancelAppointment(
    id: string,
    data: CancelAppointmentRequest
  ): Promise<Appointment> {
    return apiService.put<Appointment>(`/appointments/${id}/cancel`, data)
  }

  /**
   * Update appointment status
   */
  async updateStatus(
    id: string,
    data: UpdateStatusRequest
  ): Promise<Appointment> {
    return apiService.patch<Appointment>(`/appointments/${id}/status`, data)
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
