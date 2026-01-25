/**
 * Payroll Types
 */

export interface SalaryStructure {
  id: string
  employee_id: string
  base_salary: number
  components: SalaryComponent[]
  effective_date: string
  is_active: boolean
  employee_name?: string
  created_at?: string
  updated_at?: string
}

export interface SalaryComponent {
  name: string
  amount: number
  component_type: ComponentType
  is_percentage: boolean
  percentage_base?: string
  is_taxable: boolean
}

export type ComponentType = 'ALLOWANCE' | 'DEDUCTION' | 'BONUS'

export interface SalaryStructureCreateRequest {
  employee_id: string
  base_salary: number
  components: SalaryComponent[]
  effective_date: string
  is_active?: boolean
}

export interface Attendance {
  id: string
  employee_id: string
  date: string
  check_in?: string | null
  check_out?: string | null
  status: AttendanceStatus
  notes?: string | null
  employee_name?: string
  created_at?: string
  updated_at?: string
}

export type AttendanceStatus = 'PRESENT' | 'ABSENT' | 'LATE' | 'LEAVE' | 'HOLIDAY'

export interface AttendanceCreateRequest {
  employee_id: string
  date: string
  check_in?: string
  check_out?: string
  status: AttendanceStatus
  notes?: string
}

export interface Payroll {
  id: string
  payroll_number: string
  employee_id: string
  payroll_month: string
  base_salary: number
  total_allowances: number
  total_deductions: number
  gross_salary: number
  net_salary: number
  status: PayrollStatus
  employee_name?: string
  created_at?: string
  updated_at?: string
}

export type PayrollStatus = 'DRAFT' | 'PROCESSED' | 'PAID'

export interface PayrollGenerateRequest {
  employee_id: string
  payroll_month: string
}

export interface Payslip {
  id: string
  payslip_number: string
  payroll_id: string
  employee_id: string
  employee_name?: string
  payroll_month?: string
  net_salary?: number
  generated_at?: string
}

export interface PayslipGenerateRequest {
  payroll_id: string
}
