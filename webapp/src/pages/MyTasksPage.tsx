/**
 * Your Tasks – personal tasks per user (not visible to others).
 */

import { useState, useCallback, useMemo } from 'react'
import { createPortal } from 'react-dom'
import { toast } from 'sonner'
import { Plus, CheckCircle2, Trash2, Loader2, Calendar } from 'lucide-react'
import { useMyTasks } from '@/hooks/useMyTasks'
import { DataTable, Column, LoadingSpinner, ErrorMessage, PaginationState } from '@/components/common'
import { Button } from '@/components/ui/button'
import { Input } from '@/components/ui/input'
import { glassmorphism } from '@/lib/glassmorphism'
import { cn } from '@/lib/utils'
import type { UserTask, CreateMyTaskRequest } from '@/types/my-tasks.types'

const DEFAULT_PAGE_SIZE = 10

function formatDate(s: string | null | undefined) {
  if (s == null || s === '') return '–'
  const d = new Date(s)
  if (Number.isNaN(d.getTime())) return '–'
  return d.toLocaleDateString('en-US', { year: 'numeric', month: 'short', day: 'numeric', hour: '2-digit', minute: '2-digit' })
}

function statusStyle(s: string) {
  const map: Record<string, string> = {
    PENDING: 'bg-slate-500/20 text-slate-400',
    IN_PROGRESS: 'bg-blue-500/20 text-blue-400',
    COMPLETED: 'bg-green-500/20 text-green-400',
    CANCELLED: 'bg-slate-600/20 text-slate-500',
  }
  return map[s] ?? 'bg-slate-500/20 text-slate-400'
}

