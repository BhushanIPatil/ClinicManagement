/**
 * Payroll Service
 * Handles roster, clinic users, salary structures, payroll runs, payslips.
 */

import { apiService } from './api.service'
import type {
  PayrollRosterItem,
  ClinicUserForPayroll,
  AddToRosterRequest,
  UpdateRosterRequest,
  SalaryStructureBackend,
  CreateSalaryStructureRequest,
  PayrollRun,
  PayslipItem,
} from '@/types/payroll.types'

class PayrollService {
  /** Users in clinic that can be added to payroll (not already on roster) */
  async listClinicUsersForPayroll(): Promise<{ items: ClinicUserForPayroll[]; total: number }> {
    return apiService.get<{ items: ClinicUserForPayroll[]; total: number }>('/payroll/clinic-users')
  }

  /** Payroll roster for current user's clinic */
  async listRoster(params?: { skip?: number; limit?: number }): Promise<{
    items: PayrollRosterItem[]
    total: number
    skip: number
    limit: number
  }> {
    const q = new URLSearchParams()
    if (params?.skip != null) q.append('skip', String(params.skip))
    if (params?.limit != null) q.append('limit', String(params.limit))
    const query = q.toString()
    return apiService.get(`/payroll/roster${query ? `?${query}` : ''}`)
  }

  async addToRoster(body: AddToRosterRequest): Promise<PayrollRosterItem> {
    return apiService.post<PayrollRosterItem>('/payroll/roster', {
      ...body,
      user_id: body.user_id,
      joining_date: body.joining_date,
      role: body.role,
      salary_structure_id: body.salary_structure_id || null,
    })
  }

  async updateRoster(assignmentId: string, body: UpdateRosterRequest): Promise<PayrollRosterItem> {
    return apiService.put<PayrollRosterItem>(`/payroll/roster/${assignmentId}`, body)
  }

  async removeFromRoster(assignmentId: string): Promise<{ message: string }> {
    return apiService.delete(`/payroll/roster/${assignmentId}`)
  }

  /** Salary structures (optionally filter by user_id) */
  async listSalaryStructures(params?: {
    user_id?: string
    skip?: number
    limit?: number
  }): Promise<{ items: SalaryStructureBackend[]; total: number; skip: number; limit: number }> {
    const q = new URLSearchParams()
    if (params?.user_id) q.append('user_id', params.user_id)
    if (params?.skip != null) q.append('skip', String(params.skip))
    if (params?.limit != null) q.append('limit', String(params.limit))
    const query = q.toString()
    return apiService.get(`/payroll/salary-structures${query ? `?${query}` : ''}`)
  }

  async createSalaryStructure(body: CreateSalaryStructureRequest): Promise<SalaryStructureBackend> {
    return apiService.post<SalaryStructureBackend>('/payroll/salary-structures', body)
  }

  async getSalaryStructure(structureId: string): Promise<SalaryStructureBackend> {
    return apiService.get<SalaryStructureBackend>(`/payroll/salary-structures/${structureId}`)
  }

  /** Payroll runs */
  async listPayrollRuns(params?: {
    skip?: number
    limit?: number
    status?: string
    clinic_id?: string
  }): Promise<{ items: PayrollRun[]; total: number; skip: number; limit: number }> {
    const q = new URLSearchParams()
    if (params?.skip != null) q.append('skip', String(params.skip))
    if (params?.limit != null) q.append('limit', String(params.limit))
    if (params?.status) q.append('status', params.status)
    if (params?.clinic_id) q.append('clinic_id', params.clinic_id)
    const query = q.toString()
    return apiService.get(`/payroll/runs${query ? `?${query}` : ''}`)
  }

  async createPayrollRun(body: {
    period_start: string
    period_end: string
    pay_date?: string
    status?: string
    clinic_id?: string
    notes?: string
  }): Promise<PayrollRun> {
    return apiService.post<PayrollRun>('/payroll/runs', body)
  }

  async getPayrollRun(payrollId: string): Promise<PayrollRun> {
    return apiService.get<PayrollRun>(`/payroll/runs/${payrollId}`)
  }

  /** Generate payslips for a payroll run from roster */
  async generatePayslips(payrollId: string): Promise<{ message: string; count: number; payslip_numbers: string[] }> {
    return apiService.post('/payroll/payslips/generate', { payroll_id: payrollId })
  }

  /** Payslips */
  async listPayslips(params?: {
    skip?: number
    limit?: number
    payroll_id?: string
    clinic_id?: string
    status?: string
  }): Promise<{ items: PayslipItem[]; total: number; skip: number; limit: number }> {
    const q = new URLSearchParams()
    if (params?.skip != null) q.append('skip', String(params.skip))
    if (params?.limit != null) q.append('limit', String(params.limit))
    if (params?.payroll_id) q.append('payroll_id', params.payroll_id)
    if (params?.clinic_id) q.append('clinic_id', params.clinic_id)
    if (params?.status) q.append('status', params.status)
    const query = q.toString()
    return apiService.get(`/payroll/payslips${query ? `?${query}` : ''}`)
  }

  async getPayslip(payslipId: string): Promise<PayslipItem> {
    return apiService.get<PayslipItem>(`/payroll/payslips/${payslipId}`)
  }
}

export const payrollService = new PayrollService()
