/**
 * App Layout
 *
 * Sidebar (role-based menus) + header + content. Sidebar is toggleable.
 */

import { ReactNode, useState } from 'react'
import { useNavigate, NavLink } from 'react-router-dom'
import { LogOut, User, PanelLeftClose, PanelLeft } from 'lucide-react'
import { useAuth } from '@/hooks/useAuth'
import { Button } from '@/components/ui/button'
import { glassmorphism } from '@/lib/glassmorphism'
import { cn } from '@/lib/utils'
import { getVisibleMenuItems } from '@/config/sidebar-menu'

interface AppLayoutProps {
  children: ReactNode
}

export function AppLayout({ children }: AppLayoutProps) {
  const { user, logout, featureAccess } = useAuth()
  const navigate = useNavigate()
  const [sidebarCollapsed, setSidebarCollapsed] = useState(false)
  const menuItems = getVisibleMenuItems(user?.role_names ?? [], featureAccess ?? null)

  const handleLogout = () => {
    logout()
    navigate('/login', { replace: true })
  }

  return (
    <div className="min-h-screen bg-slate-950 flex">
      {/* Sidebar - header height matches main header for aligned bottom border */}
      <aside
        className={cn(
          glassmorphism('dark', false, false),
          'border-r border-slate-700/50 flex flex-col fixed left-0 top-0 h-screen z-40 transition-[width] duration-300 ease-in-out overflow-hidden',
          sidebarCollapsed ? 'w-16' : 'w-64'
        )}
      >
        <div className={cn('border-b border-slate-700/50 shrink-0 flex items-center h-14', sidebarCollapsed ? 'justify-center p-2' : 'px-4')}>
          {!sidebarCollapsed && (
            <h2 className="text-lg font-semibold text-slate-200 whitespace-nowrap">
              Clinic Management
            </h2>
          )}
          {sidebarCollapsed && (
            <span className="text-xs font-semibold text-slate-200">CM</span>
          )}
        </div>
        <nav className="flex-1 overflow-y-auto py-4">
          <ul className="space-y-0.5 px-2">
            {menuItems.map((item) => {
              const Icon = item.icon
              return (
                <li key={item.key}>
                  <NavLink
                    to={item.path}
                    end={item.path === '/dashboard'}
                    title={sidebarCollapsed ? item.label : undefined}
                    className={({ isActive }) =>
                      cn(
                        'flex items-center rounded-lg text-sm transition-colors',
                        sidebarCollapsed ? 'justify-center p-2.5' : 'gap-3 px-3 py-2.5',
                        isActive
                          ? 'bg-slate-700/50 text-slate-100 font-medium'
                          : 'text-slate-400 hover:bg-slate-800/50 hover:text-slate-200'
                      )
                    }
                  >
                    <Icon className="w-5 h-5 shrink-0" />
                    {!sidebarCollapsed && <span className="whitespace-nowrap">{item.label}</span>}
                  </NavLink>
                </li>
              )
            })}
          </ul>
        </nav>
      </aside>

      {/* Main area: header + content */}
      <div
        className={cn(
          'flex-1 flex flex-col min-h-screen transition-[margin-left] duration-300 ease-in-out',
          sidebarCollapsed ? 'ml-16' : 'ml-64'
        )}
      >
        <header
          className={cn(
            glassmorphism('dark', false, false),
            'border-b border-slate-700/50 sticky top-0 z-30 h-14 flex items-center'
          )}
        >
          <div className="w-full px-6 flex items-center justify-between">
            <div className="flex items-center gap-4 min-w-0">
              <Button
                variant="ghost"
                size="icon"
                onClick={() => setSidebarCollapsed((c) => !c)}
                title={sidebarCollapsed ? 'Expand sidebar' : 'Collapse sidebar'}
                className="shrink-0"
              >
                {sidebarCollapsed ? (
                  <PanelLeft className="w-5 h-5" />
                ) : (
                  <PanelLeftClose className="w-5 h-5" />
                )}
              </Button>
              <span className="text-muted-foreground text-sm truncate">
                {user?.primary_clinic_name || 'Clinic Management'}
              </span>
            </div>
            <div className="flex items-center gap-4">
              {user && (
                <div className="flex items-center gap-2 text-sm">
                  <User className="w-4 h-4" />
                  <span className="text-muted-foreground">
                    {user.first_name} {user.last_name}
                  </span>
                  <span className="px-2 py-1 rounded bg-slate-700/50 text-slate-200 text-xs font-medium">
                    {user.role_names?.[0] ?? 'USER'}
                  </span>
                </div>
              )}
              <Button variant="ghost" size="sm" onClick={handleLogout} className="gap-2">
                <LogOut className="w-4 h-4" />
                Logout
              </Button>
            </div>
          </div>
        </header>

        <main className="flex-1 p-6">{children}</main>
      </div>
    </div>
  )
}
