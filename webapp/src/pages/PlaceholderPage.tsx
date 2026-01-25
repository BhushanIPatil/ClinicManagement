import { useLocation } from 'react-router-dom'

const LABELS: Record<string, string> = {
  payroll: 'Payroll',
  finance: 'Finance',
  kpi: 'KPI & Targets',
  users: 'Users',
}

export default function PlaceholderPage() {
  const loc = useLocation()
  const segment = loc.pathname.split('/').filter(Boolean)[0] || 'page'
  const title = LABELS[segment] ?? segment.replace(/-/g, ' ')
  return (
    <div className="space-y-6">
      <h1 className="text-2xl font-bold">{title}</h1>
      <p className="text-muted-foreground">Content for {title} will appear here.</p>
    </div>
  )
}
