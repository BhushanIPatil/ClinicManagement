import { useEffect, useState } from 'react'
import { Users, Calendar, DollarSign, UserCheck } from 'lucide-react'
import { DashboardLayout } from '@/components/dashboard/dashboard-layout'
import { DashboardGrid, DashboardSection } from '@/components/dashboard/dashboard-grid'
import { KPIWidget } from '@/components/dashboard/kpi-widget'
import { ChartCard } from '@/components/dashboard/chart-card'
import { RevenueChart } from '@/components/dashboard/revenue-chart'
import { AppointmentsChart } from '@/components/dashboard/appointments-chart'
import { PatientTrendChart } from '@/components/dashboard/patient-trend-chart'
import { fetchDashboardData, type DashboardData } from '@/lib/dashboard-data'

export default function Dashboard() {
  const [data, setData] = useState<DashboardData | null>(null)
  const [loading, setLoading] = useState(true)

  useEffect(() => {
    async function loadData() {
      try {
        const dashboardData = await fetchDashboardData()
        setData(dashboardData)
      } catch (error) {
        console.error('Failed to load dashboard data:', error)
      } finally {
        setLoading(false)
      }
    }

    loadData()
  }, [])

  if (loading || !data) {
    return (
      <DashboardLayout>
        <div className="flex items-center justify-center min-h-[60vh]">
          <div className="text-center">
            <div className="w-16 h-16 border-4 border-primary border-t-transparent rounded-full animate-spin mx-auto mb-4" />
            <p className="text-muted-foreground">Loading dashboard...</p>
          </div>
        </div>
      </DashboardLayout>
    )
  }

  const kpis = data.kpis ?? {}
  const totalPatients = Number(kpis.totalPatients) || 0
  const appointmentsToday = Number(kpis.appointmentsToday) || 0
  const revenueToday = Number(kpis.revenueToday) || 0
  const activeDoctors = Number(kpis.activeDoctors) || 0
  const revenueData = Array.isArray(data.revenueData) ? data.revenueData : []
  const appointmentsData = Array.isArray(data.appointmentsData) ? data.appointmentsData : []
  const patientTrendData = Array.isArray(data.patientTrendData) ? data.patientTrendData : []

  return (
    <DashboardLayout>
      {/* KPI Widgets */}
      <DashboardSection cols={4}>
        <DashboardGrid>
          <KPIWidget
            title="Total Patients"
            value={totalPatients.toLocaleString()}
            icon={Users}
            delay={0}
          />
          <KPIWidget
            title="Appointments Today"
            value={appointmentsToday}
            icon={Calendar}
            delay={0.1}
          />
          <KPIWidget
            title="Revenue Today"
            value={`$${revenueToday.toLocaleString()}`}
            icon={DollarSign}
            delay={0.2}
          />
          <KPIWidget
            title="Active Doctors"
            value={activeDoctors}
            icon={UserCheck}
            delay={0.3}
          />
        </DashboardGrid>
      </DashboardSection>

      {/* Charts Row 1 */}
      <DashboardSection cols={2}>
        <ChartCard
          title="Revenue Trend"
          description="Weekly revenue and patient visits"
          delay={0.4}
        >
          <RevenueChart data={revenueData} />
        </ChartCard>
      </DashboardSection>

      <DashboardSection cols={2}>
        <ChartCard
          title="Appointments"
          description="Scheduled vs completed appointments"
          delay={0.5}
        >
          <AppointmentsChart data={appointmentsData} />
        </ChartCard>
      </DashboardSection>

      {/* Charts Row 2 */}
      <DashboardSection cols={4}>
        <ChartCard
          title="Patient Growth"
          description="New vs returning patients over time"
          delay={0.6}
        >
          <PatientTrendChart data={patientTrendData} />
        </ChartCard>
      </DashboardSection>
    </DashboardLayout>
  )
}
