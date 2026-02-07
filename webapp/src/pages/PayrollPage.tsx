/**
 * Payroll Page
 * Add users to payroll, manage roster (joining date, role, salary structure, payment status, payment dates),
 * track updated by / updated at, and generate payslip/invoice for download (client-side, no storage).
 */

import { useCallback, useEffect, useState, useMemo } from 'react'
import { createPortal } from 'react-dom'
import { toast } from 'sonner'
import { UserPlus, RefreshCw, Pencil, Trash2, Download, FileText, Loader2 } from 'lucide-react'
import { useAuth } from '@/hooks/useAuth'
import { payrollService } from '@/services/payroll.service'
import type {
  PayrollRosterItem,
  ClinicUserForPayroll,
  AddToRosterRequest,
  UpdateRosterRequest,
  SalaryStructureBackend,
  PayrollRun,
  PayslipItem,
} from '@/types/payroll.types'
import { Button } from '@/components/ui/button'
import { Input } from '@/components/ui/input'
import { DataTable, Column, LoadingSpinner, ErrorMessage, PaginationState } from '@/components/common'
import { glassmorphism } from '@/lib/glassmorphism'
import { cn } from '@/lib/utils'
import { buildPayslipHtml, buildInvoiceHtml, printPayslip } from '@/lib/payroll-download'

const DEFAULT_PAGE_SIZE = 10
const ROLES = ['NURSE', 'HR_OPERATIONS', 'RECEPTIONIST', 'DOCTOR', 'CLINIC_ADMIN']

