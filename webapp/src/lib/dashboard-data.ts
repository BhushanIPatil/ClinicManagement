/**
 * Dashboard data types and fetch from API.
 * Data is loaded via dashboard.service; all numeric and list fields
 * are normalized to 0 / [] when missing to avoid blank UI.
 */

export interface DashboardData {
  kpis: {
    totalPatients: number
    appointmentsToday: number
    revenueToday: number
    activeDoctors: number
  }
  revenueData: Array<{
    date: string
    revenue: number
    patients: number
  }>
  appointmentsData: Array<{
    day: string
    scheduled: number
    completed: number
  }>
  patientTrendData: Array<{
    month: string
    new: number
    returning: number
  }>
}

/**
 * Fetch dashboard data from the API (via dashboard.service).
 * Returns normalized data; numbers and arrays are never null/undefined.
 */
export async function fetchDashboardData(): Promise<DashboardData> {
  const { getDashboardData } = await import('@/services/dashboard.service')
  return getDashboardData()
}
