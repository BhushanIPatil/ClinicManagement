/**
 * Work Queue Task Board (sprint-style)
 * Columns: Pending (includes upcoming appointments) | In Progress | Completed | Cancelled
 */

import { useMemo, useState, useEffect, useCallback } from 'react'
import { toast } from 'sonner'
import { Calendar, User, Loader2, GripVertical, Stethoscope } from 'lucide-react'
import { Link } from 'react-router-dom'
import { useWorkQueue } from '@/hooks/useWorkQueue'
import { appointmentService } from '@/services/appointment.service'
import { LoadingSpinner, ErrorMessage } from '@/components/common'
import { cn } from '@/lib/utils'
import type { WorkQueueItem, WorkQueueStatus } from '@/types/work-queue.types'
import type { Appointment } from '@/types/appointment.types'

const BOARD_COLUMNS: { status: WorkQueueStatus; label: string; headerClass: string }[] = [
  { status: 'PENDING', label: 'Pending', headerClass: 'border-amber-500/40 bg-amber-500/5' },
  { status: 'IN_PROGRESS', label: 'In progress', headerClass: 'border-blue-500/40 bg-blue-500/5' },
  { status: 'COMPLETED', label: 'Completed', headerClass: 'border-emerald-500/40 bg-emerald-500/5' },
  { status: 'CANCELLED', label: 'Cancelled', headerClass: 'border-slate-500/40 bg-slate-500/5' },
]

function formatAppointmentDate(s: string | null | undefined): string {
  if (!s) return '–'
  const d = new Date(s)
  if (Number.isNaN(d.getTime())) return '–'
  return d.toLocaleDateString('en-US', { month: 'short', day: 'numeric', year: 'numeric', hour: '2-digit', minute: '2-digit' })
}

function appointmentStatusClass(s: string): string {
  const m: Record<string, string> = {
    SCHEDULED: 'bg-blue-500/20 text-blue-400',
    CONFIRMED: 'bg-emerald-500/20 text-emerald-400',
    IN_PROGRESS: 'bg-amber-500/20 text-amber-400',
    COMPLETED: 'bg-slate-500/20 text-slate-400',
    CANCELLED: 'bg-red-500/20 text-red-400',
    NO_SHOW: 'bg-orange-500/20 text-orange-400',
  }
  return m[s] ?? 'bg-slate-500/20 text-slate-400'
}

function priorityClass(p: string): string {
  const m: Record<string, string> = {
    URGENT: 'bg-red-500/20 text-red-400',
    HIGH: 'bg-orange-500/20 text-orange-400',
    NORMAL: 'bg-slate-500/20 text-slate-400',
    MEDIUM: 'bg-yellow-500/20 text-yellow-400',
    LOW: 'bg-blue-500/20 text-blue-400',
  }
  return m[p] ?? 'bg-slate-500/20 text-slate-400'
}

function formatDue(s: string | null | undefined): string {
  if (!s) return '–'
  const d = new Date(s)
  if (Number.isNaN(d.getTime())) return '–'
  return d.toLocaleDateString('en-US', { month: 'short', day: 'numeric', year: 'numeric', hour: '2-digit', minute: '2-digit' })
}

interface WorkQueueBoardProps {
  className?: string
  /** Pass a key from parent to force refetch (e.g. after creating an item) */
  refreshKey?: number
}

