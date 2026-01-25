/**
 * Work Queue Page
 *
 * Role-based:
 * - DOCTOR: My schedule (appointments) with patient status, visit status, fees paid; can update status.
 * - NURSE: Patient status and details (generic work queue).
 * - RECEPTIONIST / CLINIC_ADMIN: Work queue items and appointment management.
 */

import { useState, useEffect, useCallback } from 'react'
import { useAuth } from '@/hooks/useAuth'
import { Calendar, Clock, User, DollarSign, Loader2 } from 'lucide-react'
import { Link } from 'react-router-dom'
import { WorkQueueList } from '@/components/features/WorkQueueList'
import { appointmentService } from '@/services/appointment.service'
import { DataTable, Column, LoadingSpinner, ErrorMessage } from '@/components/common'
import { Button } from '@/components/ui/button'
import { glassmorphism } from '@/lib/glassmorphism'
import { cn } from '@/lib/utils'
import type { Appointment, AppointmentStatus } from '@/types/appointment.types'

const STATUS_OPTIONS: AppointmentStatus[] = [
  'SCHEDULED',
  'CONFIRMED',
  'IN_PROGRESS',
  'COMPLETED',
  'NO_SHOW',
]

function formatDate(dateString?: string | null) {
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

function getStatusColor(s: string) {
  const map: Record<string, string> = {
    SCHEDULED: 'bg-blue-500/20 text-blue-400',
    CONFIRMED: 'bg-green-500/20 text-green-400',
    IN_PROGRESS: 'bg-amber-500/20 text-amber-400',
    COMPLETED: 'bg-gray-500/20 text-gray-400',
    NO_SHOW: 'bg-orange-500/20 text-orange-400',
    CANCELLED: 'bg-red-500/20 text-red-400',
  }
  return map[s] ?? 'bg-gray-500/20 text-gray-400'
}

/** Doctor view: my schedule with patient status, visit status, fees paid; update status. */
function DoctorWorkQueueView() {
  const [appointments, setAppointments] = useState<Appointment[]>([])
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState<string | null>(null)
  const [updatingId, setUpdatingId] = useState<string | null>(null)

  const fetchSchedule = useCallback(async () => {
    setLoading(true)
    setError(null)
    try {
      const data = await appointmentService.getMySchedule(100)
      setAppointments(Array.isArray(data) ? data : [])
    } catch (e: unknown) {
      const msg = (e as { detail?: string })?.detail ?? (e as Error)?.message ?? 'Failed to load schedule'
      setError(String(msg))
      setAppointments([])
    } finally {
      setLoading(false)
    }
  }, [])

  useEffect(() => {
    fetchSchedule()
  }, [fetchSchedule])

  const handleStatusChange = async (app: Appointment, newStatus: AppointmentStatus) => {
    setUpdatingId(app.id)
    try {
      await appointmentService.updateAppointment(app.id, { status: newStatus })
      setAppointments((prev) =>
        prev.map((a) => (a.id === app.id ? { ...a, status: newStatus } : a))
      )
    } catch {
      // keep previous state; error could be shown via toast
    } finally {
      setUpdatingId(null)
    }
  }

  if (loading && appointments.length === 0) {
    return (
      <div className={cn(glassmorphism('dark', true, true), 'rounded-lg p-8')}>
        <LoadingSpinner text="Loading your schedule..." />
      </div>
    )
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
      header: 'Visit status',
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
    {
      key: 'fees_paid',
      header: 'Fees paid',
      render: (item) => (
        <div className="flex items-center gap-2">
          {item.fees_paid ? (
            <span className="text-green-500 text-sm font-medium">Yes</span>
          ) : (
            <span className="text-muted-foreground text-sm">No</span>
          )}
          {!item.fees_paid && (
            <Link to="/finance">
              <Button variant="ghost" size="sm" className="h-7 gap-1" title="Record payment in Finance">
                <DollarSign className="w-3 h-3" />
                Record
              </Button>
            </Link>
          )}
        </div>
      ),
    },
    {
      key: 'actions',
      header: 'Actions',
      render: (item) => (
        <div className="flex items-center gap-1">
          {updatingId === item.id ? (
            <Loader2 className="w-4 h-4 animate-spin text-muted-foreground" />
          ) : (
            <select
              className="rounded border border-input bg-background px-2 py-1 text-sm"
              value={item.status ?? 'SCHEDULED'}
              onChange={(e) => handleStatusChange(item, e.target.value as AppointmentStatus)}
            >
              {STATUS_OPTIONS.map((s) => (
                <option key={s} value={s}>
                  {s.replace('_', ' ')}
                </option>
              ))}
            </select>
          )}
        </div>
      ),
    },
  ]

  return (
    <div className="space-y-4">
      <p className="text-muted-foreground text-sm">
        Your next appointments. Update visit status and see whether fees have been paid.
      </p>
      {error && <ErrorMessage message={error} />}
      <DataTable
        columns={columns}
        data={appointments}
        keyExtractor={(item) => item.id}
        emptyMessage="No upcoming appointments"
      />
    </div>
  )
}

export default function WorkQueuePage() {
  const { user } = useAuth()
  const roles = (user?.role_names ?? []).map((r) => r.toUpperCase())
  const isDoctor = roles.includes('DOCTOR')

  return (
    <div className="space-y-6">
      <h1 className="text-2xl font-bold">Work Queue</h1>
      {isDoctor ? (
        <DoctorWorkQueueView />
      ) : (
        <>
          <p className="text-muted-foreground text-sm">
            Manage work items, patient status, and appointments.
          </p>
          <WorkQueueList />
        </>
      )}
    </div>
  )
}