export default function PayrollPage() {
  const { user } = useAuth()
  const [roster, setRoster] = useState<PayrollRosterItem[]>([])
  const [rosterTotal, setRosterTotal] = useState(0)
  const [clinicUsers, setClinicUsers] = useState<ClinicUserForPayroll[]>([])
  const [salaryStructures, setSalaryStructures] = useState<SalaryStructureBackend[]>([])
  const [payrollRuns, setPayrollRuns] = useState<PayrollRun[]>([])
  const [payslips, setPayslips] = useState<PayslipItem[]>([])
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState<string | null>(null)
  const [page, setPage] = useState(1)
  const [pageSize, setPageSize] = useState(DEFAULT_PAGE_SIZE)

  const [addModalOpen, setAddModalOpen] = useState(false)
  const [editRow, setEditRow] = useState<PayrollRosterItem | null>(null)
  const [createRunModalOpen, setCreateRunModalOpen] = useState(false)
  const [createStructureModalOpen, setCreateStructureModalOpen] = useState(false)
  const [formSubmitting, setFormSubmitting] = useState(false)
  const [formError, setFormError] = useState<string | null>(null)

  const loadRoster = useCallback(async () => {
    try {
      const res = await payrollService.listRoster({ skip: 0, limit: 500 })
      setRoster(res.items)
      setRosterTotal(res.total)
    } catch {
      setRoster([])
      setRosterTotal(0)
    }
  }, [])

  const loadClinicUsers = useCallback(async () => {
    try {
      const res = await payrollService.listClinicUsersForPayroll()
      setClinicUsers(res.items)
    } catch {
      setClinicUsers([])
    }
  }, [])

  const loadSalaryStructures = useCallback(async () => {
    try {
      const res = await payrollService.listSalaryStructures({ skip: 0, limit: 200 })
      setSalaryStructures(res.items)
    } catch {
      setSalaryStructures([])
    }
  }, [])

  const loadPayrollRuns = useCallback(async () => {
    try {
      const res = await payrollService.listPayrollRuns({ skip: 0, limit: 50 })
      setPayrollRuns(res.items)
    } catch {
      setPayrollRuns([])
    }
  }, [])

  const loadPayslips = useCallback(async () => {
    try {
      const res = await payrollService.listPayslips({ skip: 0, limit: 100 })
      setPayslips(res.items)
    } catch {
      setPayslips([])
    }
  }, [])

  const loadAll = useCallback(async () => {
    setLoading(true)
    setError(null)
    try {
      await Promise.all([
        loadRoster(),
        loadClinicUsers(),
        loadSalaryStructures(),
        loadPayrollRuns(),
        loadPayslips(),
      ])
    } catch (err: unknown) {
      const msg =
        err && typeof err === 'object' && 'detail' in err
          ? String((err as { detail: unknown }).detail)
          : err instanceof Error
            ? err.message
            : 'Failed to load payroll'
      setError(msg)
      toast.error(msg)
    } finally {
      setLoading(false)
    }
  }, [loadRoster, loadClinicUsers, loadSalaryStructures, loadPayrollRuns, loadPayslips])

  useEffect(() => {
    loadAll()
  }, [loadAll])

  const openAddModal = useCallback(() => {
    setFormError(null)
    setAddModalOpen(true)
  }, [])

  const closeAddModal = useCallback(() => {
    setAddModalOpen(false)
    setFormError(null)
  }, [])

  const openEditModal = useCallback((row: PayrollRosterItem) => {
    setEditRow(row)
    setFormError(null)
  }, [])

  const closeEditModal = useCallback(() => {
    setEditRow(null)
    setFormError(null)
  }, [])

  const pagination: PaginationState = useMemo(
    () => ({ page, pageSize, total: rosterTotal }),
    [page, pageSize, rosterTotal]
  )
  const paginatedRoster = useMemo(
    () => roster.slice((page - 1) * pageSize, page * pageSize),
    [roster, page, pageSize]
  )
  const onPageChange = useCallback((p: number, ps: number) => {
    setPage(p)
    setPageSize(ps)
  }, [])

  const handleDownloadPayslip = useCallback((row: PayrollRosterItem) => {
    const html = buildPayslipHtml({
      user_name: row.user_name,
      joining_date: row.joining_date,
      role: row.role,
      base_salary: row.base_salary ?? 0,
      gross_salary: row.gross_salary ?? 0,
      net_salary: row.net_salary ?? 0,
    })
    printPayslip(html)
    toast.success('Payslip opened for print / Save as PDF')
  }, [])

  const handleDownloadInvoice = useCallback((row: PayrollRosterItem) => {
    const html = buildInvoiceHtml({
      user_name: row.user_name,
      joining_date: row.joining_date,
      role: row.role,
      base_salary: row.base_salary ?? 0,
      gross_salary: row.gross_salary ?? 0,
      net_salary: row.net_salary ?? 0,
    })
    printPayslip(html)
    toast.success('Invoice opened for print / Save as PDF')
  }, [])

  const handleDownloadPayslipFromPayslip = useCallback((item: PayslipItem) => {
    const html = buildPayslipHtml({
      user_name: item.user_name ?? '—',
      joining_date: undefined,
      role: undefined,
      base_salary: item.base_salary,
      gross_salary: item.gross_salary,
      net_salary: item.net_salary,
      period_start: item.period_start,
      period_end: item.period_end,
      payslip_number: item.payslip_number,
    })
    printPayslip(html)
    toast.success('Payslip opened for print / Save as PDF')
  }, [])

  const columns: Column<PayrollRosterItem>[] = useMemo(
    () => [
      { key: 'user_name', header: 'User', render: (r) => r.user_name || '—' },
      {
        key: 'joining_date',
        header: 'Joining date',
        render: (r) => (r.joining_date ? new Date(r.joining_date).toLocaleDateString() : '—'),
      },
      { key: 'role', header: 'Role', render: (r) => r.role || '—' },
      {
        key: 'salary',
        header: 'Net salary',
        render: (r) =>
          r.net_salary != null
            ? new Intl.NumberFormat(undefined, { style: 'currency', currency: 'USD' }).format(r.net_salary)
            : '—',
      },
      {
        key: 'payment_status',
        header: 'Payment status',
        render: (r) => (
          <span
            className={cn(
              'inline-flex rounded-full px-2 py-0.5 text-xs font-medium',
              r.payment_status === 'PAID' && 'bg-green-500/20 text-green-400',
              r.payment_status === 'PENDING' && 'bg-amber-500/20 text-amber-400',
              r.payment_status === 'PARTIAL' && 'bg-blue-500/20 text-blue-400'
            )}
          >
            {r.payment_status || 'PENDING'}
          </span>
        ),
      },
      {
        key: 'last_payment_date',
        header: 'Last payment',
        render: (r) => (r.last_payment_date ? new Date(r.last_payment_date).toLocaleDateString() : '—'),
      },
      { key: 'updated_by_name', header: 'Updated by', render: (r) => r.updated_by_name || '—' },
      {
        key: 'updated_at',
        header: 'Updated at',
        render: (r) => (r.updated_at ? new Date(r.updated_at).toLocaleString() : '—'),
      },
      {
        key: 'actions',
        header: 'Actions',
        render: (r) => (
          <div className="flex items-center gap-1">
            <Button
              variant="ghost"
              size="icon"
              className="h-8 w-8"
              onClick={() => handleDownloadPayslip(r)}
              title="Download payslip"
            >
              <Download className="h-4 w-4" />
            </Button>
            <Button
              variant="ghost"
              size="icon"
              className="h-8 w-8"
              onClick={() => handleDownloadInvoice(r)}
              title="Download invoice"
            >
              <FileText className="h-4 w-4" />
            </Button>
            <Button variant="ghost" size="icon" className="h-8 w-8" onClick={() => openEditModal(r)} title="Edit">
              <Pencil className="h-4 w-4" />
            </Button>
            <Button
              variant="ghost"
              size="icon"
              className="h-8 w-8 text-destructive"
              onClick={async () => {
                if (!confirm('Remove this user from payroll?')) return
                try {
                  await payrollService.removeFromRoster(r.id)
                  toast.success('Removed from roster')
                  loadRoster()
                } catch (e: unknown) {
                  toast.error((e as { detail?: string })?.detail ?? 'Failed to remove')
                }
              }}
              title="Remove from payroll"
            >
              <Trash2 className="h-4 w-4" />
            </Button>
          </div>
        ),
      },
    ],
    [handleDownloadPayslip, handleDownloadInvoice, openEditModal, loadRoster]
  )

  return (
    <div className="space-y-8">
      <div className="flex flex-col gap-4 sm:flex-row sm:items-center sm:justify-between">
        <h1 className="text-2xl font-bold">Payroll</h1>
        <div className="flex gap-2">
          <Button variant="outline" size="icon" onClick={() => loadAll()} disabled={loading} title="Refresh">
            <RefreshCw className={cn('h-4 w-4', loading ? 'animate-spin' : '')} />
          </Button>
          <Button onClick={openAddModal} className="gap-2">
            <UserPlus className="h-4 w-4" />
            Add user to payroll
          </Button>
        </div>
      </div>
      <p className="text-muted-foreground text-sm">
        Add existing clinic users to payroll, manage joining date, role, salary structure, payment status and dates.
        Track who last updated each entry. Generate payslip or invoice for download (no storage).
      </p>

      {error && <ErrorMessage message={error} />}

      {loading && roster.length === 0 ? (
        <div className="rounded-lg border border-slate-700/50 bg-slate-900/40 p-8">
          <LoadingSpinner text="Loading payroll…" />
        </div>
      ) : (
        <>
          <section>
            <h2 className="mb-4 text-lg font-semibold">Payroll roster</h2>
            <DataTable
              columns={columns}
              data={paginatedRoster}
              keyExtractor={(r) => r.id}
              emptyMessage="No users on payroll. Use “Add user to payroll” to add an existing clinic user."
              pagination={pagination}
              onPageChange={onPageChange}
            />
          </section>

          <section>
            <div className="mb-4 flex items-center justify-between">
              <h2 className="text-lg font-semibold">Payroll runs</h2>
              <Button size="sm" variant="outline" onClick={() => setCreateRunModalOpen(true)}>
                Create payroll run
              </Button>
            </div>
            <div className="rounded-lg border border-slate-700/50 bg-slate-900/40 p-4">
              {payrollRuns.length === 0 ? (
                <p className="text-muted-foreground text-sm">No payroll runs yet. Create one to generate payslips.</p>
              ) : (
                <ul className="space-y-2 text-sm">
                  {payrollRuns.slice(0, 10).map((run) => (
                    <li key={run.id} className="flex items-center justify-between gap-4">
                      <span>
                        {run.payroll_number} · {run.period_start} – {run.period_end} · {run.status}
                      </span>
                      <Button
                        size="sm"
                        variant="outline"
                        onClick={async () => {
                          try {
                            await payrollService.generatePayslips(run.id)
                            toast.success('Payslips generated')
                            loadPayslips()
                            loadRoster()
                          } catch (e: unknown) {
                            toast.error((e as { detail?: string })?.detail ?? 'Failed to generate')
                          }
                        }}
                      >
                        Generate payslips
                      </Button>
                    </li>
                  ))}
                </ul>
              )}
            </div>
          </section>

          <section>
            <div className="mb-4 flex items-center justify-between">
              <h2 className="text-lg font-semibold">Salary structures</h2>
              <Button size="sm" variant="outline" onClick={() => setCreateStructureModalOpen(true)}>
                Create salary structure
              </Button>
            </div>
            <div className="rounded-lg border border-slate-700/50 bg-slate-900/40 p-4">
              {salaryStructures.length === 0 ? (
                <p className="text-muted-foreground text-sm">No salary structures. Create one to assign to users on payroll.</p>
              ) : (
                <ul className="space-y-2 text-sm">
                  {salaryStructures.slice(0, 15).map((s) => (
                    <li key={s.id}>
                      {s.user_name ?? '—'} · Base: {new Intl.NumberFormat(undefined, { style: 'currency', currency: 'USD' }).format(s.base_salary)} · Net: {new Intl.NumberFormat(undefined, { style: 'currency', currency: 'USD' }).format(s.net_salary)}
                    </li>
                  ))}
                </ul>
              )}
            </div>
          </section>

          <section>
            <h2 className="mb-4 text-lg font-semibold">Payslips</h2>
            <div className="rounded-lg border border-slate-700/50 bg-slate-900/40 p-4">
              {payslips.length === 0 ? (
                <p className="text-muted-foreground text-sm">No payslips yet. Generate from a payroll run above.</p>
              ) : (
                <ul className="space-y-2 text-sm">
                  {payslips.slice(0, 15).map((ps) => (
                    <li key={ps.id} className="flex items-center justify-between gap-4">
                      <span>
                        {ps.payslip_number} · {ps.user_name ?? '—'} · {ps.period_start} – {ps.period_end} ·{' '}
                        {new Intl.NumberFormat(undefined, { style: 'currency', currency: 'USD' }).format(ps.net_salary)}
                      </span>
                      <Button size="sm" variant="outline" onClick={() => handleDownloadPayslipFromPayslip(ps)}>
                        <Download className="mr-1 h-3 w-3" />
                        Download
                      </Button>
                    </li>
                  ))}
                </ul>
              )}
            </div>
          </section>
        </>
      )}

      {/* Add user to payroll modal */}
      {addModalOpen && (
        <AddRosterModal
          clinicUsers={clinicUsers}
          salaryStructures={salaryStructures}
          formError={formError}
          formSubmitting={formSubmitting}
          onClose={closeAddModal}
          onSuccess={() => {
            closeAddModal()
            loadRoster()
            loadSalaryStructures()
            toast.success('User added to payroll')
          }}
          setFormError={setFormError}
          setFormSubmitting={setFormSubmitting}
        />
      )}

      {/* Edit roster modal */}
      {editRow && (
        <EditRosterModal
          row={editRow}
          salaryStructures={salaryStructures}
          formError={formError}
          formSubmitting={formSubmitting}
          onClose={closeEditModal}
          onSuccess={() => {
            closeEditModal()
            loadRoster()
            toast.success('Roster entry updated')
          }}
          setFormError={setFormError}
          setFormSubmitting={setFormSubmitting}
        />
      )}

      {/* Create payroll run modal */}
      {createRunModalOpen && (
        <CreatePayrollRunModal
          primaryClinicId={user?.primary_clinic_id ?? null}
          formError={formError}
          formSubmitting={formSubmitting}
          onClose={() => setCreateRunModalOpen(false)}
          onSuccess={() => {
            setCreateRunModalOpen(false)
            loadPayrollRuns()
            toast.success('Payroll run created')
          }}
          setFormError={setFormError}
          setFormSubmitting={setFormSubmitting}
        />
      )}

      {/* Create salary structure modal */}
      {createStructureModalOpen && (
        <CreateSalaryStructureModal
          clinicUsers={clinicUsers}
          formError={formError}
          formSubmitting={formSubmitting}
          onClose={() => setCreateStructureModalOpen(false)}
          onSuccess={() => {
            setCreateStructureModalOpen(false)
            loadSalaryStructures()
            toast.success('Salary structure created')
          }}
          setFormError={setFormError}
          setFormSubmitting={setFormSubmitting}
        />
      )}
    </div>
  )
}

