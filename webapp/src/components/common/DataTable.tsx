/**
 * Data Table Component
 * 
 * Reusable table component with consistent styling.
 */

import { ReactNode } from 'react'
import { cn } from '@/lib/utils'
import { glassmorphism } from '@/lib/glassmorphism'

export interface Column<T> {
  key: string
  header: string
  render?: (item: T) => ReactNode
  className?: string
}

interface DataTableProps<T> {
  columns: Column<T>[]
  data: T[]
  keyExtractor: (item: T) => string
  emptyMessage?: string
  className?: string
}

export function DataTable<T>({
  columns,
  data,
  keyExtractor,
  emptyMessage = 'No data available',
  className,
}: DataTableProps<T>) {
  if (data.length === 0) {
    return (
      <div className={cn('text-center py-8 text-muted-foreground', className)}>
        {emptyMessage}
      </div>
    )
  }

  return (
    <div
      className={cn(
        glassmorphism('dark', false, true),
        'rounded-lg overflow-hidden border border-white/20',
        className
      )}
    >
      <div className="overflow-x-auto">
        <table className="w-full">
          <thead>
            <tr className="border-b border-white/20">
              {columns.map((column) => (
                <th
                  key={column.key}
                  className={cn(
                    'px-4 py-3 text-left text-sm font-medium text-muted-foreground',
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
                className="border-b border-white/10 hover:bg-white/5 transition-colors"
              >
                {columns.map((column) => (
                  <td
                    key={column.key}
                    className={cn('px-4 py-3 text-sm', column.className)}
                  >
                    {column.render
                      ? column.render(item)
                      : (item as any)[column.key] || '-'}
                  </td>
                ))}
              </tr>
            ))}
          </tbody>
        </table>
      </div>
    </div>
  )
}
