/**
 * Finance Service
 * 
 * Handles all finance-related API calls.
 */

import { apiService } from './api.service'
import type {
  Invoice,
  InvoiceCreateRequest,
  Payment,
  PaymentCreateRequest,
  Insurance,
  InsuranceCreateRequest,
} from '@/types/finance.types'

class FinanceService {
  // Invoice methods
  async createInvoice(data: InvoiceCreateRequest): Promise<Invoice> {
    return apiService.post<Invoice>('/finance/invoices', data)
  }

  async getInvoice(id: string): Promise<Invoice> {
    return apiService.get<Invoice>(`/finance/invoices/${id}`)
  }

  async listInvoices(params?: {
    patient_id?: string
    status?: string
    page?: number
  }): Promise<Invoice[]> {
    const queryParams = new URLSearchParams()
    if (params?.patient_id) queryParams.append('patient_id', params.patient_id)
    if (params?.status) queryParams.append('status', params.status)
    if (params?.page) queryParams.append('page', params.page.toString())

    const query = queryParams.toString()
    return apiService.get<Invoice[]>(
      `/finance/invoices${query ? `?${query}` : ''}`
    )
  }

  async issueInvoice(id: string): Promise<Invoice> {
    return apiService.post<Invoice>(`/finance/invoices/${id}/issue`)
  }

  // Payment methods
  async createPayment(data: PaymentCreateRequest): Promise<Payment> {
    return apiService.post<Payment>('/finance/payments', data)
  }

  async getPayment(id: string): Promise<Payment> {
    return apiService.get<Payment>(`/finance/payments/${id}`)
  }

  async listPayments(params?: {
    invoice_id?: string
    page?: number
  }): Promise<Payment[]> {
    const queryParams = new URLSearchParams()
    if (params?.invoice_id) queryParams.append('invoice_id', params.invoice_id)
    if (params?.page) queryParams.append('page', params.page.toString())

    const query = queryParams.toString()
    return apiService.get<Payment[]>(
      `/finance/payments${query ? `?${query}` : ''}`
    )
  }

  // Insurance methods
  async createInsurance(data: InsuranceCreateRequest): Promise<Insurance> {
    return apiService.post<Insurance>('/finance/insurance', data)
  }

  async getInsurance(id: string): Promise<Insurance> {
    return apiService.get<Insurance>(`/finance/insurance/${id}`)
  }

  async listInsurance(params?: {
    patient_id?: string
    is_active?: boolean
  }): Promise<Insurance[]> {
    const queryParams = new URLSearchParams()
    if (params?.patient_id) queryParams.append('patient_id', params.patient_id)
    if (params?.is_active !== undefined)
      queryParams.append('is_active', params.is_active.toString())

    const query = queryParams.toString()
    return apiService.get<Insurance[]>(
      `/finance/insurance${query ? `?${query}` : ''}`
    )
  }
}

export const financeService = new FinanceService()
