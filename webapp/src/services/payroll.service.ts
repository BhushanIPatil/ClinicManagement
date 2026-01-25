/**
 * Payroll Service
 * 
 * Handles all payroll-related API calls.
 */

import { apiService } from './api.service'
import type {
  SalaryStructure,
  SalaryStructureCreateRequest,
  Attendance,
  AttendanceCreateRequest,
  Payroll,
  PayrollGenerateRequest,
  Payslip,
  PayslipGenerateRequest,
} from '@/types/payroll.types'

class PayrollService {
  // Salary Structure methods
  async createSalaryStructure(
    data: SalaryStructureCreateRequest
  ): Promise<SalaryStructure> {
    return apiService.post<SalaryStructure>(
      '/payroll/salary-structures',
      data
    )
  }

  async getSalaryStructure(id: string): Promise<SalaryStructure> {
    return apiService.get<SalaryStructure>(
      `/payroll/salary-structures/${id}`
    )
  }

  // Attendance methods
  async createAttendance(data: AttendanceCreateRequest): Promise<Attendance> {
    return apiService.post<Attendance>('/payroll/attendance', data)
  }

  async listAttendance(params?: {
    employee_id?: string
    start_date?: string
    end_date?: string
  }): Promise<Attendance[]> {
    const queryParams = new URLSearchParams()
    if (params?.employee_id)
      queryParams.append('employee_id', params.employee_id)
    if (params?.start_date) queryParams.append('start_date', params.start_date)
    if (params?.end_date) queryParams.append('end_date', params.end_date)

    const query = queryParams.toString()
    return apiService.get<Attendance[]>(
      `/payroll/attendance${query ? `?${query}` : ''}`
    )
  }

  // Payroll methods
  async generatePayroll(data: PayrollGenerateRequest): Promise<Payroll> {
    return apiService.post<Payroll>('/payroll/generate', data)
  }

  async processPayroll(payrollId: string): Promise<Payroll> {
    return apiService.post<Payroll>(`/payroll/process`, { payroll_id: payrollId })
  }

  async getPayroll(id: string): Promise<Payroll> {
    return apiService.get<Payroll>(`/payroll/payrolls/${id}`)
  }

  async listPayrolls(params?: {
    employee_id?: string
    payroll_month?: string
  }): Promise<Payroll[]> {
    const queryParams = new URLSearchParams()
    if (params?.employee_id)
      queryParams.append('employee_id', params.employee_id)
    if (params?.payroll_month)
      queryParams.append('payroll_month', params.payroll_month)

    const query = queryParams.toString()
    return apiService.get<Payroll[]>(
      `/payroll/payrolls${query ? `?${query}` : ''}`
    )
  }

  // Payslip methods
  async generatePayslip(data: PayslipGenerateRequest): Promise<Payslip> {
    return apiService.post<Payslip>('/payroll/payslips/generate', data)
  }

  async getPayslip(id: string): Promise<Payslip> {
    return apiService.get<Payslip>(`/payroll/payslips/${id}`)
  }

  async listPayslips(params?: {
    employee_id?: string
  }): Promise<Payslip[]> {
    const queryParams = new URLSearchParams()
    if (params?.employee_id)
      queryParams.append('employee_id', params.employee_id)

    const query = queryParams.toString()
    return apiService.get<Payslip[]>(
      `/payroll/payslips${query ? `?${query}` : ''}`
    )
  }
}

export const payrollService = new PayrollService()
