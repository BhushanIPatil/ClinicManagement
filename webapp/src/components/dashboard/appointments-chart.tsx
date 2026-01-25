import {
  BarChart,
  Bar,
  XAxis,
  YAxis,
  CartesianGrid,
  Tooltip,
  ResponsiveContainer,
} from 'recharts'

interface AppointmentsChartProps {
  data: Array<{
    day: string
    scheduled: number
    completed: number
  }>
}

export function AppointmentsChart({ data }: AppointmentsChartProps) {
  const safeData = data ?? []
  if (safeData.length === 0) {
    return (
      <div className="flex items-center justify-center h-[300px] text-muted-foreground">
        No appointment data for this period
      </div>
    )
  }
  return (
    <ResponsiveContainer width="100%" height={300}>
      <BarChart data={safeData} margin={{ top: 10, right: 10, left: 0, bottom: 0 }}>
        <CartesianGrid strokeDasharray="3 3" stroke="#ffffff10" />
        <XAxis
          dataKey="day"
          stroke="#ffffff40"
          style={{ fontSize: '12px' }}
        />
        <YAxis
          stroke="#ffffff40"
          style={{ fontSize: '12px' }}
        />
        <Tooltip
          contentStyle={{
            backgroundColor: 'rgba(0, 0, 0, 0.8)',
            border: '1px solid rgba(255, 255, 255, 0.2)',
            borderRadius: '8px',
            backdropFilter: 'blur(10px)',
          }}
        />
        <Bar
          dataKey="scheduled"
          fill="#3b82f6"
          radius={[8, 8, 0, 0]}
          opacity={0.8}
        />
        <Bar
          dataKey="completed"
          fill="#10b981"
          radius={[8, 8, 0, 0]}
          opacity={0.8}
        />
      </BarChart>
    </ResponsiveContainer>
  )
}
