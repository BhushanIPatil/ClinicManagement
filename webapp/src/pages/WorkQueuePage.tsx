/**
 * Work Queue Page
 *
 * - Future appointments (clinic) and clinic work (tasks) with Create work button.
 * - DOCTOR: also "My schedule" with visit status and fees.
 */

import { useState, useEffect, useCallback } from 'react'
import { createPortal } from 'react-dom'
import { toast } from 'sonner'
import { useAuth } from '@/hooks/useAuth'
import { Calendar, Clock, User, DollarSign, Loader2, Plus } from 'lucide-react'
import { Link } from 'react-router-dom'
import { WorkQueueBoard } from '@/components/features/WorkQueueBoard'
import { appointmentService } from '@/services/appointment.service'
import { DataTable, Column, LoadingSpinner, ErrorMessage } from '@/components/common'
import { Button } from '@/components/ui/button'
import { Input } from '@/components/ui/input'
import { glassmorphism } from '@/lib/glassmorphism'
import { cn } from '@/lib/utils'
import type { Appointment, AppointmentStatus } from '@/types/appointment.types'
import type { WorkQueueCreateRequest } from '@/types/work-queue.types'
import { useWorkQueue } from '@/hooks/useWorkQueue'

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
      <div className={cn(glassmorphism('dark', false, false), 'rounded-lg p-8')}>
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
  const [createModalOpen, setCreateModalOpen] = useState(false)
  const [createSubmitting, setCreateSubmitting] = useState(false)
  const [createTitle, setCreateTitle] = useState('')
  const [createDescription, setCreateDescription] = useState('')
  const [createDueDate, setCreateDueDate] = useState('')
  const [createPriority, setCreatePriority] = useState<string>('NORMAL')
  const [listRefreshKey, setListRefreshKey] = useState(0)
  const { createItem } = useWorkQueue({ future_only: true, autoFetch: false })

  const handleCreateWork = useCallback(async () => {
    const title = (createTitle ?? '').trim()
    if (!title) {
      toast.warning('Title is required.')
      return
    }
    setCreateSubmitting(true)
    try {
      const payload: WorkQueueCreateRequest = {
        title,
        description: (createDescription ?? '').trim() || undefined,
        priority: (createPriority as 'LOW' | 'NORMAL' | 'HIGH') || 'NORMAL',
        entity_type: 'TASK',
      }
      if ((createDueDate ?? '').trim()) {
        payload.due_date = new Date(createDueDate).toISOString()
      }
      await createItem(payload)
      toast.success('Work item created.')
      setCreateModalOpen(false)
      setCreateTitle('')
      setCreateDescription('')
      setCreateDueDate('')
      setCreatePriority('NORMAL')
      setListRefreshKey((k) => k + 1)
    } catch (err: unknown) {
      const msg = (err as { detail?: string })?.detail ?? (err as Error)?.message ?? 'Failed to create work item'
      toast.error(msg)
    } finally {
      setCreateSubmitting(false)
    }
  }, [createTitle, createDescription, createDueDate, createPriority, createItem])

  return (
    <div className="space-y-6">
      <h1 className="text-2xl font-bold">Work Queue</h1>
      <p className="text-slate-400 text-sm">
        Future appointments and clinic work. Add work items visible to your clinic.
      </p>

      {isDoctor && (
        <section className="space-y-2">
          <h2 className="text-lg font-semibold text-slate-200">My schedule</h2>
          <DoctorWorkQueueView />
        </section>
      )}

      <section className="space-y-2">
        <div className="flex items-center justify-between">
          <h2 className="text-lg font-semibold text-slate-200">Clinic work</h2>
          <Button onClick={() => setCreateModalOpen(true)} className="gap-2">
            <Plus className="w-4 h-4" />
            Create work
          </Button>
        </div>
        <p className="text-slate-500 text-sm">Pending column includes upcoming appointments and clinic tasks. Move tasks between Pending, In progress, and Completed using the dropdown on each card.</p>
        <WorkQueueBoard key={listRefreshKey} />
      </section>

      {createModalOpen && createPortal(
        <div
          className="fixed inset-0 z-[100] flex items-center justify-center bg-black/70 min-h-screen w-screen"
          style={{ top: 0, left: 0, right: 0, bottom: 0 }}
          onClick={() => !createSubmitting && setCreateModalOpen(false)}
        >
          <div className="rounded-lg border border-slate-700 bg-slate-900 p-6 shadow-xl w-full max-w-md mx-4" onClick={(e) => e.stopPropagation()}>
            <h3 className="text-lg font-semibold text-slate-200 mb-4">Create work item</h3>
            <div className="space-y-4">
              <div>
                <label className="block text-sm text-slate-400 mb-1">Title *</label>
                <Input value={createTitle} onChange={(e) => setCreateTitle(e.target.value)} placeholder="Task title" className="bg-slate-800 border-slate-600" />
              </div>
              <div>
                <label className="block text-sm text-slate-400 mb-1">Description</label>
                <Input value={createDescription} onChange={(e) => setCreateDescription(e.target.value)} placeholder="Optional" className="bg-slate-800 border-slate-600" />
              </div>
              <div>
                <label className="block text-sm text-slate-400 mb-1">Due date</label>
                <Input type="datetime-local" value={createDueDate} onChange={(e) => setCreateDueDate(e.target.value)} className="bg-slate-800 border-slate-600" />
              </div>
              <div>
                <label className="block text-sm text-slate-400 mb-1">Priority</label>
                <select value={createPriority} onChange={(e) => setCreatePriority(e.target.value)} className="w-full rounded border border-slate-600 bg-slate-800 px-3 py-2 text-slate-200">
                  <option value="LOW">Low</option>
                  <option value="NORMAL">Normal</option>
                  <option value="HIGH">High</option>
                  <option value="URGENT">Urgent</option>
                </select>
              </div>
            </div>
            <div className="flex gap-2 mt-6 justify-end">
              <Button variant="outline" onClick={() => !createSubmitting && setCreateModalOpen(false)} disabled={createSubmitting}>Cancel</Button>
              <Button onClick={handleCreateWork} disabled={createSubmitting}>
                {createSubmitting ? <Loader2 className="w-4 h-4 animate-spin" /> : 'Create'}
              </Button>
            </div>
          </div>
        </div>,
        document.body
      )}
    </div>
  )
}