interface AddRosterModalProps {
  clinicUsers: ClinicUserForPayroll[]
  salaryStructures: SalaryStructureBackend[]
  formError: string | null
  formSubmitting: boolean
  onClose: () => void
  onSuccess: () => void
  setFormError: (s: string | null) => void
  setFormSubmitting: (b: boolean) => void
}

function AddRosterModal({
  clinicUsers,
  salaryStructures,
  formError,
  formSubmitting,
  onClose,
  onSuccess,
  setFormError,
  setFormSubmitting,
}: AddRosterModalProps) {
  const [user_id, setUser_id] = useState('')
  const [joining_date, setJoining_date] = useState('')
  const [role, setRole] = useState('')
  const [salary_structure_id, setSalary_structure_id] = useState('')

  const handleSubmit = useCallback(async () => {
    if (!user_id || !joining_date || !role.trim()) {
      setFormError('User, joining date and role are required.')
      return
    }
    setFormSubmitting(true)
    setFormError(null)
    try {
      const payload: AddToRosterRequest = {
        user_id,
        joining_date,
        role: role.trim(),
        salary_structure_id: salary_structure_id || undefined,
      }
      await payrollService.addToRoster(payload)
      onSuccess()
    } catch (e: unknown) {
      setFormError((e as { detail?: string })?.detail ?? (e as Error)?.message ?? 'Failed to add')
    } finally {
      setFormSubmitting(false)
    }
  }, [user_id, joining_date, role, salary_structure_id, onSuccess, setFormError, setFormSubmitting])

  const userStructures = useMemo(
    () => (user_id ? salaryStructures.filter((s) => s.user_id === user_id) : salaryStructures),
    [user_id, salaryStructures]
  )

  return createPortal(
    <div
      className="fixed inset-0 z-[100] flex min-h-screen w-screen items-center justify-center bg-black/70"
      style={{ top: 0, left: 0, right: 0, bottom: 0 }}
      onClick={onClose}
    >
      <div
        className={cn(glassmorphism('dark', false, false), 'max-h-[90vh] w-full max-w-lg overflow-y-auto rounded-xl border border-slate-700/50 bg-slate-900/95 mx-4 shadow-xl')}
        onClick={(e) => e.stopPropagation()}
      >
        <div className="space-y-4 p-6">
          <h2 className="text-lg font-semibold">Add user to payroll</h2>
          {formError && <p className="text-sm text-destructive">{formError}</p>}
          <div className="grid gap-2">
            <label className="text-sm font-medium text-muted-foreground">User *</label>
            <select
              className="flex h-10 w-full rounded-md border border-input bg-background px-3 py-2 text-sm"
              value={user_id}
              onChange={(e) => setUser_id(e.target.value)}
            >
              <option value="">Select user</option>
              {clinicUsers.map((u) => (
                <option key={u.id} value={u.id}>
                  {[u.first_name, u.last_name].filter(Boolean).join(' ') || u.username || u.email || u.id}
                </option>
              ))}
            </select>
          </div>
          <div className="grid gap-2">
            <label className="text-sm font-medium text-muted-foreground">Joining date *</label>
            <Input
              type="date"
              value={joining_date}
              onChange={(e) => setJoining_date(e.target.value)}
            />
          </div>
          <div className="grid gap-2">
            <label className="text-sm font-medium text-muted-foreground">Role *</label>
            <select
              className="flex h-10 w-full rounded-md border border-input bg-background px-3 py-2 text-sm"
              value={role}
              onChange={(e) => setRole(e.target.value)}
            >
              <option value="">Select role</option>
              {ROLES.map((r) => (
                <option key={r} value={r}>
                  {r}
                </option>
              ))}
            </select>
          </div>
          <div className="grid gap-2">
            <label className="text-sm font-medium text-muted-foreground">Salary structure (optional)</label>
            <select
              className="flex h-10 w-full rounded-md border border-input bg-background px-3 py-2 text-sm"
              value={salary_structure_id}
              onChange={(e) => setSalary_structure_id(e.target.value)}
            >
              <option value="">None</option>
              {userStructures.map((s) => (
                <option key={s.id} value={s.id}>
                  {s.user_name ?? s.id} · Net: {new Intl.NumberFormat(undefined, { style: 'currency', currency: 'USD' }).format(s.net_salary)}
                </option>
              ))}
            </select>
          </div>
          <div className="flex justify-end gap-2 pt-2">
            <Button variant="outline" onClick={onClose} disabled={formSubmitting}>
              Cancel
            </Button>
            <Button onClick={handleSubmit} disabled={formSubmitting}>
              {formSubmitting ? <Loader2 className="h-4 w-4 animate-spin" /> : 'Add to payroll'}
            </Button>
          </div>
        </div>
      </div>
    </div>,
    document.body
  )
}

