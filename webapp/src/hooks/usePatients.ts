/**
 * usePatients Hook
 * 
 * Hook for managing patients with loading and error states.
 */

import { useState, useEffect, useCallback } from 'react'
import { patientService } from '@/services/patient.service'
import type {
  Patient,
  PatientCreateRequest,
  PatientUpdateRequest,
} from '@/types/patient.types'

interface UsePatientsOptions {
  autoFetch?: boolean
  page?: number
  pageSize?: number
}

export function usePatients(options: UsePatientsOptions = {}) {
  const { autoFetch = true, page = 1, pageSize = 20 } = options

  const [patients, setPatients] = useState<Patient[]>([])
  const [total, setTotal] = useState(0)
  const [loading, setLoading] = useState(false)
  const [error, setError] = useState<string | null>(null)

  const fetchPatients = useCallback(async () => {
    setLoading(true)
    setError(null)
    try {
      const response = await patientService.listPatients({
        page,
        page_size: pageSize,
      })
      setPatients(Array.isArray(response.patients) ? response.patients : [])
      setTotal(Number(response.total) || 0)
    } catch (err: any) {
      setError(err?.detail || 'Failed to fetch patients')
    } finally {
      setLoading(false)
    }
  }, [page, pageSize])

  const createPatient = useCallback(async (data: PatientCreateRequest) => {
    setLoading(true)
    setError(null)
    try {
      const patient = await patientService.createPatient(data)
      setPatients((prev) => [patient, ...prev])
      setTotal((prev) => prev + 1)
      return patient
    } catch (err: any) {
      setError(err?.detail || 'Failed to create patient')
      throw err
    } finally {
      setLoading(false)
    }
  }, [])

  const updatePatient = useCallback(
    async (id: string, data: PatientUpdateRequest) => {
      setLoading(true)
      setError(null)
      try {
        const patient = await patientService.updatePatient(id, data)
        setPatients((prev) =>
          prev.map((p) => (p.id === id ? patient : p))
        )
        return patient
      } catch (err: any) {
        setError(err?.detail || 'Failed to update patient')
        throw err
      } finally {
        setLoading(false)
      }
    },
    []
  )

  useEffect(() => {
    if (autoFetch) {
      fetchPatients()
    }
  }, [fetchPatients, autoFetch])

  return {
    patients,
    total,
    loading,
    error,
    fetchPatients,
    createPatient,
    updatePatient,
  }
}
