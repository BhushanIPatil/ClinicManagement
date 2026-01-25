/**
 * Sidebar menu configuration with role-based visibility.
 * User sees only items whose allowedRoles intersect with their roles.
 */

import type { UserRole } from '@/types/auth.types'
import {
  LayoutDashboard,
  Building2,
  Users,
  Calendar,
  ListTodo,
  Wallet,
  DollarSign,
  BarChart3,
  UserPlus,
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
    allowedRoles: ['SUPER_ADMIN', 'CLINIC_ADMIN', 'NURSE', 'HR_OPERATIONS', 'RECEPTIONIST'],
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
    key: 'appointments',
    label: 'Appointments',
    path: '/appointments',
    icon: Calendar,
    allowedRoles: ['CLINIC_ADMIN', 'RECEPTIONIST'],
  },
  {
    key: 'work-queue',
    label: 'Work Queue',
    path: '/work-queue',
    icon: ListTodo,
    allowedRoles: ['CLINIC_ADMIN', 'RECEPTIONIST'],
  },
  {
    key: 'payroll',
    label: 'Payroll',
    path: '/payroll',
    icon: DollarSign,
    allowedRoles: ['CLINIC_ADMIN', 'HR_OPERATIONS'],
  },
  {
    key: 'finance',
    label: 'Finance',
    path: '/finance',
    icon: Wallet,
    allowedRoles: ['CLINIC_ADMIN', 'HR_OPERATIONS'],
  },
  {
    key: 'kpi',
    label: 'KPI & Targets',
    path: '/kpi',
    icon: BarChart3,
    allowedRoles: ['CLINIC_ADMIN'],
  },
]

/**
 * Filter menu items by user roles. User sees only items they are allowed to access.
 */
export function getVisibleMenuItems(userRoles: string[]): SidebarMenuItem[] {
  const roles = userRoles.map((r) => r.toUpperCase())
  return SIDEBAR_MENU.filter((item) => {
    if (item.allowedRoles.length === 0) return true
    return item.allowedRoles.some((r) => roles.includes(r.toUpperCase()))
  })
}
