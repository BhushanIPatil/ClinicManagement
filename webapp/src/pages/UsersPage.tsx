import { useCallback, useEffect, useState } from 'react'
import { Link } from 'react-router-dom'
import { UserPlus, RefreshCw } from 'lucide-react'
import { clinicAdminService } from '@/services/clinic-admin.service'
import type { ClinicEmployeeListItem } from '@/services/clinic-admin.service'
import { Button } from '@/components/ui/button'

export default function UsersPage() {
  const [items, setItems] = useState<ClinicEmployeeListItem[]>([])
  const [total, setTotal] = useState(0)
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState<string | null>(null)

  const load = useCallback(async () => {
    setLoading(true)
    setError(null)
    try {
      const res = await clinicAdminService.listClinicEmployeesCurrentUser({ skip: 0, limit: 100 })
      setItems(res.items)
      setTotal(res.total)
    } catch (err: unknown) {
      const msg = err && typeof err === 'object' && 'detail' in err
        ? String((err as { detail: unknown }).detail)
        : err instanceof Error ? err.message : 'Failed to load users'
      setError(msg)
      setItems([])
      setTotal(0)
    } finally {
      setLoading(false)
    }
  }, [])

  useEffect(() => {
    load()
  }, [load])

  return (
    <div className="space-y-6">
      <div className="flex flex-col gap-4 sm:flex-row sm:items-center sm:justify-between">
        <h1 className="text-2xl font-bold">Users</h1>
        <div className="flex gap-2">
          <Button variant="outline" size="icon" onClick={() => load()} disabled={loading} title="Refresh list">
            <RefreshCw className={`h-4 w-4 ${loading ? 'animate-spin' : ''}`} />
          </Button>
          <Button asChild>
            <Link to="/users/add">
              <UserPlus className="mr-2 h-4 w-4" />
              Add User
            </Link>
          </Button>
        </div>
      </div>
      <p className="text-muted-foreground">
        Users and employees in your clinic. Both have access by role; employees are also in the employees table for HR/payroll.
      </p>

      {error && (
        <div className="rounded-md bg-destructive/10 px-3 py-2 text-sm text-destructive">
          {error}
        </div>
      )}

      {loading ? (
        <p className="text-muted-foreground">Loading…</p>
      ) : items.length === 0 ? (
        <div className="rounded-lg border border-white/10 bg-white/5 p-8 text-center text-muted-foreground">
          No users yet. Use <strong>Add User</strong> to add the first user to your clinic.
        </div>
      ) : (
        <div className="overflow-hidden rounded-lg border border-white/10">
          <table className="w-full text-left text-sm">
            <thead className="border-b border-white/10 bg-white/5">
              <tr>
                <th className="px-4 py-3 font-medium">Name</th>
                <th className="px-4 py-3 font-medium">Type</th>
                <th className="px-4 py-3 font-medium">Email</th>
                <th className="px-4 py-3 font-medium">Username</th>
                <th className="px-4 py-3 font-medium">Role</th>
                <th className="px-4 py-3 font-medium">Employee #</th>
                <th className="px-4 py-3 font-medium">Status</th>
              </tr>
            </thead>
            <tbody>
              {items.map((u) => (
                <tr key={u.id} className="border-b border-white/5 hover:bg-white/5">
                  <td className="px-4 py-3">
                    {[u.first_name, u.last_name].filter(Boolean).join(' ') || '—'}
                  </td>
                  <td className="px-4 py-3">
                    <span
                      className={`inline-flex rounded-full px-2 py-0.5 text-xs font-medium ${
                        u.record_type === 'employee'
                          ? 'bg-blue-500/20 text-blue-600 dark:text-blue-400'
                          : 'bg-slate-500/20 text-slate-600 dark:text-slate-400'
                      }`}
                    >
                      {u.record_type === 'employee' ? 'Employee' : 'User'}
                    </span>
                  </td>
                  <td className="px-4 py-3">{u.email ?? '—'}</td>
                  <td className="px-4 py-3">{u.username ?? '—'}</td>
                  <td className="px-4 py-3">{u.clinic_role ?? '—'}</td>
                  <td className="px-4 py-3 font-mono text-xs">{u.employee_number ?? '—'}</td>
                  <td className="px-4 py-3">
                    {u.is_active_empl !== false && u.is_active !== false ? (
                      <span className="text-green-600 dark:text-green-400">Active</span>
                    ) : (
                      <span className="text-muted-foreground">Inactive</span>
                    )}
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
          {total > items.length && (
            <p className="px-4 py-2 text-xs text-muted-foreground">
              Showing {items.length} of {total}
            </p>
          )}
        </div>
      )}
    </div>
  )
}
