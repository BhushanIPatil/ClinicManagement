/**
 * Tests for useAppointments hook
 */

import { describe, it, expect, vi, beforeEach } from 'vitest'
import { renderHook, waitFor } from '@testing-library/react'
import { useAppointments } from '../useAppointments'
import { appointmentService } from '@/services/appointment.service'

// Mock the service
vi.mock('@/services/appointment.service', () => ({
  appointmentService: {
    listAppointments: vi.fn(),
    bookAppointment: vi.fn(),
  },
}))

describe('useAppointments', () => {
  beforeEach(() => {
    vi.clearAllMocks()
  })

  it('fetches appointments on mount', async () => {
    const mockAppointments = [
      { id: '1', appointment_number: 'APT001', status: 'SCHEDULED' },
    ]
    vi.mocked(appointmentService.listAppointments).mockResolvedValue(mockAppointments)

    const { result } = renderHook(() => useAppointments({ autoFetch: true }))

    await waitFor(() => {
      expect(result.current.loading).toBe(false)
    })

    expect(result.current.appointments).toEqual(mockAppointments)
    expect(appointmentService.listAppointments).toHaveBeenCalled()
  })

  it('handles errors correctly', async () => {
    const error = new Error('Failed to fetch')
    vi.mocked(appointmentService.listAppointments).mockRejectedValue(error)

    const { result } = renderHook(() => useAppointments({ autoFetch: true }))

    await waitFor(() => {
      expect(result.current.loading).toBe(false)
    })

    expect(result.current.error).toBeTruthy()
  })

  it('books appointment successfully', async () => {
    const newAppointment = { id: '2', appointment_number: 'APT002' }
    vi.mocked(appointmentService.bookAppointment).mockResolvedValue(newAppointment as any)

    const { result } = renderHook(() => useAppointments({ autoFetch: false }))

    await result.current.bookAppointment({
      patient_id: '1',
      doctor_id: '1',
      appointment_date: '2025-01-25T10:00:00Z',
    })

    expect(appointmentService.bookAppointment).toHaveBeenCalled()
  })
})