interface EditRosterModalProps {
  row: PayrollRosterItem
  salaryStructures: SalaryStructureBackend[]
  formError: string | null
  formSubmitting: boolean
  onClose: () => void
  onSuccess: () => void
  setFormError: (s: string | null) => void
  setFormSubmitting: (b: boolean) => void
}

function EditRosterModal({
  row,
  salaryStructures,
  formError,
  formSubmitting,
  onClose,
  onSuccess,
  setFormError,
  setFormSubmitting,
}: EditRosterModalProps) {
  const [joining_date, setJoining_date] = useState(row.joining_date)
  const [role, setRole] = useState(row.role)
  const [salary_structure_id, setSalary_structure_id] = useState(row.salary_structure_id ?? '')
  const [payment_status, setPayment_status] = useState<'PENDING' | 'PAID' | 'PARTIAL'>(row.payment_status as 'PENDING' | 'PAID' | 'PARTIAL')
  const [last_payment_date, setLast_payment_date] = useState(row.last_payment_date ?? '')

  const handleSubmit = useCallback(async () => {
    setFormSubmitting(true)
    setFormError(null)
    try {
      const payload: UpdateRosterRequest = {
        joining_date,
        role,
        salary_structure_id: salary_structure_id || null,
        payment_status,
        last_payment_date: last_payment_date || null,
      }
      await payrollService.updateRoster(row.id, payload)
      onSuccess()
    } catch (e: unknown) {
      setFormError((e as { detail?: string })?.detail ?? (e as Error)?.message ?? 'Failed to update')
    } finally {
      setFormSubmitting(false)
    }
  }, [row.id, joining_date, role, salary_structure_id, payment_status, last_payment_date, onSuccess, setFormError, setFormSubmitting])

  const userStructures = useMemo(
    () => (row.user_id ? salaryStructures.filter((s) => s.user_id === row.user_id) : salaryStructures),
    [row.user_id, salaryStructures]
  )

  return createPortal(
    <div
      className="fixed inset-0 z-[100] flex min-h-screen w-screen items-center justify-center bg-black/70"
      style={{ top: 0, left: 0, right: 0, bottom: 0 }}
      onClick={onClose}
    >
      <div
        className={cn(glassmorphism('dark', false, false), 'max-h-[90vh] w-full max-w-lg overflow-y-auto rounded-xl border border-slate-700/50 bg-slate-900/95 mx-4 shadow-xl')}
        onClick={(e) => e.stopPropagation()}
      >
        <div className="space-y-4 p-6">
          <h2 className="text-lg font-semibold">Edit payroll entry · {row.user_name}</h2>
          {formError && <p className="text-sm text-destructive">{formError}</p>}
          <div className="grid gap-2">
            <label className="text-sm font-medium text-muted-foreground">Joining date</label>
            <Input type="date" value={joining_date} onChange={(e) => setJoining_date(e.target.value)} />
          </div>
          <div className="grid gap-2">
            <label className="text-sm font-medium text-muted-foreground">Role</label>
            <select
              className="flex h-10 w-full rounded-md border border-input bg-background px-3 py-2 text-sm"
              value={role}
              onChange={(e) => setRole(e.target.value)}
            >
              {ROLES.map((r) => (
                <option key={r} value={r}>
                  {r}
                </option>
              ))}
            </select>
          </div>
          <div className="grid gap-2">
            <label className="text-sm font-medium text-muted-foreground">Salary structure</label>
            <select
              className="flex h-10 w-full rounded-md border border-input bg-background px-3 py-2 text-sm"
              value={salary_structure_id}
              onChange={(e) => setSalary_structure_id(e.target.value)}
            >
              <option value="">None</option>
              {userStructures.map((s) => (
                <option key={s.id} value={s.id}>
                  {s.user_name ?? s.id} · Net: {new Intl.NumberFormat(undefined, { style: 'currency', currency: 'USD' }).format(s.net_salary)}
                </option>
              ))}
            </select>
          </div>
          <div className="grid gap-2">
            <label className="text-sm font-medium text-muted-foreground">Payment status</label>
            <select
              className="flex h-10 w-full rounded-md border border-input bg-background px-3 py-2 text-sm"
              value={payment_status}
              onChange={(e) => setPayment_status(e.target.value as 'PENDING' | 'PAID' | 'PARTIAL')}
            >
              <option value="PENDING">PENDING</option>
              <option value="PAID">PAID</option>
              <option value="PARTIAL">PARTIAL</option>
            </select>
          </div>
          <div className="grid gap-2">
            <label className="text-sm font-medium text-muted-foreground">Last payment date</label>
            <Input
              type="date"
              value={last_payment_date}
              onChange={(e) => setLast_payment_date(e.target.value)}
            />
          </div>
          <div className="flex justify-end gap-2 pt-2">
            <Button variant="outline" onClick={onClose} disabled={formSubmitting}>
              Cancel
            </Button>
            <Button onClick={handleSubmit} disabled={formSubmitting}>
              {formSubmitting ? <Loader2 className="h-4 w-4 animate-spin" /> : 'Save'}
            </Button>
          </div>
        </div>
      </div>
    </div>,
    document.body
  )
}

