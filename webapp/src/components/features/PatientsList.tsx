/**
 * Patients List Component
 *
 * Displays a list of patients. When patients/loading/error are passed, uses those; otherwise fetches via usePatients.
 */

import { User, Phone, Mail, Calendar } from 'lucide-react'
import { usePatients } from '@/hooks/usePatients'
import { DataTable, Column, LoadingSpinner, ErrorMessage } from '@/components/common'
import { cn } from '@/lib/utils'
import type { Patient } from '@/types/patient.types'

interface PatientsListProps {
  className?: string
  /** When provided, use these instead of fetching (e.g. from parent page that also has Add Patient). */
  patients?: Patient[]
  loading?: boolean
  error?: string | null
}

export function PatientsList({ className, patients: propsPatients, loading: propsLoading, error: propsError }: PatientsListProps) {
  const fromHook = usePatients({
    autoFetch: propsPatients === undefined && propsLoading === undefined && propsError === undefined,
  })
  const patients = propsPatients ?? fromHook.patients
  const loading = propsLoading ?? fromHook.loading
  const error = propsError ?? fromHook.error

  const formatDate = (dateString?: string | null) => {
    if (dateString == null || dateString === '') return '–'
    const d = new Date(dateString)
    if (Number.isNaN(d.getTime())) return '–'
    return d.toLocaleDateString('en-US', {
      year: 'numeric',
      month: 'short',
      day: 'numeric',
    })
  }

  const getAge = (dateOfBirth?: string | null) => {
    if (dateOfBirth == null || dateOfBirth === '') return '–'
    const today = new Date()
    const birth = new Date(dateOfBirth)
    if (Number.isNaN(birth.getTime())) return '–'
    let age = today.getFullYear() - birth.getFullYear()
    const monthDiff = today.getMonth() - birth.getMonth()
    if (monthDiff < 0 || (monthDiff === 0 && today.getDate() < birth.getDate())) {
      age--
    }
    return age < 0 ? '–' : `${age} years`
  }

  const columns: Column<Patient>[] = [
    {
      key: 'patient_number',
      header: 'Patient #',
      render: (item) => (
        <span className="font-mono text-sm font-medium">{item.patient_number ?? '–'}</span>
      ),
    },
    {
      key: 'name',
      header: 'Name',
      render: (item) => (
        <div className="flex items-center gap-2">
          <User className="w-4 h-4 text-muted-foreground" />
          <span>{[item.first_name, item.last_name].filter(Boolean).join(' ').trim() || '–'}</span>
        </div>
      ),
    },
    {
      key: 'date_of_birth',
      header: 'Age',
      render: (item) => (
        <div className="flex items-center gap-2">
          <Calendar className="w-4 h-4 text-muted-foreground" />
          <span>{getAge(item.date_of_birth)}</span>
        </div>
      ),
    },
    {
      key: 'gender',
      header: 'Gender',
      render: (item) => (
        <span className="capitalize">{(item.gender ?? '').toLowerCase() || '–'}</span>
      ),
    },
    {
      key: 'phone',
      header: 'Contact',
      render: (item) => {
        const phone = (item.phone ?? '').trim()
        const email = (item.email ?? '').trim()
        if (!phone && !email) return <span className="text-muted-foreground">–</span>
        return (
          <div className="flex flex-col gap-1">
            {phone && (
              <div className="flex items-center gap-1">
                <Phone className="w-3 h-3 text-muted-foreground" />
                <span className="text-xs">{phone}</span>
              </div>
            )}
            {email && (
              <div className="flex items-center gap-1">
                <Mail className="w-3 h-3 text-muted-foreground" />
                <span className="text-xs truncate max-w-[150px]">{email}</span>
              </div>
            )}
          </div>
        )
      },
    },
    {
      key: 'blood_type',
      header: 'Blood Type',
      render: (item) => (
        <span>{(item.blood_type ?? '').trim() || '–'}</span>
      ),
    },
  ]

  if (loading) {
    return (
      <div className={cn('p-8', className)}>
        <LoadingSpinner text="Loading patients..." />
      </div>
    )
  }

  if (error) {
    return (
      <div className={cn(className)}>
        <ErrorMessage message={error} />
      </div>
    )
  }

  return (
    <div className={cn(className)}>
      <DataTable
        columns={columns}
        data={Array.isArray(patients) ? patients : []}
        keyExtractor={(item) => item.id}
        emptyMessage="No patients found"
      />
    </div>
  )
}
