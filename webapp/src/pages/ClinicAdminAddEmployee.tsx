import { useState } from 'react'
import { useNavigate } from 'react-router-dom'
import { toast } from 'sonner'
import { clinicAdminService } from '@/services/clinic-admin.service'
import type { ClinicEmployeeRole, AddAsType } from '@/services/clinic-admin.service'
import { tokenStorage } from '@/lib/token-storage'
import { Button } from '@/components/ui/button'
import { Input } from '@/components/ui/input'

const ROLES: { value: ClinicEmployeeRole; label: string }[] = [
  { value: 'DOCTOR', label: 'Doctor' },
  { value: 'NURSE', label: 'Nurse' },
  { value: 'HR_OPERATIONS', label: 'HR Operations' },
  { value: 'RECEPTIONIST', label: 'Receptionist' },
]

const ADD_AS_OPTIONS: { value: AddAsType; label: string; description: string }[] = [
  { value: 'user', label: 'User', description: 'Store in users table only (access by role)' },
  { value: 'employee', label: 'Employee', description: 'Store in users + employees (access + HR/payroll)' },
]

export default function ClinicAdminAddEmployee() {
  const navigate = useNavigate()
  const [loading, setLoading] = useState(false)
  const [error, setError] = useState<string | null>(null)
  const [form, setForm] = useState({
    email: '',
    username: '',
    password: '',
    first_name: '',
    last_name: '',
    phone: '',
    role: 'NURSE' as ClinicEmployeeRole,
    add_as: 'employee' as AddAsType,
  })

  const currentUser = tokenStorage.getUser()
  const primaryClinicId = currentUser?.primary_clinic_id ?? null
  const primaryClinicName = currentUser?.primary_clinic_name ?? null

  async function handleSubmit(e: React.FormEvent) {
    e.preventDefault()
    setError(null)
    if (!primaryClinicId) {
      const msg = "Your account doesn't have a clinic assigned. Contact an administrator."
      setError(msg)
      toast.warning(msg)
      return
    }
    setLoading(true)
    try {
      await clinicAdminService.addClinicEmployeeCurrentUser({
        email: form.email,
        username: form.username,
        password: form.password,
        first_name: form.first_name,
        last_name: form.last_name,
        phone: form.phone || undefined,
        role: form.role,
        add_as: form.add_as,
      })
      toast.success('User added.')
      navigate('/users', { replace: true })
    } catch (err: any) {
      const msg = err?.detail || err?.message || 'Add employee failed'
      setError(msg)
      toast.error(msg)
    } finally {
      setLoading(false)
    }
  }

  return (
    <div className="max-w-2xl space-y-6">
      <h1 className="text-2xl font-bold">Add User</h1>
      <p className="text-muted-foreground">
        Add a <strong>User</strong> (users table only) or <strong>Employee</strong> (users + employees). Both get access by role (Doctor, Nurse, HR Operations, Receptionist). Employees are also tracked for HR/payroll.
        {primaryClinicName && (
          <span className="ml-1 block text-sm">Clinic: {primaryClinicName}</span>
        )}
      </p>
      {!primaryClinicId && (
        <p className="rounded-md bg-amber-500/10 px-3 py-2 text-sm text-amber-600 dark:text-amber-400">
          Your account does not have a clinic assigned. You need CLINIC_ADMIN with a clinic to add employees. Contact an administrator.
        </p>
      )}
      <form onSubmit={handleSubmit} className="space-y-6 rounded-lg border border-white/10 bg-white/5 p-6">
        <div className="grid gap-4 sm:grid-cols-2">
          <div>
            <label className="text-sm text-muted-foreground">Email *</label>
            <Input
              type="email"
              value={form.email}
              onChange={(e) => setForm((f) => ({ ...f, email: e.target.value }))}
              required
              className="mt-1"
            />
          </div>
          <div>
            <label className="text-sm text-muted-foreground">Username *</label>
            <Input
              value={form.username}
              onChange={(e) => setForm((f) => ({ ...f, username: e.target.value }))}
              required
              className="mt-1"
            />
          </div>
        </div>
        <div>
          <label className="text-sm text-muted-foreground">Password *</label>
          <Input
            type="password"
            value={form.password}
            onChange={(e) => setForm((f) => ({ ...f, password: e.target.value }))}
            required
            minLength={8}
            className="mt-1"
          />
        </div>
        <div className="grid gap-4 sm:grid-cols-2">
          <div>
            <label className="text-sm text-muted-foreground">First name *</label>
            <Input
              value={form.first_name}
              onChange={(e) => setForm((f) => ({ ...f, first_name: e.target.value }))}
              required
              className="mt-1"
            />
          </div>
          <div>
            <label className="text-sm text-muted-foreground">Last name *</label>
            <Input
              value={form.last_name}
              onChange={(e) => setForm((f) => ({ ...f, last_name: e.target.value }))}
              required
              className="mt-1"
            />
          </div>
        </div>
        <div>
          <label className="text-sm text-muted-foreground">Phone</label>
          <Input
            value={form.phone}
            onChange={(e) => setForm((f) => ({ ...f, phone: e.target.value }))}
            className="mt-1"
          />
        </div>
        <div>
          <label className="text-sm text-muted-foreground">Add as *</label>
          <div className="mt-2 flex flex-col gap-2 sm:flex-row sm:gap-4">
            {ADD_AS_OPTIONS.map((opt) => (
              <label
                key={opt.value}
                className="flex cursor-pointer items-start gap-2 rounded-lg border border-input bg-background px-3 py-2 has-[:checked]:ring-2 has-[:checked]:ring-primary"
              >
                <input
                  type="radio"
                  name="add_as"
                  value={opt.value}
                  checked={form.add_as === opt.value}
                  onChange={() => setForm((f) => ({ ...f, add_as: opt.value }))}
                  className="mt-1"
                />
                <div>
                  <span className="font-medium">{opt.label}</span>
                  <p className="text-xs text-muted-foreground">{opt.description}</p>
                </div>
              </label>
            ))}
          </div>
        </div>
        <div>
          <label className="text-sm text-muted-foreground">Role *</label>
          <select
            value={form.role}
            onChange={(e) => setForm((f) => ({ ...f, role: e.target.value as ClinicEmployeeRole }))}
            required
            className="mt-1 w-full rounded-md border border-input bg-background px-3 py-2 text-sm"
          >
            {ROLES.map((r) => (
              <option key={r.value} value={r.value}>
                {r.label}
              </option>
            ))}
          </select>
        </div>
        {error && (
          <p className="rounded-md bg-destructive/10 px-3 py-2 text-sm text-destructive">{error}</p>
        )}
        <div className="flex gap-2">
          <Button type="submit" disabled={loading || !primaryClinicId}>
            {loading ? 'Adding…' : 'Add User'}
          </Button>
          <Button type="button" variant="outline" onClick={() => navigate(-1)}>
            Cancel
          </Button>
        </div>
      </form>
    </div>
  )
}
