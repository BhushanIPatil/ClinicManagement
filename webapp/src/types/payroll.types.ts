/**
 * Payroll Types
 * Roster (users on payroll), salary structures, payslips, payroll runs.
 */

export interface ClinicUserForPayroll {
  id: string
  email?: string
  username?: string
  first_name?: string
  last_name?: string
  is_active?: boolean
  clinic_role?: string
  user_access?: string
}

export interface PayrollRosterItem {
  id: string
  user_id: string
  user_name: string
  clinic_id: string
  joining_date: string
  role: string
  salary_structure_id: string | null
  payment_status: 'PENDING' | 'PAID' | 'PARTIAL'
  last_payment_date: string | null
  base_salary: number | null
  gross_salary: number | null
  net_salary: number | null
  created_at?: string
  updated_at?: string
  updated_by_id: string | null
  updated_by_name: string | null
  created_by_id: string | null
  created_by_name: string | null
}

export interface AddToRosterRequest {
  user_id: string
  joining_date: string
  role: string
  salary_structure_id?: string | null
}

export interface UpdateRosterRequest {
  joining_date?: string
  role?: string
  salary_structure_id?: string | null
  payment_status?: 'PENDING' | 'PAID' | 'PARTIAL'
  last_payment_date?: string | null
}

export interface SalaryStructureBackend {
  id: string
  user_id: string | null
  user_name: string | null
  base_salary: number
  housing_allowance: number
  transport_allowance: number
  medical_allowance: number
  other_allowances: number
  tax_deduction: number
  insurance_deduction: number
  other_deductions: number
  gross_salary: number
  net_salary: number
  is_active: boolean
  notes: string | null
}

export interface CreateSalaryStructureRequest {
  user_id: string
  base_salary: number
  housing_allowance?: number
  transport_allowance?: number
  medical_allowance?: number
  other_allowances?: number
  tax_deduction?: number
  insurance_deduction?: number
  other_deductions?: number
  notes?: string | null
}

export interface PayrollRun {
  id: string
  payroll_number: string
  period_start: string
  period_end: string
  pay_date: string | null
  status: string
  total_gross: number
  total_deductions: number
  total_net: number
  employee_count: number
  clinic_id: string | null
  notes: string | null
  created_at?: string
  updated_at?: string
}

export interface PayslipItem {
  id: string
  payslip_number: string
  payroll_id: string
  payroll_number?: string
  period_start?: string
  period_end?: string
  employee_id?: string | null
  user_id?: string | null
  user_name?: string | null
  base_salary: number
  gross_salary: number
  net_salary: number
  status: string
  notes?: string | null
}

export interface SalaryStructure {
  id: string
  employee_id?: string
  base_salary: number
  components?: SalaryComponent[]
  effective_date?: string
  is_active?: boolean
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

export type PayrollStatus = 'DRAFT' | 'PROCESSED' | 'PAID'