export function WorkQueueBoard({ className, refreshKey }: WorkQueueBoardProps) {
  const { items, loading, error, updateItem } = useWorkQueue({
    autoFetch: true,
    future_only: false,
  })
  const [appointments, setAppointments] = useState<Appointment[]>([])
  const [appointmentsLoading, setAppointmentsLoading] = useState(true)
  const [movingId, setMovingId] = useState<string | null>(null)

  const fetchAppointments = useCallback(async () => {
    setAppointmentsLoading(true)
    try {
      const data = await appointmentService.getUpcomingAppointments(100)
      setAppointments(Array.isArray(data) ? data : [])
    } catch {
      setAppointments([])
    } finally {
      setAppointmentsLoading(false)
    }
  }, [])

  useEffect(() => {
    fetchAppointments()
  }, [fetchAppointments, refreshKey])

  const byStatus = useMemo(() => {
    const map: Record<string, WorkQueueItem[]> = {
      PENDING: [],
      IN_PROGRESS: [],
      COMPLETED: [],
      CANCELLED: [],
    }
    for (const item of items) {
      const s = (item.status ?? 'PENDING') as WorkQueueStatus
      if (map[s]) map[s].push(item)
      else map.PENDING.push(item)
    }
    return map
  }, [items])

  const handleStatusChange = async (item: WorkQueueItem, newStatus: WorkQueueStatus) => {
    if ((item.status ?? '') === newStatus) return
    setMovingId(item.id)
    try {
      await updateItem(item.id, { status: newStatus })
      toast.success('Status updated.')
    } catch (err: unknown) {
      const msg = (err as { detail?: string })?.detail ?? (err as Error)?.message ?? 'Failed to update status'
      toast.error(msg)
    } finally {
      setMovingId(null)
    }
  }

  if (loading && items.length === 0 && !appointments.length) {
    return (
      <div className={cn('rounded-lg border border-slate-700/50 bg-slate-900/40 p-8', className)}>
        <LoadingSpinner text="Loading board..." />
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

  const pendingCount = byStatus.PENDING.length + (appointmentsLoading ? 0 : appointments.length)

  return (
    <div className={cn('flex gap-4 overflow-x-auto pb-2 min-h-[320px]', className)}>
      {BOARD_COLUMNS.map((col) => (
        <div
          key={col.status}
          className={cn(
            'flex flex-col w-[280px] shrink-0 rounded-lg border',
            col.headerClass
          )}
        >
          <div className={cn('px-3 py-2 border-b border-slate-700/50 flex items-center justify-between')}>
            <span className="font-semibold text-slate-200">{col.label}</span>
            <span className="text-sm text-slate-400 tabular-nums">
              {col.status === 'PENDING' ? pendingCount : byStatus[col.status].length}
            </span>
          </div>
          <div className="flex-1 overflow-y-auto p-2 space-y-2 min-h-[200px]">
            {/* Pending column: show upcoming appointments first, then Pending tasks */}
            {col.status === 'PENDING' && (
              <>
                {appointmentsLoading ? (
                  <div className="flex items-center justify-center py-4">
                    <Loader2 className="w-5 h-5 animate-spin text-slate-500" />
                  </div>
                ) : (
                  appointments.map((app) => (
                    <Link
                      key={`app-${app.id}`}
                      to="/appointments"
                      className="block rounded-lg border border-slate-600/50 bg-slate-800/60 p-3 shadow-sm transition-shadow hover:shadow-md hover:border-amber-500/30"
                    >
                      <p className="font-mono text-xs text-slate-400 mb-1">{app.appointment_number ?? '–'}</p>
                      <p className="font-medium text-slate-200 text-sm leading-tight">
                        {(app.patient_name ?? '').trim() || 'Patient'}
                      </p>
                      <div className="flex items-center gap-1 mt-1.5 text-xs text-slate-400">
                        <Stethoscope className="w-3 h-3 shrink-0" />
                        <span className="truncate">{(app.doctor_name ?? '').trim() || '–'}</span>
                      </div>
                      <div className="flex items-center gap-1 mt-1.5 text-xs text-slate-400">
                        <Calendar className="w-3 h-3 shrink-0" />
                        {formatAppointmentDate(app.appointment_date)}
                      </div>
                      <span className={cn('inline-block mt-2 px-1.5 py-0.5 rounded text-xs font-medium', appointmentStatusClass(app.status ?? ''))}>
                        {app.status ?? '–'}
                      </span>
                    </Link>
                  ))
                )}
              </>
            )}
            {byStatus[col.status].map((item) => (
              <div
                key={item.id}
                className={cn(
                  'rounded-lg border border-slate-600/50 bg-slate-800/60 p-3 shadow-sm transition-shadow hover:shadow-md',
                  movingId === item.id && 'opacity-70 pointer-events-none'
                )}
              >
                <div className="flex items-start gap-2">
                  <GripVertical className="w-4 h-4 text-slate-500 shrink-0 mt-0.5" aria-hidden />
                  <div className="flex-1 min-w-0">
                    <p className="font-medium text-slate-200 text-sm leading-tight truncate" title={item.title}>
                      {(item.title ?? '').trim() || 'Untitled'}
                    </p>
                    {item.description && (
                      <p className="text-xs text-slate-400 mt-1 line-clamp-2">{(item.description ?? '').trim()}</p>
                    )}
                    <div className="flex flex-wrap items-center gap-2 mt-2">
                      <span className={cn('px-1.5 py-0.5 rounded text-xs font-medium', priorityClass(item.priority ?? 'NORMAL'))}>
                        {item.priority ?? 'NORMAL'}
                      </span>
                      {item.due_date && (
                        <span className="flex items-center gap-1 text-xs text-slate-400">
                          <Calendar className="w-3 h-3" />
                          {formatDue(item.due_date)}
                        </span>
                      )}
                    </div>
                    {item.assigned_to_user_name && item.assigned_to_user_name !== 'N/A' && (
                      <div className="flex items-center gap-1 mt-1.5 text-xs text-slate-500">
                        <User className="w-3 h-3" />
                        {item.assigned_to_user_name}
                      </div>
                    )}
                    <div className="mt-2 pt-2 border-t border-slate-700/50">
                      <select
                        className="w-full rounded border border-slate-600 bg-slate-700/50 px-2 py-1.5 text-xs text-slate-200 focus:outline-none focus:ring-1 focus:ring-slate-500"
                        value={item.status ?? 'PENDING'}
                        onChange={(e) => handleStatusChange(item, e.target.value as WorkQueueStatus)}
                        disabled={movingId === item.id}
                      >
                        {BOARD_COLUMNS.map((c) => (
                          <option key={c.status} value={c.status}>
                            {c.label}
                          </option>
                        ))}
                      </select>
                    </div>
                  </div>
                  {movingId === item.id && (
                    <Loader2 className="w-4 h-4 animate-spin text-slate-400 shrink-0" />
                  )}
                </div>
              </div>
            ))}
          </div>
        </div>
      ))}
    </div>
  )
}
