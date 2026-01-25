/**
 * Appointments List Component
 * 
 * Displays a list of appointments with consistent UI.
 */

import { Calendar, Clock, User, Stethoscope } from 'lucide-react'
import { useAppointments } from '@/hooks/useAppointments'
import { DataTable, Column, LoadingSpinner, ErrorMessage, EmptyState } from '@/components/common'
import { glassmorphism } from '@/lib/glassmorphism'
import { cn } from '@/lib/utils'
import type { Appointment } from '@/types/appointment.types'

interface AppointmentsListProps {
  patientId?: string
  doctorId?: string
  className?: string
}

export function AppointmentsList({
  patientId,
  doctorId,
  className,
}: AppointmentsListProps) {
  const { appointments, loading, error } = useAppointments({
    patientId,
    doctorId,
  })

  const formatDate = (dateString?: string | null) => {
    if (dateString == null || dateString === '') return '–'
    const d = new Date(dateString)
    if (Number.isNaN(d.getTime())) return '–'
    return d.toLocaleDateString('en-US', {
      year: 'numeric',
      month: 'short',
      day: 'numeric',
      hour: '2-digit',
      minute: '2-digit',
    })
  }

  const getStatusColor = (status: string) => {
    const colors: Record<string, string> = {
      SCHEDULED: 'bg-blue-500/20 text-blue-400',
      CONFIRMED: 'bg-green-500/20 text-green-400',
      COMPLETED: 'bg-gray-500/20 text-gray-400',
      CANCELLED: 'bg-red-500/20 text-red-400',
      NO_SHOW: 'bg-orange-500/20 text-orange-400',
    }
    return colors[status] || 'bg-gray-500/20 text-gray-400'
  }

  const columns: Column<Appointment>[] = [
    {
      key: 'appointment_number',
      header: 'Appointment #',
      render: (item) => (
        <span className="font-mono text-sm">{item.appointment_number ?? '–'}</span>
      ),
    },
    {
      key: 'patient_name',
      header: 'Patient',
      render: (item) => (
        <div className="flex items-center gap-2">
          <User className="w-4 h-4 text-muted-foreground" />
          <span>{(item.patient_name ?? '').trim() || 'N/A'}</span>
        </div>
      ),
    },
    {
      key: 'doctor_name',
      header: 'Doctor',
      render: (item) => (
        <div className="flex items-center gap-2">
          <Stethoscope className="w-4 h-4 text-muted-foreground" />
          <span>{(item.doctor_name ?? '').trim() || 'N/A'}</span>
        </div>
      ),
    },
    {
      key: 'appointment_date',
      header: 'Date & Time',
      render: (item) => (
        <div className="flex items-center gap-2">
          <Calendar className="w-4 h-4 text-muted-foreground" />
          <span>{formatDate(item?.appointment_date)}</span>
        </div>
      ),
    },
    {
      key: 'duration_minutes',
      header: 'Duration',
      render: (item) => (
        <div className="flex items-center gap-2">
          <Clock className="w-4 h-4 text-muted-foreground" />
          <span>{item.duration_minutes ?? 0} min</span>
        </div>
      ),
    },
    {
      key: 'status',
      header: 'Status',
      render: (item) => (
        <span
          className={cn(
            'px-2 py-1 rounded text-xs font-medium',
          getStatusColor(item.status ?? '')
        )}
        >
        {item.status ?? '–'}
        </span>
      ),
    },
  ]

  if (loading) {
    return (
      <div className={cn(glassmorphism('dark', true, true), 'rounded-lg p-8', className)}>
        <LoadingSpinner text="Loading appointments..." />
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
        data={Array.isArray(appointments) ? appointments : []}
        keyExtractor={(item) => item.id}
        emptyMessage="No appointments found"
      />
    </div>
  )
}
