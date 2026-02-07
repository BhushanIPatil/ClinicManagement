/**
 * Data Table Component
 *
 * Reusable table with optional pagination (top and bottom).
 */

import { ReactNode } from 'react'
import { ChevronLeft, ChevronRight } from 'lucide-react'
import { cn } from '@/lib/utils'
import { glassmorphism } from '@/lib/glassmorphism'
import { Button } from '@/components/ui/button'

export interface Column<T> {
  key: string
  header: string
  render?: (item: T) => ReactNode
  className?: string
}

export interface PaginationState {
  page: number
  pageSize: number
  total: number
}

interface DataTableProps<T> {
  columns: Column<T>[]
  data: T[]
  keyExtractor: (item: T) => string
  emptyMessage?: string
  className?: string
  /** When provided, pagination controls are shown above and below the table */
  pagination?: PaginationState
  onPageChange?: (page: number, pageSize: number) => void
}

const PAGE_SIZE_OPTIONS = [10, 25, 50, 100]

function PaginationBar({
  pagination,
  onPageChange,
  position,
}: {
  pagination: PaginationState
  onPageChange: (page: number, pageSize: number) => void
  position: 'top' | 'bottom'
}) {
  const { page, pageSize, total } = pagination
  const totalPages = Math.max(1, Math.ceil(total / pageSize))
  const start = total === 0 ? 0 : (page - 1) * pageSize + 1
  const end = Math.min(page * pageSize, total)

  return (
    <div
      className={cn(
        'flex flex-wrap items-center justify-between gap-3 px-4 py-2 border-slate-700/50 text-sm text-slate-400',
        position === 'top' ? 'border-b' : 'border-t'
      )}
    >
      <div className="flex items-center gap-4">
        <span>
          {total === 0 ? '0' : `${start}–${end}`} of {total}
        </span>
        <select
          value={pageSize}
          onChange={(e) => onPageChange(1, Number(e.target.value))}
          className="h-8 rounded border border-slate-600 bg-slate-800 px-2 text-slate-200 focus:outline-none focus:ring-1 focus:ring-slate-500"
        >
          {PAGE_SIZE_OPTIONS.map((n) => (
            <option key={n} value={n}>
              {n} per page
            </option>
          ))}
        </select>
      </div>
      <div className="flex items-center gap-1">
        <Button
          variant="ghost"
          size="icon"
          className="h-8 w-8"
          disabled={page <= 1}
          onClick={() => onPageChange(page - 1, pageSize)}
        >
          <ChevronLeft className="h-4 w-4" />
        </Button>
        <span className="min-w-[6rem] text-center">
          Page {page} of {totalPages}
        </span>
        <Button
          variant="ghost"
          size="icon"
          className="h-8 w-8"
          disabled={page >= totalPages}
          onClick={() => onPageChange(page + 1, pageSize)}
        >
          <ChevronRight className="h-4 w-4" />
        </Button>
      </div>
    </div>
  )
}

export function DataTable<T>({
  columns,
  data,
  keyExtractor,
  emptyMessage = 'No data available',
  className,
  pagination,
  onPageChange,
}: DataTableProps<T>) {
  const showPagination = pagination && onPageChange

  if (data.length === 0 && !showPagination) {
    return (
      <div className={cn('text-center py-8 text-slate-500', className)}>
        {emptyMessage}
      </div>
    )
  }

  return (
    <div
      className={cn(
        glassmorphism('dark', false, false),
        'rounded-lg overflow-hidden border border-slate-700/50',
        className
      )}
    >
      {showPagination && (
        <PaginationBar
          pagination={pagination}
          onPageChange={onPageChange}
          position="top"
        />
      )}
      <div className="overflow-x-auto">
        {data.length === 0 ? (
          <div className="py-8 text-center text-slate-500">{emptyMessage}</div>
        ) : (
          <table className="w-full">
            <thead>
              <tr className="border-b border-slate-700/50">
                {columns.map((column) => (
                  <th
                    key={column.key}
                    className={cn(
                      'px-4 py-3 text-left text-sm font-medium text-slate-400',
                      column.className
                    )}
                  >
                    {column.header}
                  </th>
                ))}
              </tr>
            </thead>
            <tbody>
              {data.map((item) => (
                <tr
                  key={keyExtractor(item)}
                  className="border-b border-slate-700/30 hover:bg-slate-800/40 transition-colors"
                >
                  {columns.map((column) => (
                    <td
                      key={column.key}
                      className={cn('px-4 py-3 text-sm text-slate-200', column.className)}
                    >
                      {column.render
                        ? column.render(item)
                        : (item as Record<string, unknown>)[column.key] ?? '-'}
                    </td>
                  ))}
                </tr>
              ))}
            </tbody>
          </table>
        )}
      </div>
      {showPagination && (
        <PaginationBar
          pagination={pagination}
          onPageChange={onPageChange}
          position="bottom"
        />
      )}
    </div>
  )
}