interface CreatePayrollRunModalProps {
  primaryClinicId: string | null
  formError: string | null
  formSubmitting: boolean
  onClose: () => void
  onSuccess: () => void
  setFormError: (s: string | null) => void
  setFormSubmitting: (b: boolean) => void
}

function CreatePayrollRunModal({
  primaryClinicId,
  formError,
  formSubmitting,
  onClose,
  onSuccess,
  setFormError,
  setFormSubmitting,
}: CreatePayrollRunModalProps) {
  const [period_start, setPeriod_start] = useState('')
  const [period_end, setPeriod_end] = useState('')
  const [pay_date, setPay_date] = useState('')

  const handleSubmit = useCallback(async () => {
    if (!period_start || !period_end) {
      setFormError('Period start and end are required.')
      return
    }
    setFormSubmitting(true)
    setFormError(null)
    try {
      await payrollService.createPayrollRun({
        period_start,
        period_end,
        pay_date: pay_date || undefined,
        clinic_id: primaryClinicId ?? undefined,
      })
      onSuccess()
    } catch (e: unknown) {
      setFormError((e as { detail?: string })?.detail ?? (e as Error)?.message ?? 'Failed to create')
    } finally {
      setFormSubmitting(false)
    }
  }, [period_start, period_end, pay_date, primaryClinicId, onSuccess, setFormError, setFormSubmitting])

  return createPortal(
    <div
      className="fixed inset-0 z-[100] flex min-h-screen w-screen items-center justify-center bg-black/70"
      style={{ top: 0, left: 0, right: 0, bottom: 0 }}
      onClick={onClose}
    >
      <div
        className={cn(glassmorphism('dark', false, false), 'max-h-[90vh] w-full max-w-lg overflow-y-auto rounded-xl border border-slate-700/50 bg-slate-900/95 mx-4 shadow-xl')}
        onClick={(e) => e.stopPropagation()}
      >
        <div className="space-y-4 p-6">
          <h2 className="text-lg font-semibold">Create payroll run</h2>
          {formError && <p className="text-sm text-destructive">{formError}</p>}
          <div className="grid gap-2">
            <label className="text-sm font-medium text-muted-foreground">Period start *</label>
            <Input type="date" value={period_start} onChange={(e) => setPeriod_start(e.target.value)} />
          </div>
          <div className="grid gap-2">
            <label className="text-sm font-medium text-muted-foreground">Period end *</label>
            <Input type="date" value={period_end} onChange={(e) => setPeriod_end(e.target.value)} />
          </div>
          <div className="grid gap-2">
            <label className="text-sm font-medium text-muted-foreground">Pay date (optional)</label>
            <Input type="date" value={pay_date} onChange={(e) => setPay_date(e.target.value)} />
          </div>
          <div className="flex justify-end gap-2 pt-2">
            <Button variant="outline" onClick={onClose} disabled={formSubmitting}>Cancel</Button>
            <Button onClick={handleSubmit} disabled={formSubmitting}>
              {formSubmitting ? <Loader2 className="h-4 w-4 animate-spin" /> : 'Create'}
            </Button>
          </div>
        </div>
      </div>
    </div>,
    document.body
  )
}

