import { useState } from 'react'
import { useNavigate } from 'react-router-dom'
import { superAdminService } from '@/services/super-admin.service'
import { Button } from '@/components/ui/button'
import { Input } from '@/components/ui/input'

export default function SuperAdminOnboard() {
  const navigate = useNavigate()
  const [loading, setLoading] = useState(false)
  const [error, setError] = useState<string | null>(null)
  const [form, setForm] = useState({
    clinicName: '',
    clinicCode: '',
    clinicAddress: '',
    clinicPhone: '',
    userEmail: '',
    userUsername: '',
    userPassword: '',
    userFirstName: '',
    userLastName: '',
    userPhone: '',
  })

  async function handleSubmit(e: React.FormEvent) {
    e.preventDefault()
    setError(null)
    setLoading(true)
    try {
      await superAdminService.onboardClinic({
        clinic: {
          name: form.clinicName,
          code: form.clinicCode,
          address: form.clinicAddress || undefined,
          phone: form.clinicPhone || undefined,
        },
        user: {
          email: form.userEmail,
          username: form.userUsername,
          password: form.userPassword,
          first_name: form.userFirstName,
          last_name: form.userLastName,
          phone: form.userPhone || undefined,
        },
      })
      navigate('/super-admin/clinics', { replace: true })
    } catch (err: any) {
      setError(err?.detail || err?.message || 'Onboard failed')
    } finally {
      setLoading(false)
    }
  }

  return (
    <div className="max-w-2xl space-y-6">
      <h1 className="text-2xl font-bold">Onboard Clinic with User</h1>
      <p className="text-muted-foreground">
        Creates clinic, user, and links the user to the clinic as <strong>Clinic Admin</strong>.
      </p>
      <form onSubmit={handleSubmit} className="space-y-6 rounded-lg bg-white/5 border border-white/10 p-6">
        <div className="space-y-4">
          <h2 className="text-lg font-semibold">Clinic</h2>
          <div className="grid gap-4 sm:grid-cols-2">
            <div>
              <label className="text-sm text-muted-foreground">Name *</label>
              <Input
                value={form.clinicName}
                onChange={(e) => setForm((f) => ({ ...f, clinicName: e.target.value }))}
                required
                className="mt-1"
              />
            </div>
            <div>
              <label className="text-sm text-muted-foreground">Code *</label>
              <Input
                value={form.clinicCode}
                onChange={(e) => setForm((f) => ({ ...f, clinicCode: e.target.value.toUpperCase() }))}
                required
                placeholder="e.g. CLINIC-A"
                className="mt-1"
              />
            </div>
            <div className="sm:col-span-2">
              <label className="text-sm text-muted-foreground">Address</label>
              <Input
                value={form.clinicAddress}
                onChange={(e) => setForm((f) => ({ ...f, clinicAddress: e.target.value }))}
                className="mt-1"
              />
            </div>
            <div>
              <label className="text-sm text-muted-foreground">Phone</label>
              <Input
                value={form.clinicPhone}
                onChange={(e) => setForm((f) => ({ ...f, clinicPhone: e.target.value }))}
                className="mt-1"
              />
            </div>
          </div>
        </div>
        <div className="space-y-4">
          <h2 className="text-lg font-semibold">Clinic Admin User</h2>
          <div className="grid gap-4 sm:grid-cols-2">
            <div>
              <label className="text-sm text-muted-foreground">Email *</label>
              <Input
                type="email"
                value={form.userEmail}
                onChange={(e) => setForm((f) => ({ ...f, userEmail: e.target.value }))}
                required
                className="mt-1"
              />
            </div>
            <div>
              <label className="text-sm text-muted-foreground">Username *</label>
              <Input
                value={form.userUsername}
                onChange={(e) => setForm((f) => ({ ...f, userUsername: e.target.value }))}
                required
                className="mt-1"
              />
            </div>
            <div>
              <label className="text-sm text-muted-foreground">Password *</label>
              <Input
                type="password"
                value={form.userPassword}
                onChange={(e) => setForm((f) => ({ ...f, userPassword: e.target.value }))}
                required
                className="mt-1"
              />
            </div>
            <div>
              <label className="text-sm text-muted-foreground">First name *</label>
              <Input
                value={form.userFirstName}
                onChange={(e) => setForm((f) => ({ ...f, userFirstName: e.target.value }))}
                required
                className="mt-1"
              />
            </div>
            <div>
              <label className="text-sm text-muted-foreground">Last name *</label>
              <Input
                value={form.userLastName}
                onChange={(e) => setForm((f) => ({ ...f, userLastName: e.target.value }))}
                required
                className="mt-1"
              />
            </div>
            <div>
              <label className="text-sm text-muted-foreground">Phone</label>
              <Input
                value={form.userPhone}
                onChange={(e) => setForm((f) => ({ ...f, userPhone: e.target.value }))}
                className="mt-1"
              />
            </div>
          </div>
        </div>
        {error && <div className="text-sm text-destructive">{error}</div>}
        <Button type="submit" disabled={loading}>
          {loading ? 'Creating...' : 'Onboard Clinic & User'}
        </Button>
      </form>
    </div>
  )
}
