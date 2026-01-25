/**
 * useAppointments Hook
 * 
 * Hook for managing appointments with loading and error states.
 */

import { useState, useEffect, useCallback } from 'react'
import { appointmentService } from '@/services/appointment.service'
import type {
  Appointment,
  BookAppointmentRequest,
  UpdateAppointmentRequest,
  CancelAppointmentRequest,
} from '@/types/appointment.types'

interface UseAppointmentsOptions {
  patientId?: string
  doctorId?: string
  autoFetch?: boolean
}

export function useAppointments(options: UseAppointmentsOptions = {}) {
  const { patientId, doctorId, autoFetch = true } = options

  const [appointments, setAppointments] = useState<Appointment[]>([])
  const [loading, setLoading] = useState(false)
  const [error, setError] = useState<string | null>(null)

  const fetchAppointments = useCallback(async () => {
    setLoading(true)
    setError(null)
    try {
      const data = await appointmentService.listAppointments({
        patient_id: patientId,
        doctor_id: doctorId,
      })
      setAppointments(data)
    } catch (err: any) {
      setError(err?.detail || 'Failed to fetch appointments')
    } finally {
      setLoading(false)
    }
  }, [patientId, doctorId])

  const bookAppointment = useCallback(
    async (data: BookAppointmentRequest) => {
      setLoading(true)
      setError(null)
      try {
        const appointment = await appointmentService.bookAppointment(data)
        setAppointments((prev) => [appointment, ...prev])
        return appointment
      } catch (err: any) {
        setError(err?.detail || 'Failed to book appointment')
        throw err
      } finally {
        setLoading(false)
      }
    },
    []
  )

  const updateAppointment = useCallback(
    async (id: string, data: UpdateAppointmentRequest) => {
      setLoading(true)
      setError(null)
      try {
        const updated = await appointmentService.updateAppointment(id, data)
        setAppointments((prev) =>
          prev.map((a) => (a.id === id ? updated : a))
        )
        return updated
      } catch (err: any) {
        setError(err?.detail || 'Failed to update appointment')
        throw err
      } finally {
        setLoading(false)
      }
    },
    []
  )

  const cancelAppointment = useCallback(
    async (id: string, data?: CancelAppointmentRequest) => {
      setLoading(true)
      setError(null)
      try {
        const updated = await appointmentService.cancelAppointment(id, data)
        setAppointments((prev) =>
          prev.map((a) => (a.id === id ? updated : a))
        )
        return updated
      } catch (err: any) {
        setError(err?.detail || 'Failed to cancel appointment')
        throw err
      } finally {
        setLoading(false)
      }
    },
    []
  )

  useEffect(() => {
    if (autoFetch) {
      fetchAppointments()
    }
  }, [fetchAppointments, autoFetch])

  return {
    appointments,
    loading,
    error,
    fetchAppointments,
    bookAppointment,
    updateAppointment,
    cancelAppointment,
  }
}
