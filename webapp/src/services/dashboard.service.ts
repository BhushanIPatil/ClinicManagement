/**
 * Dashboard Service
 *
 * Fetches KPI and chart data from the backend. All responses are normalized
 * so that numbers are 0 and arrays are [] when missing, avoiding blank UI.
 */

import { apiService } from './api.service'
import type { DashboardData } from '@/lib/dashboard-data'

const defaultKpis = {
  totalPatients: 0,
  appointmentsToday: 0,
  revenueToday: 0,
  activeDoctors: 0,
}

const num = (v: unknown): number => (typeof v === 'number' && !Number.isNaN(v) ? v : 0)
const arr = <T>(v: unknown): T[] => (Array.isArray(v) ? v : [])

/**
 * Normalize API dashboard response to DashboardData with safe defaults.
 */
function normalize(res: unknown): DashboardData {
  if (res == null || typeof res !== 'object') {
    return {
      kpis: { ...defaultKpis },
      revenueData: [],
      appointmentsData: [],
      patientTrendData: [],
    }
  }
  const r = res as Record<string, unknown>
  const k = (r.kpis as Record<string, unknown>) ?? {}
  return {
    kpis: {
      totalPatients: num(k.totalPatients),
      appointmentsToday: num(k.appointmentsToday),
      revenueToday: num(k.revenueToday),
      activeDoctors: num(k.activeDoctors),
    },
    revenueData: arr(r.revenueData).map((x: any) => ({
      date: typeof x?.date === 'string' ? x.date : '',
      revenue: num(x?.revenue),
      patients: num(x?.patients),
    })),
    appointmentsData: arr(r.appointmentsData).map((x: any) => ({
      day: typeof x?.day === 'string' ? x.day : '',
      scheduled: num(x?.scheduled),
      completed: num(x?.completed),
    })),
    patientTrendData: arr(r.patientTrendData).map((x: any) => ({
      month: typeof x?.month === 'string' ? x.month : '',
      new: num(x?.new),
      returning: num(x?.returning),
    })),
  }
}

/**
 * Fetch dashboard data from the API. Returns normalized data; never null/undefined
 * for numbers or arrays.
 */
export async function getDashboardData(): Promise<DashboardData> {
  const res = await apiService.get<unknown>('/kpi/dashboard')
  return normalize(res)
}
