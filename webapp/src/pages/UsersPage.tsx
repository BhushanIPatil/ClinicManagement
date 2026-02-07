import { useCallback, useEffect, useState, useMemo } from 'react'
import { toast } from 'sonner'
import { Link } from 'react-router-dom'
import { UserPlus, RefreshCw } from 'lucide-react'
import { clinicAdminService } from '@/services/clinic-admin.service'
import type { ClinicEmployeeListItem } from '@/services/clinic-admin.service'
import { Button } from '@/components/ui/button'
import { DataTable, Column, LoadingSpinner, ErrorMessage, PaginationState } from '@/components/common'

const DEFAULT_PAGE_SIZE = 10

export default function UsersPage() {
  const [items, setItems] = useState<ClinicEmployeeListItem[]>([])
  const [total, setTotal] = useState(0)
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState<string | null>(null)
  const [page, setPage] = useState(1)
  const [pageSize, setPageSize] = useState(DEFAULT_PAGE_SIZE)

  const load = useCallback(async () => {
    setLoading(true)
    setError(null)
    try {
      const res = await clinicAdminService.listClinicEmployeesCurrentUser({ skip: 0, limit: 500 })
      setItems(res.items)
      setTotal(res.total)
    } catch (err: unknown) {
      const msg = err && typeof err === 'object' && 'detail' in err
        ? String((err as { detail: unknown }).detail)
        : err instanceof Error ? err.message : 'Failed to load users'
      setError(msg)
      toast.error(msg)
      setItems([])
      setTotal(0)
    } finally {
      setLoading(false)
    }
  }, [])

  useEffect(() => {
    load()
  }, [load])

  const pagination: PaginationState = useMemo(
    () => ({ page, pageSize, total: items.length }),
    [page, pageSize, items.length]
  )
  const paginatedData = useMemo(
    () => items.slice((page - 1) * pageSize, page * pageSize),
    [items, page, pageSize]
  )
  const onPageChange = useCallback((p: number, ps: number) => {
    setPage(p)
    setPageSize(ps)
  }, [])

  const columns: Column<ClinicEmployeeListItem>[] = [
    {
      key: 'name',
      header: 'Name',
      render: (u) => [u.first_name, u.last_name].filter(Boolean).join(' ') || '—',
    },
    {
      key: 'record_type',
      header: 'Type',
      render: (u) => (
        <span
          className={
            u.record_type === 'employee'
              ? 'inline-flex rounded-full px-2 py-0.5 text-xs font-medium bg-blue-500/20 text-blue-400'
              : 'inline-flex rounded-full px-2 py-0.5 text-xs font-medium bg-slate-500/20 text-slate-400'
          }
        >
          {u.record_type === 'employee' ? 'Employee' : 'User'}
        </span>
      ),
    },
    { key: 'email', header: 'Email', render: (u) => u.email ?? '—' },
    { key: 'username', header: 'Username', render: (u) => u.username ?? '—' },
    { key: 'clinic_role', header: 'Role', render: (u) => u.clinic_role ?? '—' },
    {
      key: 'employee_number',
      header: 'Employee #',
      render: (u) => <span className="font-mono text-xs">{u.employee_number ?? '—'}</span>,
    },
    {
      key: 'status',
      header: 'Status',
      render: (u) =>
        u.is_active_empl !== false && u.is_active !== false ? (
          <span className="text-green-500">Active</span>
        ) : (
          <span className="text-slate-500">Inactive</span>
        ),
    },
  ]

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
      <p className="text-slate-400 text-sm">
        Users and employees in your clinic. Both have access by role; employees are also in the employees table for HR/payroll.
      </p>

      {error && <ErrorMessage message={error} />}

      {loading && items.length === 0 ? (
        <div className="rounded-lg border border-slate-700/50 bg-slate-900/40 p-8">
          <LoadingSpinner text="Loading users…" />
        </div>
      ) : (
        <DataTable
          columns={columns}
          data={paginatedData}
          keyExtractor={(u) => u.id}
          emptyMessage="No users yet. Use Add User to add the first user to your clinic."
          pagination={pagination}
          onPageChange={onPageChange}
        />
      )}
    </div>
  )
}
