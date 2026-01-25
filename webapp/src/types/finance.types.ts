/**
 * Finance Types
 */

export interface Invoice {
  id: string
  invoice_number: string
  patient_id: string
  total_amount: number
  subtotal: number
  tax_amount: number
  status: InvoiceStatus
  due_date: string
  issued_date?: string | null
  paid_date?: string | null
  line_items: InvoiceLineItem[]
  patient_name?: string
  created_at?: string
  updated_at?: string
}

export type InvoiceStatus = 'DRAFT' | 'ISSUED' | 'PAID' | 'OVERDUE' | 'CANCELLED'

export interface InvoiceLineItem {
  description: string
  quantity: number
  unit_price: number
  total: number
}

export interface InvoiceCreateRequest {
  patient_id: string
  due_date: string
  line_items: InvoiceLineItem[]
  notes?: string
}

export interface Payment {
  id: string
  payment_number: string
  invoice_id: string
  amount: number
  payment_method: PaymentMethod
  payment_date: string
  reference_number?: string | null
  notes?: string | null
  invoice_number?: string
  created_at?: string
}

export type PaymentMethod = 'CASH' | 'CARD' | 'BANK_TRANSFER' | 'CHEQUE' | 'INSURANCE'

export interface PaymentCreateRequest {
  invoice_id: string
  amount: number
  payment_method: PaymentMethod
  payment_date: string
  reference_number?: string
  notes?: string
}

export interface Insurance {
  id: string
  patient_id: string
  insurance_provider: string
  policy_number: string
  coverage_type: string
  coverage_amount?: number | null
  expiry_date?: string | null
  is_active: boolean
  patient_name?: string
  created_at?: string
  updated_at?: string
}

export interface InsuranceCreateRequest {
  patient_id: string
  insurance_provider: string
  policy_number: string
  coverage_type: string
  coverage_amount?: number
  expiry_date?: string
  is_active?: boolean
}
