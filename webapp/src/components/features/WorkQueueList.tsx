/**
 * Work Queue List Component
 * 
 * Displays work queue items with priority-based styling.
 */

import { useState, useMemo } from 'react'
import { AlertCircle, Clock, User, CheckCircle2 } from 'lucide-react'
import { useWorkQueue } from '@/hooks/useWorkQueue'
import { DataTable, Column, LoadingSpinner, ErrorMessage, PaginationState } from '@/components/common'
import { Button } from '@/components/ui/button'
import { cn } from '@/lib/utils'
import type { WorkQueueItem } from '@/types/work-queue.types'

interface WorkQueueListProps {
  status?: string
  priority?: string
  /** Only show future items (due in future, not completed/cancelled) */
  future_only?: boolean
  className?: string
}

const DEFAULT_PAGE_SIZE = 10

export function WorkQueueList({
  status,
  priority,
  future_only,
  className,
}: WorkQueueListProps) {
  const { items, loading, error, completeItem } = useWorkQueue({
    status,
    priority,
    future_only,
  })
  const [page, setPage] = useState(1)
  const [pageSize, setPageSize] = useState(DEFAULT_PAGE_SIZE)
  const list = Array.isArray(items) ? items : []
  const total = list.length
  const pagination: PaginationState = useMemo(
    () => ({ page, pageSize, total }),
    [page, pageSize, total]
  )
  const paginatedData = useMemo(
    () => list.slice((page - 1) * pageSize, page * pageSize),
    [list, page, pageSize]
  )
  const onPageChange = (p: number, ps: number) => {
    setPage(p)
    setPageSize(ps)
  }

  const getPriorityColor = (priority: string) => {
    const colors: Record<string, string> = {
      CRITICAL: 'bg-red-500/20 text-red-400 border-red-500/30',
      URGENT: 'bg-red-500/20 text-red-400 border-red-500/30',
      HIGH: 'bg-orange-500/20 text-orange-400 border-orange-500/30',
      MEDIUM: 'bg-yellow-500/20 text-yellow-400 border-yellow-500/30',
      NORMAL: 'bg-slate-500/20 text-slate-400 border-slate-500/30',
      LOW: 'bg-blue-500/20 text-blue-400 border-blue-500/30',
    }
    return colors[priority] || 'bg-gray-500/20 text-gray-400'
  }

  const getStatusColor = (status: string) => {
    const colors: Record<string, string> = {
      PENDING: 'bg-yellow-500/20 text-yellow-400',
      IN_PROGRESS: 'bg-blue-500/20 text-blue-400',
      COMPLETED: 'bg-green-500/20 text-green-400',
      CANCELLED: 'bg-gray-500/20 text-gray-400',
    }
    return colors[status] || 'bg-gray-500/20 text-gray-400'
  }

  const formatDate = (dateString?: string | null) => {
    if (!dateString) return '-'
    return new Date(dateString).toLocaleDateString('en-US', {
      year: 'numeric',
      month: 'short',
      day: 'numeric',
      hour: '2-digit',
      minute: '2-digit',
    })
  }

  const handleComplete = async (id: string) => {
    try {
      await completeItem(id)
    } catch (err) {
      // Error handled by hook
    }
  }

  const columns: Column<WorkQueueItem>[] = [
    {
      key: 'title',
      header: 'Title',
      render: (item) => (
        <div className="flex items-center gap-2">
          <AlertCircle className="w-4 h-4 text-muted-foreground" />
          <span className="font-medium">{item.title ?? '–'}</span>
        </div>
      ),
    },
    {
      key: 'priority',
      header: 'Priority',
      render: (item) => (
        <span
          className={cn(
            'px-2 py-1 rounded text-xs font-medium border',
            getPriorityColor(item.priority ?? '')
          )}
        >
        {item.priority ?? '–'}
        </span>
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
        {(item.status ?? '').replace('_', ' ')}
        </span>
      ),
    },
    {
      key: 'assigned_to_user_name',
      header: 'Assigned To',
      render: (item) => (
        <div className="flex items-center gap-2">
          <User className="w-4 h-4 text-muted-foreground" />
          <span>{(item.assigned_to_user_name ?? '').trim() || 'Unassigned'}</span>
        </div>
      ),
    },
    {
      key: 'due_date',
      header: 'Due Date',
      render: (item) => (
        <div className="flex items-center gap-2">
          <Clock className="w-4 h-4 text-muted-foreground" />
          <span className="text-sm">{formatDate(item.due_date)}</span>
        </div>
      ),
    },
    {
      key: 'actions',
      header: 'Actions',
      render: (item) => (
        <div className="flex items-center gap-2">
          {(item.status ?? '') !== 'COMPLETED' && (
            <Button
              size="sm"
              variant="outline"
              onClick={() => handleComplete(item.id)}
              className="h-7"
            >
              <CheckCircle2 className="w-3 h-3 mr-1" />
              Complete
            </Button>
          )}
        </div>
      ),
    },
  ]

  if (loading) {
    return (
      <div className={cn('p-8', className)}>
        <LoadingSpinner text="Loading work queue..." />
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

  return (
    <div className={cn(className)}>
      <DataTable
        columns={columns}
        data={paginatedData}
        keyExtractor={(item) => item.id}
        emptyMessage="No work queue items found"
        pagination={pagination}
        onPageChange={onPageChange}
      />
    </div>
  )
}
