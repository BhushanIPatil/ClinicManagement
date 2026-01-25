import {
  AreaChart,
  Area,
  XAxis,
  YAxis,
  CartesianGrid,
  Tooltip,
  ResponsiveContainer,
} from 'recharts'

interface RevenueChartProps {
  data: Array<{
    date: string
    revenue: number
    patients: number
  }>
}

export function RevenueChart({ data }: RevenueChartProps) {
  const safeData = data ?? []
  if (safeData.length === 0) {
    return (
      <div className="flex items-center justify-center h-[300px] text-muted-foreground">
        No revenue data for this period
      </div>
    )
  }
  return (
    <ResponsiveContainer width="100%" height={300}>
      <AreaChart data={safeData} margin={{ top: 10, right: 10, left: 0, bottom: 0 }}>
        <defs>
          <linearGradient id="colorRevenue" x1="0" y1="0" x2="0" y2="1">
            <stop offset="5%" stopColor="#3b82f6" stopOpacity={0.8} />
            <stop offset="95%" stopColor="#3b82f6" stopOpacity={0} />
          </linearGradient>
        </defs>
        <CartesianGrid strokeDasharray="3 3" stroke="#ffffff10" />
        <XAxis
          dataKey="date"
          stroke="#ffffff40"
          style={{ fontSize: '12px' }}
        />
        <YAxis
          stroke="#ffffff40"
          style={{ fontSize: '12px' }}
          tickFormatter={(value) => `$${value}`}
        />
        <Tooltip
          contentStyle={{
            backgroundColor: 'rgba(0, 0, 0, 0.8)',
            border: '1px solid rgba(255, 255, 255, 0.2)',
            borderRadius: '8px',
            backdropFilter: 'blur(10px)',
          }}
        />
        <Area
          type="monotone"
          dataKey="revenue"
          stroke="#3b82f6"
          strokeWidth={2}
          fillOpacity={1}
          fill="url(#colorRevenue)"
        />
      </AreaChart>
    </ResponsiveContainer>
  )
}
