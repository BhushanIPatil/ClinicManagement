/**
 * Appointments Page
 *
 * Add, list, edit, and cancel appointments. Used by CLINIC_ADMIN, RECEPTIONIST, DOCTOR.
 */

import { useState, useCallback, useMemo } from 'react'
import { createPortal } from 'react-dom'
import { toast } from 'sonner'
import { Calendar, Clock, User, Stethoscope, Plus, Pencil, X, DollarSign } from 'lucide-react'
import { useAuth } from '@/hooks/useAuth'
import { useAppointments } from '@/hooks/useAppointments'
import { appointmentService } from '@/services/appointment.service'
import { patientService } from '@/services/patient.service'
import { DataTable, Column, LoadingSpinner, ErrorMessage, PaginationState } from '@/components/common'
import { Button } from '@/components/ui/button'
import { Input } from '@/components/ui/input'
import { SearchableSelect } from '@/components/ui/searchable-select'
import { glassmorphism } from '@/lib/glassmorphism'
import { cn } from '@/lib/utils'
import type {
  Appointment,
  BookAppointmentRequest,
  UpdateAppointmentRequest,
  DoctorOption,
  PatientOption,
  AppointmentStatus,
  AppointmentType,
} from '@/types/appointment.types'

const STATUS_OPTIONS: AppointmentStatus[] = [
  'SCHEDULED',
  'CONFIRMED',
  'IN_PROGRESS',
  'COMPLETED',
  'CANCELLED',
  'NO_SHOW',
]
const TYPE_OPTIONS: AppointmentType[] = [
  'CONSULTATION',
  'FOLLOW_UP',
  'CHECKUP',
  'EMERGENCY',
  'SURGERY',
  'OTHER',
]

const PAYMENT_MODE_OPTIONS = [
  { value: 'CASH', label: 'Cash' },
  { value: 'CARD', label: 'Card' },
  { value: 'BANK_TRANSFER', label: 'Bank transfer' },
  { value: 'INSURANCE', label: 'Insurance' },
  { value: 'CHEQUE', label: 'Cheque' },
  { value: 'OTHER', label: 'Other' },
]

function toDatetimeLocal(iso?: string | null): string {
  if (!iso) return ''
  const d = new Date(iso)
  if (Number.isNaN(d.getTime())) return ''
  const y = d.getFullYear()
  const m = String(d.getMonth() + 1).padStart(2, '0')
  const day = String(d.getDate()).padStart(2, '0')
  const h = String(d.getHours()).padStart(2, '0')
  const min = String(d.getMinutes()).padStart(2, '0')
  return `${y}-${m}-${day}T${h}:${min}`
}

function fromDatetimeLocal(v: string): string {
  if (!v) return ''
  return new Date(v).toISOString()
}

