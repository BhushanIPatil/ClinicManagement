/**
 * Clinic Settings Page (Clinic Admin only)
 *
 * Access to features: table with users (employees) as rows and features
 * (Finance, Patients, Work Queue, Payroll) as columns.
 * Checkbox = this user can access this feature.
 */

import { useCallback, useEffect, useState, useMemo } from 'react'
import { toast } from 'sonner'
import { Settings, Save, RefreshCw } from 'lucide-react'
import { clinicAdminService } from '@/services/clinic-admin.service'
import type { ClinicSettingsUserItem, UserFeatures } from '@/services/clinic-admin.service'
import { Button } from '@/components/ui/button'
import { glassmorphism } from '@/lib/glassmorphism'
import { cn } from '@/lib/utils'
import { LoadingSpinner, ErrorMessage, DataTable, Column, PaginationState } from '@/components/common'

const FEATURES = [
  { key: 'FINANCE', label: 'Finance' },
  { key: 'PATIENTS', label: 'Patients' },
  { key: 'WORK_QUEUE', label: 'Work Queue' },
  { key: 'PAYROLL', label: 'Payroll' },
] as const

const defaultFeatures = (): UserFeatures => ({
  FINANCE: true,
  PATIENTS: true,
  WORK_QUEUE: true,
  PAYROLL: true,
})

const DEFAULT_PAGE_SIZE = 10

export default function SettingsPage() {
  const [users, setUsers] = useState<ClinicSettingsUserItem[]>([])
  const [loading, setLoading] = useState(true)
  const [saving, setSaving] = useState(false)
  const [error, setError] = useState<string | null>(null)
  const [saveMessage, setSaveMessage] = useState<string | null>(null)
  const [page, setPage] = useState(1)
  const [pageSize, setPageSize] = useState(DEFAULT_PAGE_SIZE)

  const load = useCallback(async () => {
    setLoading(true)
    setError(null)
    try {
      const res = await clinicAdminService.getClinicSettings()
      setUsers(
        Array.isArray(res.users)
          ? res.users.map((u) => ({
              ...u,
              features: {
                ...defaultFeatures(),
                ...(u.features || {}),
              },
            }))
          : []
      )
    } catch (err: unknown) {
      const msg =
        err && typeof err === 'object' && 'detail' in err
          ? String((err as { detail: unknown }).detail)
          : err instanceof Error ? err.message : 'Failed to load settings'
      setError(msg)
      toast.error(msg)
      setUsers([])
    } finally {
      setLoading(false)
    }
  }, [])

  useEffect(() => {
    load()
  }, [load])

  const setChecked = useCallback((userId: string, featureKey: string, value: boolean) => {
    setUsers((prev) =>
      prev.map((u) =>
        u.id === userId
          ? { ...u, features: { ...u.features, [featureKey]: value } }
          : u
      )
    )
    setSaveMessage(null)
  }, [])

  const handleSave = useCallback(async () => {
    setSaving(true)
    setError(null)
    setSaveMessage(null)
    try {
      await clinicAdminService.putClinicSettings({
        users: users.map((u) => ({ user_id: u.id, features: u.features })),
      })
      setSaveMessage('Settings saved.')
      toast.success('Settings saved.')
    } catch (err: unknown) {
      const msg =
        err && typeof err === 'object' && 'detail' in err
          ? String((err as { detail: unknown }).detail)
          : err instanceof Error ? err.message : 'Failed to save settings'
      setError(msg)
      toast.error(msg)
    } finally {
      setSaving(false)
    }
  }, [users])

  const pagination: PaginationState = useMemo(
    () => ({ page, pageSize, total: users.length }),
    [page, pageSize, users.length]
  )
  const paginatedUsers = useMemo(
    () => users.slice((page - 1) * pageSize, page * pageSize),
    [users, page, pageSize]
  )
  const onPageChange = useCallback((p: number, ps: number) => {
    setPage(p)
    setPageSize(ps)
  }, [])

  const columns: Column<ClinicSettingsUserItem>[] = useMemo(
    () => [
      {
        key: 'user',
        header: 'User',
        render: (u) => (
          <div>
            <div className="font-medium text-slate-200">
              {(u.first_name || u.last_name) ? [u.first_name, u.last_name].filter(Boolean).join(' ') : u.username || u.email || u.id}
            </div>
            {u.email && <div className="text-xs text-slate-500">{u.email}</div>}
          </div>
        ),
      },
      {
        key: 'role',
        header: 'Role',
        render: (u) => <span className="text-slate-400">{u.clinic_role || '–'}</span>,
      },
      ...FEATURES.map((f) => ({
        key: f.key,
        header: f.label,
        className: 'text-center' as const,
        render: (u: ClinicSettingsUserItem) => (
          <div className="flex justify-center">
            <input
              type="checkbox"
              checked={Boolean(u.features?.[f.key])}
              onChange={(e) => setChecked(u.id, f.key, e.target.checked)}
              className="h-4 w-4 rounded border-slate-600 bg-slate-800"
              aria-label={`${u.username || u.id} – ${f.label}`}
            />
          </div>
        ),
      })),
    ],
    [setChecked]
  )

  if (loading && users.length === 0) {
    return (
      <div className="space-y-6">
        <h1 className="text-2xl font-bold">Clinic Settings</h1>
        <div className={cn(glassmorphism('dark', false, false), 'rounded-lg p-8')}>
          <LoadingSpinner text="Loading settings..." />
        </div>
      </div>
    )
  }

  return (
    <div className="space-y-6">
      <div className="flex flex-col gap-4 sm:flex-row sm:items-center sm:justify-between">
        <h1 className="text-2xl font-bold flex items-center gap-2">
          <Settings className="h-7 w-7" />
          Clinic Settings
        </h1>
        <div className="flex gap-2">
          <Button variant="outline" size="icon" onClick={load} disabled={loading} title="Refresh">
            <RefreshCw className={cn('h-4 w-4', loading && 'animate-spin')} />
          </Button>
          <Button onClick={handleSave} disabled={saving}>
            <Save className="mr-2 h-4 w-4" />
            {saving ? 'Saving...' : 'Save'}
          </Button>
        </div>
      </div>

      <p className="text-muted-foreground">
        Control which users (employees) can access each feature. Only checked features are allowed for that user.
      </p>

      {error && <ErrorMessage message={error} />}
      {saveMessage && (
        <div className="rounded-md bg-green-500/10 px-3 py-2 text-sm text-green-500">
          {saveMessage}
        </div>
      )}

      <div className="space-y-2">
        <h2 className="text-lg font-semibold text-slate-200">Access to features</h2>
        <DataTable
          columns={columns}
          data={paginatedUsers}
          keyExtractor={(u) => u.id}
          emptyMessage="No users in this clinic. Add users from the Users page first."
          pagination={pagination}
          onPageChange={onPageChange}
        />
      </div>
    </div>
  )
}