interface CreateSalaryStructureModalProps {
  clinicUsers: ClinicUserForPayroll[]
  formError: string | null
  formSubmitting: boolean
  onClose: () => void
  onSuccess: () => void
  setFormError: (s: string | null) => void
  setFormSubmitting: (b: boolean) => void
}

function CreateSalaryStructureModal({
  clinicUsers,
  formError,
  formSubmitting,
  onClose,
  onSuccess,
  setFormError,
  setFormSubmitting,
}: CreateSalaryStructureModalProps) {
  const [user_id, setUser_id] = useState('')
  const [base_salary, setBase_salary] = useState('')
  const [housing_allowance, setHousing_allowance] = useState('0')
  const [transport_allowance, setTransport_allowance] = useState('0')
  const [medical_allowance, setMedical_allowance] = useState('0')
  const [other_allowances, setOther_allowances] = useState('0')
  const [tax_deduction, setTax_deduction] = useState('0')
  const [insurance_deduction, setInsurance_deduction] = useState('0')
  const [other_deductions, setOther_deductions] = useState('0')

  const handleSubmit = useCallback(async () => {
    if (!user_id || !base_salary.trim()) {
      setFormError('User and base salary are required.')
      return
    }
    const base = Number(base_salary)
    if (Number.isNaN(base) || base < 0) {
      setFormError('Base salary must be a non-negative number.')
      return
    }
    setFormSubmitting(true)
    setFormError(null)
    try {
      await payrollService.createSalaryStructure({
        user_id,
        base_salary: base,
        housing_allowance: Number(housing_allowance) || 0,
        transport_allowance: Number(transport_allowance) || 0,
        medical_allowance: Number(medical_allowance) || 0,
        other_allowances: Number(other_allowances) || 0,
        tax_deduction: Number(tax_deduction) || 0,
        insurance_deduction: Number(insurance_deduction) || 0,
        other_deductions: Number(other_deductions) || 0,
      })
      onSuccess()
    } catch (e: unknown) {
      setFormError((e as { detail?: string })?.detail ?? (e as Error)?.message ?? 'Failed to create')
    } finally {
      setFormSubmitting(false)
    }
  }, [user_id, base_salary, housing_allowance, transport_allowance, medical_allowance, other_allowances, tax_deduction, insurance_deduction, other_deductions, onSuccess, setFormError, setFormSubmitting])

  return createPortal(
    <div
      className="fixed inset-0 z-[100] flex min-h-screen w-screen items-center justify-center bg-black/70"
      style={{ top: 0, left: 0, right: 0, bottom: 0 }}
      onClick={onClose}
    >
      <div
        className={cn(glassmorphism('dark', false, false), 'max-h-[90vh] w-full max-w-lg overflow-y-auto rounded-xl border border-slate-700/50 bg-slate-900/95 mx-4 shadow-xl')}
        onClick={(e) => e.stopPropagation()}
      >
        <div className="space-y-4 p-6">
          <h2 className="text-lg font-semibold">Create salary structure</h2>
          {formError && <p className="text-sm text-destructive">{formError}</p>}
          <div className="grid gap-2">
            <label className="text-sm font-medium text-muted-foreground">User *</label>
            <select
              className="flex h-10 w-full rounded-md border border-input bg-background px-3 py-2 text-sm"
              value={user_id}
              onChange={(e) => setUser_id(e.target.value)}
            >
              <option value="">Select user</option>
              {clinicUsers.map((u) => (
                <option key={u.id} value={u.id}>
                  {[u.first_name, u.last_name].filter(Boolean).join(' ') || u.username || u.email || u.id}
                </option>
              ))}
            </select>
          </div>
          <div className="grid gap-2">
            <label className="text-sm font-medium text-muted-foreground">Base salary *</label>
            <Input
              type="number"
              min={0}
              step={0.01}
              value={base_salary}
              onChange={(e) => setBase_salary(e.target.value)}
              placeholder="0"
            />
          </div>
          <div className="grid grid-cols-2 gap-4">
            <div className="grid gap-2">
              <label className="text-sm font-medium text-muted-foreground">Housing allowance</label>
              <Input type="number" min={0} step={0.01} value={housing_allowance} onChange={(e) => setHousing_allowance(e.target.value)} />
            </div>
            <div className="grid gap-2">
              <label className="text-sm font-medium text-muted-foreground">Transport allowance</label>
              <Input type="number" min={0} step={0.01} value={transport_allowance} onChange={(e) => setTransport_allowance(e.target.value)} />
            </div>
          </div>
          <div className="grid grid-cols-2 gap-4">
            <div className="grid gap-2">
              <label className="text-sm font-medium text-muted-foreground">Medical allowance</label>
              <Input type="number" min={0} step={0.01} value={medical_allowance} onChange={(e) => setMedical_allowance(e.target.value)} />
            </div>
            <div className="grid gap-2">
              <label className="text-sm font-medium text-muted-foreground">Other allowances</label>
              <Input type="number" min={0} step={0.01} value={other_allowances} onChange={(e) => setOther_allowances(e.target.value)} />
            </div>
          </div>
          <div className="grid grid-cols-2 gap-4">
            <div className="grid gap-2">
              <label className="text-sm font-medium text-muted-foreground">Tax deduction</label>
              <Input type="number" min={0} step={0.01} value={tax_deduction} onChange={(e) => setTax_deduction(e.target.value)} />
            </div>
            <div className="grid gap-2">
              <label className="text-sm font-medium text-muted-foreground">Insurance deduction</label>
              <Input type="number" min={0} step={0.01} value={insurance_deduction} onChange={(e) => setInsurance_deduction(e.target.value)} />
            </div>
          </div>
          <div className="grid gap-2">
            <label className="text-sm font-medium text-muted-foreground">Other deductions</label>
            <Input type="number" min={0} step={0.01} value={other_deductions} onChange={(e) => setOther_deductions(e.target.value)} />
          </div>
          <div className="flex justify-end gap-2 pt-2">
            <Button variant="outline" onClick={onClose} disabled={formSubmitting}>Cancel</Button>
            <Button onClick={handleSubmit} disabled={formSubmitting}>
              {formSubmitting ? <Loader2 className="h-4 w-4 animate-spin" /> : 'Create'}
            </Button>
          </div>
        </div>
      </div>
    </div>,
    document.body
  )
}
