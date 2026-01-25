import { ReactNode } from 'react'
import { motion } from 'framer-motion'
import { glassmorphism } from '@/lib/glassmorphism'
import { cn } from '@/lib/utils'

interface DashboardGridProps {
  children: ReactNode
  className?: string
}

export function DashboardGrid({ children, className }: DashboardGridProps) {
  return (
    <div
      className={cn(
        'grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 xl:grid-cols-4 gap-6',
        className
      )}
    >
      {children}
    </div>
  )
}

interface DashboardSectionProps {
  title?: string
  children: ReactNode
  className?: string
  cols?: 1 | 2 | 3 | 4
}

export function DashboardSection({
  title,
  children,
  className,
  cols = 1,
}: DashboardSectionProps) {
  const colClasses = {
    1: 'lg:col-span-1',
    2: 'lg:col-span-2',
    3: 'lg:col-span-3',
    4: 'lg:col-span-4',
  }

  return (
    <motion.section
      initial={{ opacity: 0, y: 20 }}
      animate={{ opacity: 1, y: 0 }}
      transition={{ duration: 0.5 }}
      className={cn('col-span-full', colClasses[cols], className)}
    >
      {title && (
        <h2 className="text-2xl font-bold mb-4 text-foreground">{title}</h2>
      )}
      {children}
    </motion.section>
  )
}
