import { motion } from 'framer-motion'
import { ReactNode } from 'react'
import { glassmorphism } from '@/lib/glassmorphism'
import { cn } from '@/lib/utils'
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card'

interface ChartCardProps {
  title: string
  description?: string
  children: ReactNode
  delay?: number
  className?: string
}

export function ChartCard({
  title,
  description,
  children,
  delay = 0,
  className,
}: ChartCardProps) {
  return (
    <motion.div
      initial={{ opacity: 0, scale: 0.95 }}
      animate={{ opacity: 1, scale: 1 }}
      transition={{ duration: 0.5, delay }}
      whileHover={{ scale: 1.01 }}
    >
      <Card
        className={cn(
          glassmorphism('dark', true, true),
          'border-white/20 rounded-2xl overflow-hidden',
          className
        )}
      >
        <CardHeader>
          <CardTitle className="text-xl">{title}</CardTitle>
          {description && (
            <CardDescription className="text-muted-foreground">
              {description}
            </CardDescription>
          )}
        </CardHeader>
        <CardContent>{children}</CardContent>
      </Card>
    </motion.div>
  )
}
