/**
 * App Layout
 *
 * Sidebar (role-based menus) + header + content.
 */

import { ReactNode } from 'react'
import { useNavigate, NavLink } from 'react-router-dom'
import { LogOut, User } from 'lucide-react'
import { useAuth } from '@/hooks/useAuth'
import { Button } from '@/components/ui/button'
import { glassmorphism } from '@/lib/glassmorphism'
import { cn } from '@/lib/utils'
import { getVisibleMenuItems } from '@/config/sidebar-menu'

interface AppLayoutProps {
  children: ReactNode
}

export function AppLayout({ children }: AppLayoutProps) {
  const { user, logout } = useAuth()
  const navigate = useNavigate()
  const menuItems = getVisibleMenuItems(user?.role_names ?? [])

  const handleLogout = () => {
    logout()
    navigate('/login', { replace: true })
  }

  return (
    <div className="min-h-screen bg-gradient-to-br from-slate-900 via-purple-900 to-slate-900 flex">
      {/* Sidebar */}
      <aside
        className={cn(
          glassmorphism('dark', false, true),
          'w-64 border-r border-white/20 flex flex-col fixed left-0 top-0 h-screen z-40'
        )}
      >
        <div className="p-4 border-b border-white/10">
          <h2 className="text-lg font-bold bg-gradient-to-r from-blue-400 to-purple-400 bg-clip-text text-transparent">
            Clinic Management
          </h2>
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
                    className={({ isActive }) =>
                      cn(
                        'flex items-center gap-3 px-3 py-2.5 rounded-lg text-sm transition-colors',
                        isActive
                          ? 'bg-primary/20 text-primary font-medium'
                          : 'text-muted-foreground hover:bg-white/5 hover:text-foreground'
                      )
                    }
                  >
                    <Icon className="w-5 h-5 shrink-0" />
                    {item.label}
                  </NavLink>
                </li>
              )
            })}
          </ul>
        </nav>
      </aside>

      {/* Main area: header + content */}
      <div className="flex-1 flex flex-col min-h-screen ml-64">
        <header
          className={cn(
            glassmorphism('dark', false, true),
            'border-b border-white/20 sticky top-0 z-30'
          )}
        >
          <div className="px-6 py-4 flex items-center justify-between">
            <div className="flex items-center gap-4">
              <span className="text-muted-foreground text-sm">Clinic Management</span>
            </div>
            <div className="flex items-center gap-4">
              {user && (
                <div className="flex items-center gap-2 text-sm">
                  <User className="w-4 h-4" />
                  <span className="text-muted-foreground">
                    {user.first_name} {user.last_name}
                  </span>
                  <span className="px-2 py-1 rounded bg-primary/20 text-primary text-xs">
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
