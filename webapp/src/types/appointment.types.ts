/**
 * Appointment Types
 */

export interface Appointment {
  id: string
  appointment_number: string
  patient_id: string
  doctor_id: string
  department_id: string
  appointment_date: string
  duration_minutes: number
  status: AppointmentStatus
  appointment_type: AppointmentType
  reason?: string | null
  notes?: string | null
  patient_name?: string
  doctor_name?: string
  department_name?: string
  created_at?: string
  updated_at?: string
  /** Present when fetched from GET /appointments/my-schedule */
  fees_paid?: boolean
  /** Present in list: whether this appointment has been paid (patient payment recorded). */
  paid?: boolean
}

export type AppointmentStatus =
  | 'SCHEDULED'
  | 'CONFIRMED'
  | 'IN_PROGRESS'
  | 'COMPLETED'
  | 'CANCELLED'
  | 'NO_SHOW'

export type AppointmentType =
  | 'CONSULTATION'
  | 'FOLLOW_UP'
  | 'CHECKUP'
  | 'EMERGENCY'
  | 'SURGERY'
  | 'OTHER'

export interface BookAppointmentRequest {
  patient_id: string
  doctor_id: string
  department_id?: string
  appointment_date: string
  duration_minutes?: number
  appointment_type?: AppointmentType
  reason?: string
  notes?: string
}

export interface UpdateAppointmentRequest {
  appointment_date?: string
  duration_minutes?: number
  status?: AppointmentStatus
  appointment_type?: AppointmentType
  reason?: string
  notes?: string
  doctor_id?: string
  department_id?: string
}

export interface DoctorOption {
  id: string
  first_name: string
  last_name: string
  label: string
}

export interface PatientOption {
  id: string
  first_name: string
  last_name: string
  patient_number?: string
  label: string
}

export interface RescheduleAppointmentRequest {
  appointment_date: string
  duration_minutes?: number
  notes?: string
}

export interface CancelAppointmentRequest {
  reason?: string
}

export interface UpdateStatusRequest {
  status: AppointmentStatus
}

export interface AvailabilitySlot {
  start_time: string
  end_time: string
  is_available: boolean
}

export interface AvailabilityQuery {
  doctor_id: string
  date: string
  duration_minutes?: number
}