export default function MyTasksPage() {
  const { items, total, loading, error, createTask, deleteTask, completeTask } = useMyTasks()
  const [page, setPage] = useState(1)
  const [pageSize, setPageSize] = useState(DEFAULT_PAGE_SIZE)
  const [modalOpen, setModalOpen] = useState(false)
  const [submitting, setSubmitting] = useState(false)
  const [completingId, setCompletingId] = useState<string | null>(null)
  const [deletingId, setDeletingId] = useState<string | null>(null)
  const [title, setTitle] = useState('')
  const [description, setDescription] = useState('')
  const [dueDate, setDueDate] = useState('')
  const [priority, setPriority] = useState('NORMAL')

  const pagination: PaginationState = useMemo(() => ({ page, pageSize, total }), [page, pageSize, total])
  const paginatedData = useMemo(
    () => items.slice((page - 1) * pageSize, page * pageSize),
    [items, page, pageSize]
  )

  const handleCreate = useCallback(async () => {
    const t = (title ?? '').trim()
    if (!t) {
      toast.warning('Title is required.')
      return
    }
    setSubmitting(true)
    try {
      const payload: CreateMyTaskRequest = {
        title: t,
        description: (description ?? '').trim() || undefined,
        priority: priority || 'NORMAL',
      }
      if ((dueDate ?? '').trim()) payload.due_date = new Date(dueDate).toISOString()
      await createTask(payload)
      toast.success('Task added.')
      setModalOpen(false)
      setTitle('')
      setDescription('')
      setDueDate('')
      setPriority('NORMAL')
    } catch (err: unknown) {
      const msg = (err as { detail?: string })?.detail ?? (err as Error)?.message ?? 'Failed to add task'
      toast.error(msg)
    } finally {
      setSubmitting(false)
    }
  }, [title, description, dueDate, priority, createTask])

  const handleComplete = useCallback(
    async (id: string) => {
      setCompletingId(id)
      try {
        await completeTask(id)
        toast.success('Task completed.')
      } catch {
        toast.error('Failed to complete task.')
      } finally {
        setCompletingId(null)
      }
    },
    [completeTask]
  )

  const handleDelete = useCallback(
    async (id: string) => {
      if (!window.confirm('Delete this task?')) return
      setDeletingId(id)
      try {
        await deleteTask(id)
        toast.success('Task deleted.')
      } catch {
        toast.error('Failed to delete task.')
      } finally {
        setDeletingId(null)
      }
    },
    [deleteTask]
  )

  const columns: Column<UserTask>[] = [
    {
      key: 'title',
      header: 'Title',
      render: (t) => <span className="font-medium text-slate-200">{(t.title ?? '').trim() || '–'}</span>,
    },
    {
      key: 'description',
      header: 'Description',
      render: (t) => <span className="text-slate-400 text-sm max-w-[200px] truncate block">{(t.description ?? '').trim() || '–'}</span>,
    },
    {
      key: 'due_date',
      header: 'Due',
      render: (t) => (
        <div className="flex items-center gap-1 text-slate-400">
          <Calendar className="w-4 h-4" />
          {formatDate(t.due_date)}
        </div>
      ),
    },
    {
      key: 'status',
      header: 'Status',
      render: (t) => (
        <span className={cn('px-2 py-1 rounded text-xs font-medium', statusStyle(t.status ?? ''))}>
          {(t.status ?? 'PENDING').replace('_', ' ')}
        </span>
      ),
    },
    {
      key: 'actions',
      header: 'Actions',
      render: (t) => (
        <div className="flex items-center gap-1">
          {(t.status ?? '') !== 'COMPLETED' && (
            <Button
              variant="ghost"
              size="sm"
              className="h-8 gap-1"
              onClick={() => handleComplete(t.id)}
              disabled={completingId === t.id}
            >
              {completingId === t.id ? <Loader2 className="w-4 h-4 animate-spin" /> : <CheckCircle2 className="w-4 h-4" />}
              Complete
            </Button>
          )}
          <Button variant="ghost" size="sm" className="h-8 text-red-400 hover:text-red-300" onClick={() => handleDelete(t.id)} disabled={deletingId === t.id}>
            {deletingId === t.id ? <Loader2 className="w-4 h-4 animate-spin" /> : <Trash2 className="w-4 h-4" />}
          </Button>
        </div>
      ),
    },
  ]

  if (loading && items.length === 0) {
    return (
      <div className="space-y-6">
        <h1 className="text-2xl font-bold">Your Tasks</h1>
        <div className={cn(glassmorphism('dark', false, false), 'rounded-lg p-8')}>
          <LoadingSpinner text="Loading your tasks..." />
        </div>
      </div>
    )
  }

  return (
    <div className="space-y-6">
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-2xl font-bold">Your Tasks</h1>
          <p className="text-slate-400 text-sm mt-1">Personal tasks – only visible to you.</p>
        </div>
        <Button onClick={() => setModalOpen(true)} className="gap-2">
          <Plus className="w-4 h-4" />
          Add task
        </Button>
      </div>

      {error && <ErrorMessage message={error} />}

      <DataTable
        columns={columns}
        data={paginatedData}
        keyExtractor={(t) => t.id}
        emptyMessage="No tasks yet. Add one above."
        pagination={pagination}
        onPageChange={(p, ps) => {
          setPage(p)
          setPageSize(ps)
        }}
      />

      {modalOpen && createPortal(
        <div
          className="fixed inset-0 z-[100] flex items-center justify-center bg-black/70 min-h-screen w-screen"
          style={{ top: 0, left: 0, right: 0, bottom: 0 }}
          onClick={() => !submitting && setModalOpen(false)}
        >
          <div className="rounded-lg border border-slate-700 bg-slate-900 p-6 shadow-xl w-full max-w-md mx-4" onClick={(e) => e.stopPropagation()}>
            <h3 className="text-lg font-semibold text-slate-200 mb-4">Add task</h3>
            <div className="space-y-4">
              <div>
                <label className="block text-sm text-slate-400 mb-1">Title *</label>
                <Input value={title} onChange={(e) => setTitle(e.target.value)} placeholder="Task title" className="bg-slate-800 border-slate-600" />
              </div>
              <div>
                <label className="block text-sm text-slate-400 mb-1">Description</label>
                <Input value={description} onChange={(e) => setDescription(e.target.value)} placeholder="Optional" className="bg-slate-800 border-slate-600" />
              </div>
              <div>
                <label className="block text-sm text-slate-400 mb-1">Due date</label>
                <Input type="datetime-local" value={dueDate} onChange={(e) => setDueDate(e.target.value)} className="bg-slate-800 border-slate-600" />
              </div>
              <div>
                <label className="block text-sm text-slate-400 mb-1">Priority</label>
                <select value={priority} onChange={(e) => setPriority(e.target.value)} className="w-full rounded border border-slate-600 bg-slate-800 px-3 py-2 text-slate-200">
                  <option value="LOW">Low</option>
                  <option value="NORMAL">Normal</option>
                  <option value="HIGH">High</option>
                </select>
              </div>
            </div>
            <div className="flex gap-2 mt-6 justify-end">
              <Button variant="outline" onClick={() => !submitting && setModalOpen(false)} disabled={submitting}>Cancel</Button>
              <Button onClick={handleCreate} disabled={submitting}>{submitting ? <Loader2 className="w-4 h-4 animate-spin" /> : 'Add'}</Button>
            </div>
          </div>
        </div>,
        document.body
      )}
    </div>
  )
}
