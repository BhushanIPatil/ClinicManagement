/**
 * Client-side payslip and invoice generation for download/print.
 * No server storage; generates HTML and opens print dialog (user can Save as PDF).
 */

import type { PayrollRosterItem, PayslipItem } from '@/types/payroll.types'

function formatDate(s: string | null | undefined): string {
  if (!s) return '—'
  try {
    return new Date(s).toLocaleDateString(undefined, { dateStyle: 'medium' })
  } catch {
    return String(s)
  }
}

function formatMoney(n: number | null | undefined): string {
  if (n == null) return '—'
  return new Intl.NumberFormat(undefined, { style: 'currency', currency: 'USD' }).format(n)
}

/** Build payslip HTML for a roster entry or payslip. */
export function buildPayslipHtml(
  data: Pick<
    PayrollRosterItem | PayslipItem,
    'user_name' | 'joining_date' | 'role' | 'base_salary' | 'gross_salary' | 'net_salary'
  > & { period_start?: string; period_end?: string; payslip_number?: string }
): string {
  const title = 'Payslip'
  const period =
    data.period_start && data.period_end
      ? `${formatDate(data.period_start)} – ${formatDate(data.period_end)}`
      : '—'
  return `
<!DOCTYPE html>
<html>
<head>
  <meta charset="utf-8">
  <title>${title}</title>
  <style>
    body { font-family: system-ui, sans-serif; max-width: 480px; margin: 24px auto; padding: 16px; color: #1a1a1a; }
    h1 { font-size: 1.25rem; margin-bottom: 8px; }
    .meta { color: #666; font-size: 0.875rem; margin-bottom: 20px; }
    table { width: 100%; border-collapse: collapse; }
    th, td { text-align: left; padding: 8px 0; border-bottom: 1px solid #eee; }
    th { font-weight: 600; color: #444; }
    .total { font-weight: 700; font-size: 1.1rem; }
    @media print { body { margin: 12px; } }
  </style>
</head>
<body>
  <h1>${title}</h1>
  <div class="meta">
    ${data.payslip_number ? `Payslip #${data.payslip_number}<br>` : ''}
    Period: ${period}
  </div>
  <table>
    <tr><th>Employee</th><td>${data.user_name ?? '—'}</td></tr>
    <tr><th>Role</th><td>${data.role ?? '—'}</td></tr>
    <tr><th>Joining date</th><td>${formatDate(data.joining_date)}</td></tr>
    <tr><th>Base salary</th><td>${formatMoney(data.base_salary ?? 0)}</td></tr>
    <tr><th>Gross salary</th><td>${formatMoney(data.gross_salary ?? 0)}</td></tr>
    <tr><th>Net salary</th><td class="total">${formatMoney(data.net_salary ?? 0)}</td></tr>
  </table>
</body>
</html>
  `.trim()
}

/** Build invoice HTML (same data, different title). */
export function buildInvoiceHtml(
  data: Pick<
    PayrollRosterItem | PayslipItem,
    'user_name' | 'joining_date' | 'role' | 'base_salary' | 'gross_salary' | 'net_salary'
  > & { period_start?: string; period_end?: string; payslip_number?: string }
): string {
  const html = buildPayslipHtml(data)
  return html.replace('<title>Payslip</title>', '<title>Payroll Invoice</title>').replace('<h1>Payslip</h1>', '<h1>Payroll Invoice</h1>')
}

/** Open HTML in new window and trigger print (user can Save as PDF). */
export function printPayslip(html: string): void {
  const w = window.open('', '_blank')
  if (!w) {
    console.error('Popup blocked')
    return
  }
  w.document.write(html)
  w.document.close()
  w.focus()
  setTimeout(() => {
    w.print()
    w.onafterprint = () => w.close()
  }, 300)
}

/** Download HTML as file (alternative to print). */
export function downloadPayslipAsFile(html: string, filename: string): void {
  const blob = new Blob([html], { type: 'text/html;charset=utf-8' })
  const url = URL.createObjectURL(blob)
  const a = document.createElement('a')
  a.href = url
  a.download = filename
  a.click()
  URL.revokeObjectURL(url)
}
