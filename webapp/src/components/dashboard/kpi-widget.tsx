import { motion } from 'framer-motion'
import { LucideIcon } from 'lucide-react'
import { glassmorphism } from '@/lib/glassmorphism'
import { cn } from '@/lib/utils'

interface KPIWidgetProps {
  title: string
  value: string | number
  change?: number
  icon: LucideIcon
  trend?: 'up' | 'down' | 'neutral'
  delay?: number
}

export function KPIWidget({
  title,
  value,
  change,
  icon: Icon,
  trend = 'neutral',
  delay = 0,
}: KPIWidgetProps) {
  const trendColors = {
    up: 'text-green-400',
    down: 'text-red-400',
    neutral: 'text-muted-foreground',
  }

  const trendIcons = {
    up: '↑',
    down: '↓',
    neutral: '→',
  }

  return (
    <motion.div
      initial={{ opacity: 0, y: 20 }}
      animate={{ opacity: 1, y: 0 }}
      transition={{ duration: 0.5, delay }}
      whileHover={{ scale: 1.02, y: -5 }}
      className={cn(
        glassmorphism('dark', true, true),
        'rounded-2xl p-6 cursor-pointer'
      )}
    >
      <div className="flex items-start justify-between mb-4">
        <div className="p-3 rounded-xl bg-primary/20">
          <Icon className="w-6 h-6 text-primary" />
        </div>
        {change !== undefined && (
          <div className={cn('flex items-center gap-1 text-sm', trendColors[trend])}>
            <span>{trendIcons[trend]}</span>
            <span>{Math.abs(change)}%</span>
          </div>
        )}
      </div>
      
      <div className="space-y-1">
        <p className="text-sm text-muted-foreground">{title}</p>
        <h3 className="text-3xl font-bold">
          {value !== undefined && value !== null && value !== ''
            ? value
            : '0'}
        </h3>
      </div>
    </motion.div>
  )
}
