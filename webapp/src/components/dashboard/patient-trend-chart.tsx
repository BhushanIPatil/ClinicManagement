import {
  LineChart,
  Line,
  XAxis,
  YAxis,
  CartesianGrid,
  Tooltip,
  ResponsiveContainer,
  Legend,
} from 'recharts'

interface PatientTrendChartProps {
  data: Array<{
    month: string
    new: number
    returning: number
  }>
}

export function PatientTrendChart({ data }: PatientTrendChartProps) {
  const safeData = data ?? []
  if (safeData.length === 0) {
    return (
      <div className="flex items-center justify-center h-[300px] text-muted-foreground">
        No patient trend data for this period
      </div>
    )
  }
  return (
    <ResponsiveContainer width="100%" height={300}>
      <LineChart data={safeData} margin={{ top: 10, right: 10, left: 0, bottom: 0 }}>
        <CartesianGrid strokeDasharray="3 3" stroke="#ffffff10" />
        <XAxis
          dataKey="month"
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
        <Legend
          wrapperStyle={{ paddingTop: '20px' }}
          iconType="line"
        />
        <Line
          type="monotone"
          dataKey="new"
          stroke="#8b5cf6"
          strokeWidth={2}
          dot={{ fill: '#8b5cf6', r: 4 }}
          name="New Patients"
        />
        <Line
          type="monotone"
          dataKey="returning"
          stroke="#ec4899"
          strokeWidth={2}
          dot={{ fill: '#ec4899', r: 4 }}
          name="Returning Patients"
        />
      </LineChart>
    </ResponsiveContainer>
  )
}
