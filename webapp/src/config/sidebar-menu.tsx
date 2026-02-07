/**
 * Sidebar menu configuration with role-based visibility.
 * User sees only items whose allowedRoles intersect with their roles.
 */

import type { UserRole } from '@/types/auth.types'
import {
  LayoutDashboard,
  Building2,
  Users,
  UserCircle,
  Calendar,
  ListTodo,
  ClipboardList,
  Wallet,
  DollarSign,
  BarChart3,
  UserPlus,
  Settings,
} from 'lucide-react'

export interface SidebarMenuItem {
  key: string
  label: string
  path: string
  icon: React.ComponentType<{ className?: string }>
  /** Roles that can see this item. Empty = everyone. */
  allowedRoles: UserRole[]
}

export const SIDEBAR_MENU: SidebarMenuItem[] = [
  {
    key: 'dashboard',
    label: 'Dashboard',
    path: '/dashboard',
    icon: LayoutDashboard,
    allowedRoles: ['SUPER_ADMIN', 'CLINIC_ADMIN', 'NURSE', 'HR_OPERATIONS', 'RECEPTIONIST', 'DOCTOR'],
  },
  {
    key: 'my-tasks',
    label: 'Your Tasks',
    path: '/my-tasks',
    icon: ClipboardList,
    allowedRoles: ['SUPER_ADMIN', 'CLINIC_ADMIN', 'NURSE', 'HR_OPERATIONS', 'RECEPTIONIST', 'DOCTOR'],
  },
  // Super Admin
  {
    key: 'clinics',
    label: 'Clinics',
    path: '/super-admin/clinics',
    icon: Building2,
    allowedRoles: ['SUPER_ADMIN'],
  },
  {
    key: 'onboard-clinic',
    label: 'Onboard Clinic',
    path: '/super-admin/onboard',
    icon: UserPlus,
    allowedRoles: ['SUPER_ADMIN'],
  },
  // Clinic Admin: users list + Add User (Doctor, Nurse, HR, Receptionist)
  {
    key: 'users',
    label: 'Users',
    path: '/users',
    icon: Users,
    allowedRoles: ['CLINIC_ADMIN'],
  },
  {
    key: 'settings',
    label: 'Settings',
    path: '/settings',
    icon: Settings,
    allowedRoles: ['CLINIC_ADMIN'],
  },
  {
    key: 'patients',
    label: 'Patients',
    path: '/patients',
    icon: UserCircle,
    allowedRoles: ['CLINIC_ADMIN', 'RECEPTIONIST', 'DOCTOR', 'NURSE'],
  },
  {
    key: 'appointments',
    label: 'Appointments',
    path: '/appointments',
    icon: Calendar,
    allowedRoles: ['CLINIC_ADMIN', 'RECEPTIONIST', 'DOCTOR'],
  },
  {
    key: 'work-queue',
    label: 'Work Queue',
    path: '/work-queue',
    icon: ListTodo,
    allowedRoles: ['CLINIC_ADMIN', 'RECEPTIONIST', 'DOCTOR', 'NURSE'],
  },
  {
    key: 'payroll',
    label: 'Payroll',
    path: '/payroll',
    icon: DollarSign,
    allowedRoles: ['CLINIC_ADMIN', 'HR_OPERATIONS', 'DOCTOR'],
  },
  {
    key: 'finance',
    label: 'Finance',
    path: '/finance',
    icon: Wallet,
    allowedRoles: ['CLINIC_ADMIN', 'HR_OPERATIONS', 'DOCTOR', 'NURSE', 'RECEPTIONIST'],
  },
  {
    key: 'kpi',
    label: 'KPI & Targets',
    path: '/kpi',
    icon: BarChart3,
    allowedRoles: ['CLINIC_ADMIN'],
  },
]

/** Map sidebar key to backend feature key (for clinic_settings). */
export const MENU_KEY_TO_FEATURE: Record<string, string> = {
  finance: 'FINANCE',
  patients: 'PATIENTS',
  'work-queue': 'WORK_QUEUE',
  payroll: 'PAYROLL',
}

/**
 * Filter menu items. Access is controlled only by clinic admin settings (no extra role restriction).
 * - Feature-gated items (Patients, Work Queue, Payroll, Finance): show only when featureAccess[featureKey] is true.
 * - Other items (Dashboard, Clinics, Users, Settings, KPI): show when user has one of allowedRoles.
 */
export function getVisibleMenuItems(
  userRoles: string[],
  featureAccess: Record<string, boolean> | null = null
): SidebarMenuItem[] {
  const roles = userRoles.map((r) => r.toUpperCase())
  return SIDEBAR_MENU.filter((item) => {
    const featureKey = MENU_KEY_TO_FEATURE[item.key]
    if (featureKey) {
      return featureAccess != null && Boolean(featureAccess[featureKey])
    }
    if (item.allowedRoles.length === 0) return true
    return item.allowedRoles.some((r) => roles.includes(r.toUpperCase()))
  })
}