export default function AppointmentsPage() {
  const { user } = useAuth()
  const {
    appointments,
    loading,
    error,
    fetchAppointments,
    bookAppointment,
    updateAppointment,
    cancelAppointment,
  } = useAppointments({ autoFetch: true })

  const [modalOpen, setModalOpen] = useState(false)
  const [editing, setEditing] = useState<Appointment | null>(null)
  const [cancelConfirmId, setCancelConfirmId] = useState<string | null>(null)
  const [doctors, setDoctors] = useState<DoctorOption[]>([])
  const [patients, setPatients] = useState<PatientOption[]>([])
  const [formSubmitting, setFormSubmitting] = useState(false)
  const [formError, setFormError] = useState<string | null>(null)

  // Patient payment modal
  const [paymentModalAppointment, setPaymentModalAppointment] = useState<Appointment | null>(null)
  const [paymentMode, setPaymentMode] = useState('CASH')
  const [paymentAmount, setPaymentAmount] = useState('')
  const [paymentDateTime, setPaymentDateTime] = useState(() => toDatetimeLocal(new Date().toISOString()))
  const [paymentSubmitting, setPaymentSubmitting] = useState(false)
  const [paymentError, setPaymentError] = useState<string | null>(null)

  const [page, setPage] = useState(1)
  const [pageSize, setPageSize] = useState(10)

  // Form fields
  const [patientId, setPatientId] = useState('')
  const [addNewPatient, setAddNewPatient] = useState(false)
  const [newPatientFirstName, setNewPatientFirstName] = useState('')
  const [newPatientLastName, setNewPatientLastName] = useState('')
  const [newPatientContact, setNewPatientContact] = useState('')
  const [newPatientAddress, setNewPatientAddress] = useState('')
  const [doctorId, setDoctorId] = useState('')
  const [appointmentDate, setAppointmentDate] = useState('')
  const [durationMinutes, setDurationMinutes] = useState(30)
  const [status, setStatus] = useState<AppointmentStatus>('SCHEDULED')
  const [appointmentType, setAppointmentType] = useState<AppointmentType>('CONSULTATION')
  const [notes, setNotes] = useState('')

  const clinicId = user?.primary_clinic_id ?? null
  const loadOptions = useCallback(async () => {
    try {
      const [d, p] = await Promise.all([
        appointmentService.getDoctorsOptions(200, clinicId),
        appointmentService.getPatientsOptions(),
      ])
      setDoctors(d)
      setPatients(p)
    } catch {
      setDoctors([])
      setPatients([])
    }
  }, [clinicId])

  const openAdd = useCallback(() => {
    setEditing(null)
    setPatientId('')
    setAddNewPatient(false)
    setNewPatientFirstName('')
    setNewPatientLastName('')
    setNewPatientContact('')
    setNewPatientAddress('')
    setDoctorId('')
    setAppointmentDate(toDatetimeLocal(new Date().toISOString()))
    setDurationMinutes(30)
    setStatus('SCHEDULED')
    setAppointmentType('CONSULTATION')
    setNotes('')
    setFormError(null)
    setModalOpen(true)
    loadOptions()
  }, [loadOptions])

  const openEdit = useCallback(
    (item: Appointment) => {
      setEditing(item)
      setPatientId(item.patient_id ?? '')
      setDoctorId(item.doctor_id ?? '')
      setAppointmentDate(toDatetimeLocal(item.appointment_date))
      setDurationMinutes(item.duration_minutes ?? 30)
      setStatus((item.status as AppointmentStatus) ?? 'SCHEDULED')
      setAppointmentType((item.appointment_type as AppointmentType) ?? 'CONSULTATION')
      setNotes(item.notes ?? '')
      setFormError(null)
      setModalOpen(true)
      loadOptions()
    },
    [loadOptions]
  )

  const closeModal = useCallback(() => {
    setModalOpen(false)
    setEditing(null)
    setFormError(null)
  }, [])

  const handleSubmit = useCallback(async () => {
    setFormSubmitting(true)
    setFormError(null)
    try {
      if (editing) {
        const payload: UpdateAppointmentRequest = {
          appointment_date: appointmentDate ? fromDatetimeLocal(appointmentDate) : undefined,
          duration_minutes: durationMinutes,
          status,
          appointment_type: appointmentType,
          notes: notes || undefined,
          doctor_id: doctorId || undefined,
        }
        await updateAppointment(editing.id, payload)
      } else {
        if (!doctorId || !appointmentDate) {
          const msg = 'Doctor and date/time are required.'
          setFormError(msg)
          toast.warning(msg)
          return
        }
        let resolvedPatientId = patientId
        if (addNewPatient) {
          const fn = (newPatientFirstName || '').trim()
          const ln = (newPatientLastName || '').trim()
          if (!fn || !ln) {
            const msg = 'Patient name (first and last name) is required.'
            setFormError(msg)
            toast.warning(msg)
            return
          }
          const contact = (newPatientContact || '').trim()
          const address = (newPatientAddress || '').trim()
          const newPatient = await patientService.createPatient({
            first_name: fn,
            last_name: ln,
            phone: contact || undefined,
            address: address || undefined,
            gender: 'OTHER',
          })
          resolvedPatientId = newPatient.id
        } else {
          if (!patientId) {
            const msg = 'Select a patient or add a new patient.'
            setFormError(msg)
            toast.warning(msg)
            return
          }
        }
        const payload: BookAppointmentRequest = {
          patient_id: resolvedPatientId,
          doctor_id: doctorId,
          appointment_date: fromDatetimeLocal(appointmentDate),
          duration_minutes: durationMinutes,
          appointment_type: appointmentType,
          notes: notes || undefined,
        }
        await bookAppointment(payload)
      }
      closeModal()
      toast.success(editing ? 'Appointment updated.' : 'Appointment booked.')
    } catch (e: any) {
      const msg = e?.detail ?? e?.message ?? 'Request failed'
      setFormError(msg)
      toast.error(msg)
    } finally {
      setFormSubmitting(false)
    }
  }, [
    editing,
    patientId,
    addNewPatient,
    newPatientFirstName,
    newPatientLastName,
    newPatientContact,
    newPatientAddress,
    doctorId,
    appointmentDate,
    durationMinutes,
    status,
    appointmentType,
    notes,
    updateAppointment,
    bookAppointment,
    closeModal,
  ])

  const handleCancelAppointment = useCallback(
    async (item: Appointment) => {
      try {
        await cancelAppointment(item.id, { reason: 'Cancelled by user' })
        setCancelConfirmId(null)
        toast.success('Appointment cancelled.')
      } catch {
        toast.error('Failed to cancel appointment.')
      }
    },
    [cancelAppointment]
  )

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

  const getStatusColor = (s: string) => {
    const map: Record<string, string> = {
      SCHEDULED: 'bg-blue-500/20 text-blue-400',
      CONFIRMED: 'bg-green-500/20 text-green-400',
      IN_PROGRESS: 'bg-amber-500/20 text-amber-400',
      COMPLETED: 'bg-gray-500/20 text-gray-400',
      CANCELLED: 'bg-red-500/20 text-red-400',
      NO_SHOW: 'bg-orange-500/20 text-orange-400',
    }
    return map[s] ?? 'bg-gray-500/20 text-gray-400'
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
    {
      key: 'paid',
      header: 'Paid',
      render: (item) => (
        <span
          className={cn(
            'px-2 py-1 rounded text-xs font-medium',
            item.paid ? 'bg-green-500/20 text-green-400' : 'bg-amber-500/20 text-amber-400'
          )}
        >
          {item.paid ? 'Paid' : 'Unpaid'}
        </span>
      ),
    },
    {
      key: 'actions',
      header: 'Actions',
      render: (item) => (
        <div className="flex items-center gap-1">
          {cancelConfirmId === item.id ? (
            <>
              <Button
                variant="destructive"
                size="sm"
                onClick={() => handleCancelAppointment(item)}
              >
                Confirm
              </Button>
              <Button variant="ghost" size="sm" onClick={() => setCancelConfirmId(null)}>
                Back
              </Button>
            </>
          ) : (
            <>
              <Button variant="ghost" size="icon" title="Edit" onClick={() => openEdit(item)}>
                <Pencil className="w-4 h-4" />
              </Button>
              {item.status !== 'CANCELLED' && (
                <Button
                  variant="ghost"
                  size="icon"
                  title="Add patient payment"
                  onClick={() => {
                    setPaymentModalAppointment(item)
                    setPaymentAmount('')
                    setPaymentMode('CASH')
                    setPaymentDateTime(toDatetimeLocal(new Date().toISOString()))
                    setPaymentError(null)
                  }}
                >
                  <DollarSign className="w-4 h-4" />
                </Button>
              )}
              {item.status !== 'CANCELLED' && (
                <Button
                  variant="ghost"
                  size="icon"
                  title="Cancel appointment"
                  onClick={() => setCancelConfirmId(item.id)}
                >
                  <X className="w-4 h-4 text-destructive" />
                </Button>
              )}
            </>
          )}
        </div>
      ),
    },
  ]

  const appointmentsList = Array.isArray(appointments) ? appointments : []
  const appointmentsPagination: PaginationState = useMemo(
    () => ({ page, pageSize, total: appointmentsList.length }),
    [page, pageSize, appointmentsList.length]
  )
  const paginatedAppointments = useMemo(
    () => appointmentsList.slice((page - 1) * pageSize, page * pageSize),
    [appointmentsList, page, pageSize]
  )
  const onAppointmentsPageChange = useCallback((p: number, ps: number) => {
    setPage(p)
    setPageSize(ps)
  }, [])

  const handleAddPayment = useCallback(async () => {
    if (!paymentModalAppointment) return
    const amt = Number(paymentAmount)
    if (!Number.isFinite(amt) || amt <= 0) {
      const msg = 'Enter a valid amount.'
      setPaymentError(msg)
      toast.warning(msg)
      return
    }
    setPaymentSubmitting(true)
    setPaymentError(null)
    try {
      await appointmentService.addPatientPayment(paymentModalAppointment.id, {
        amount: amt,
        payment_method: paymentMode,
        payment_date: fromDatetimeLocal(paymentDateTime) || new Date().toISOString(),
      })
      setPaymentModalAppointment(null)
      fetchAppointments()
      toast.success('Payment recorded.')
    } catch (e: unknown) {
      const msg = (e as { detail?: string })?.detail ?? (e as Error)?.message ?? 'Failed to add payment'
      setPaymentError(String(msg))
      toast.error(msg)
    } finally {
      setPaymentSubmitting(false)
    }
  }, [paymentModalAppointment, paymentAmount, paymentMode, paymentDateTime, fetchAppointments])

  if (loading && appointments.length === 0) {
    return (
      <div className="space-y-6">
        <h1 className="text-2xl font-bold">Appointments</h1>
        <div className={cn(glassmorphism('dark', false, false), 'rounded-lg p-8')}>
          <LoadingSpinner text="Loading appointments..." />
        </div>
      </div>
    )
  }

  return (
    <div className="space-y-6">
      <div className="flex items-center justify-between">
        <h1 className="text-2xl font-bold">Appointments</h1>
        <Button onClick={openAdd} className="gap-2">
          <Plus className="w-4 h-4" />
          Add appointment
        </Button>
      </div>

      {error && (
        <ErrorMessage message={error} />
      )}

      <div>
        <DataTable
          columns={columns}
          data={paginatedAppointments}
          keyExtractor={(item) => item.id}
          emptyMessage="No appointments found"
          pagination={appointmentsPagination}
          onPageChange={onAppointmentsPageChange}
        />
      </div>

      {/* Add/Edit modal - portaled so overlay covers full viewport */}
      {modalOpen && createPortal(
        <div
          className="fixed inset-0 z-[100] flex items-center justify-center bg-black/70 min-h-screen w-screen"
          style={{ top: 0, left: 0, right: 0, bottom: 0 }}
          onClick={closeModal}
        >
          <div
            className={cn(
              glassmorphism('dark', false, false),
              'rounded-xl border border-white/20 w-full max-w-lg max-h-[90vh] overflow-y-auto shadow-xl mx-4'
            )}
            onClick={(e) => e.stopPropagation()}
          >
            <div className="p-6 space-y-4">
              <h2 className="text-lg font-semibold">
                {editing ? 'Edit appointment' : 'Add appointment'}
              </h2>
              {formError && (
                <p className="text-sm text-destructive">{formError}</p>
              )}
              <div className="grid gap-2">
                <label className="text-sm font-medium text-muted-foreground">Patient</label>
                {editing ? (
                  <SearchableSelect
                    options={patients.map((p) => ({ id: p.id, label: p.label }))}
                    value={patientId}
                    onValueChange={setPatientId}
                    placeholder="Select patient"
                    searchPlaceholder="Search patient..."
                    disabled={true}
                    emptyMessage="No patients found"
                  />
                ) : addNewPatient ? (
                  <div className="space-y-3 rounded-lg border border-white/10 bg-white/5 p-3">
                    <div className="flex items-center justify-between">
                      <span className="text-sm font-medium text-muted-foreground">New patient</span>
                      <Button
                        type="button"
                        variant="ghost"
                        size="sm"
                        className="text-xs"
                        onClick={() => {
                          setAddNewPatient(false)
                          setNewPatientFirstName('')
                          setNewPatientLastName('')
                          setNewPatientContact('')
                          setNewPatientAddress('')
                        }}
                      >
                        Choose existing patient
                      </Button>
                    </div>
                    <div className="grid grid-cols-2 gap-2">
                      <div className="grid gap-1">
                        <label className="text-xs text-muted-foreground">First name *</label>
                        <Input
                          value={newPatientFirstName}
                          onChange={(e) => setNewPatientFirstName(e.target.value)}
                          placeholder="First name"
                        />
                      </div>
                      <div className="grid gap-1">
                        <label className="text-xs text-muted-foreground">Last name *</label>
                        <Input
                          value={newPatientLastName}
                          onChange={(e) => setNewPatientLastName(e.target.value)}
                          placeholder="Last name"
                        />
                      </div>
                    </div>
                    <div className="grid gap-1">
                      <label className="text-xs text-muted-foreground">Contact (phone)</label>
                      <Input
                        type="tel"
                        value={newPatientContact}
                        onChange={(e) => setNewPatientContact(e.target.value)}
                        placeholder="Phone number (optional)"
                      />
                    </div>
                    <div className="grid gap-1">
                      <label className="text-xs text-muted-foreground">Address</label>
                      <textarea
                        className="flex min-h-[60px] w-full rounded-md border border-input bg-background px-3 py-2 text-sm"
                        value={newPatientAddress}
                        onChange={(e) => setNewPatientAddress(e.target.value)}
                        placeholder="Address (optional)"
                      />
                    </div>
                  </div>
                ) : (
                  <>
                    <SearchableSelect
                      options={patients.map((p) => ({ id: p.id, label: p.label }))}
                      value={patientId}
                      onValueChange={setPatientId}
                      placeholder="Select patient"
                      searchPlaceholder="Search patient..."
                      emptyMessage="No patients found"
                    />
                    <Button
                      type="button"
                      variant="outline"
                      size="sm"
                      className="w-full"
                      onClick={() => setAddNewPatient(true)}
                    >
                      <User className="w-4 h-4 mr-2" />
                      Add new patient
                    </Button>
                  </>
                )}
              </div>
              <div className="grid gap-2">
                <label className="text-sm font-medium text-muted-foreground">Doctor</label>
                <SearchableSelect
                  options={doctors.map((d) => ({ id: d.id, label: d.label }))}
                  value={doctorId}
                  onValueChange={setDoctorId}
                  placeholder="Select doctor"
                  searchPlaceholder="Search doctor..."
                  emptyMessage="No doctors found"
                />
              </div>
              <div className="grid gap-2">
                <label className="text-sm font-medium text-muted-foreground">
                  Date & time
                </label>
                <input
                  type="datetime-local"
                  className="flex h-10 w-full rounded-md border border-input bg-background px-3 py-2 text-sm"
                  value={appointmentDate}
                  onChange={(e) => setAppointmentDate(e.target.value)}
                />
              </div>
              <div className="grid gap-2">
                <label className="text-sm font-medium text-muted-foreground">
                  Duration (minutes)
                </label>
                <Input
                  type="number"
                  min={1}
                  max={480}
                  value={durationMinutes}
                  onChange={(e) => setDurationMinutes(Number(e.target.value) || 30)}
                />
              </div>
              {editing && (
                <div className="grid gap-2">
                  <label className="text-sm font-medium text-muted-foreground">Status</label>
                  <select
                    className="flex h-10 w-full rounded-md border border-input bg-background px-3 py-2 text-sm"
                    value={status}
                    onChange={(e) => setStatus(e.target.value as AppointmentStatus)}
                  >
                    {STATUS_OPTIONS.map((s) => (
                      <option key={s} value={s}>
                        {s}
                      </option>
                    ))}
                  </select>
                </div>
              )}
              <div className="grid gap-2">
                <label className="text-sm font-medium text-muted-foreground">Type</label>
                <select
                  className="flex h-10 w-full rounded-md border border-input bg-background px-3 py-2 text-sm"
                  value={appointmentType}
                  onChange={(e) => setAppointmentType(e.target.value as AppointmentType)}
                >
                  {TYPE_OPTIONS.map((t) => (
                    <option key={t} value={t}>
                      {t}
                    </option>
                  ))}
                </select>
              </div>
              <div className="grid gap-2">
                <label className="text-sm font-medium text-muted-foreground">Notes</label>
                <textarea
                  className="flex min-h-[80px] w-full rounded-md border border-input bg-background px-3 py-2 text-sm"
                  value={notes}
                  onChange={(e) => setNotes(e.target.value)}
                  placeholder="Optional notes"
                />
              </div>
              <div className="flex justify-end gap-2 pt-2">
                <Button variant="outline" onClick={closeModal} disabled={formSubmitting}>
                  Cancel
                </Button>
                <Button onClick={handleSubmit} disabled={formSubmitting}>
                  {formSubmitting ? 'Saving...' : editing ? 'Update' : 'Add'}
                </Button>
              </div>
            </div>
          </div>
        </div>,
        document.body
      )}

      {/* Patient payment modal - portaled so overlay covers full viewport */}
      {paymentModalAppointment && createPortal(
        <div
          className="fixed inset-0 z-[100] flex items-center justify-center bg-black/70 min-h-screen w-screen"
          style={{ top: 0, left: 0, right: 0, bottom: 0 }}
          onClick={() => {
            setPaymentModalAppointment(null)
            setPaymentError(null)
          }}
        >
          <div
            className={cn(
              glassmorphism('dark', false, false),
              'rounded-xl border border-white/20 w-full max-w-md max-h-[90vh] overflow-y-auto shadow-xl mx-4'
            )}
            onClick={(e) => e.stopPropagation()}
          >
            <div className="p-6 space-y-4">
              <h2 className="text-lg font-semibold">Add patient payment</h2>
              <p className="text-sm text-muted-foreground">
                {paymentModalAppointment.patient_name && (
                  <>Patient: {paymentModalAppointment.patient_name}</>
                )}
                {paymentModalAppointment.appointment_number && (
                  <> · #{paymentModalAppointment.appointment_number}</>
                )}
              </p>
              {paymentError && (
                <p className="text-sm text-destructive">{paymentError}</p>
              )}
              <div className="grid gap-2">
                <label className="text-sm font-medium text-muted-foreground">
                  Payment mode
                </label>
                <select
                  className="flex h-10 w-full rounded-md border border-input bg-background px-3 py-2 text-sm"
                  value={paymentMode}
                  onChange={(e) => setPaymentMode(e.target.value)}
                >
                  {PAYMENT_MODE_OPTIONS.map((o) => (
                    <option key={o.value} value={o.value}>
                      {o.label}
                    </option>
                  ))}
                </select>
              </div>
              <div className="grid gap-2">
                <label className="text-sm font-medium text-muted-foreground">
                  Amount
                </label>
                <Input
                  type="number"
                  min={0}
                  step="0.01"
                  placeholder="0.00"
                  value={paymentAmount}
                  onChange={(e) => setPaymentAmount(e.target.value)}
                />
              </div>
              <div className="grid gap-2">
                <label className="text-sm font-medium text-muted-foreground">
                  Paid date & time
                </label>
                <input
                  type="datetime-local"
                  className="flex h-10 w-full rounded-md border border-input bg-background px-3 py-2 text-sm"
                  value={paymentDateTime}
                  onChange={(e) => setPaymentDateTime(e.target.value)}
                />
              </div>
              <div className="flex justify-end gap-2 pt-2">
                <Button
                  variant="outline"
                  onClick={() => {
                    setPaymentModalAppointment(null)
                    setPaymentError(null)
                  }}
                  disabled={paymentSubmitting}
                >
                  Cancel
                </Button>
                <Button onClick={handleAddPayment} disabled={paymentSubmitting}>
                  {paymentSubmitting ? 'Adding...' : 'Add payment'}
                </Button>
              </div>
            </div>
          </div>
        </div>,
        document.body
      )}
    </div>
  )
}
