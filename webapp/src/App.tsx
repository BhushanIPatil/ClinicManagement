import { BrowserRouter, Routes, Route, Navigate } from 'react-router-dom'
import { ThemeProvider } from './components/theme/theme-provider'
import { AuthProvider } from './stores/auth.store'
import { ProtectedRoute } from './components/auth/ProtectedRoute'
import { RoleRoute } from './components/auth/RoleRoute'
import { AppLayout } from './components/layout/AppLayout'
import Dashboard from './pages/Dashboard'
import Login from './pages/Login'
import Unauthorized from './pages/Unauthorized'
import SuperAdminClinics from './pages/SuperAdminClinics'
import SuperAdminOnboard from './pages/SuperAdminOnboard'
import AppointmentsPage from './pages/AppointmentsPage'
import WorkQueuePage from './pages/WorkQueuePage'
import PlaceholderPage from './pages/PlaceholderPage'
import UsersPage from './pages/UsersPage'
import ClinicAdminAddEmployee from './pages/ClinicAdminAddEmployee'

function App() {
  return (
    <ThemeProvider defaultTheme="dark" storageKey="clinic-ui-theme">
      <AuthProvider>
        <BrowserRouter>
          <Routes>
            <Route path="/login" element={<Login />} />
            <Route path="/unauthorized" element={<Unauthorized />} />

            <Route
              path="/dashboard"
              element={
                <ProtectedRoute>
                  <AppLayout>
                    <Dashboard />
                  </AppLayout>
                </ProtectedRoute>
              }
            />

            {/* Super Admin: clinics count, list, users, onboard */}
            <Route
              path="/super-admin/clinics"
              element={
                <RoleRoute requiredRoles="SUPER_ADMIN">
                  <AppLayout>
                    <SuperAdminClinics />
                  </AppLayout>
                </RoleRoute>
              }
            />
            <Route
              path="/super-admin/onboard"
              element={
                <RoleRoute requiredRoles="SUPER_ADMIN">
                  <AppLayout>
                    <SuperAdminOnboard />
                  </AppLayout>
                </RoleRoute>
              }
            />

            {/* Users: list + Add User (same as add employee); CLINIC_ADMIN only */}
            <Route
              path="/users"
              element={
                <RoleRoute requiredRoles="CLINIC_ADMIN">
                  <AppLayout>
                    <UsersPage />
                  </AppLayout>
                </RoleRoute>
              }
            />
            <Route
              path="/users/add"
              element={
                <RoleRoute requiredRoles="CLINIC_ADMIN">
                  <AppLayout>
                    <ClinicAdminAddEmployee />
                  </AppLayout>
                </RoleRoute>
              }
            />

            {/* Appointments & Work Queue (CLINIC_ADMIN, RECEPTIONIST) */}
            <Route
              path="/appointments"
              element={
                <ProtectedRoute>
                  <AppLayout>
                    <AppointmentsPage />
                  </AppLayout>
                </ProtectedRoute>
              }
            />
            <Route
              path="/work-queue"
              element={
                <ProtectedRoute>
                  <AppLayout>
                    <WorkQueuePage />
                  </AppLayout>
                </ProtectedRoute>
              }
            />

            {/* Payroll, Finance, KPI, Users – placeholders; protect by role in backend */}
            <Route
              path="/payroll"
              element={
                <ProtectedRoute>
                  <AppLayout>
                    <PlaceholderPage />
                  </AppLayout>
                </ProtectedRoute>
              }
            />
            <Route
              path="/finance"
              element={
                <ProtectedRoute>
                  <AppLayout>
                    <PlaceholderPage />
                  </AppLayout>
                </ProtectedRoute>
              }
            />
            <Route
              path="/kpi"
              element={
                <ProtectedRoute>
                  <AppLayout>
                    <PlaceholderPage />
                  </AppLayout>
                </ProtectedRoute>
              }
            />
            <Route path="/" element={<Navigate to="/dashboard" replace />} />
            <Route path="*" element={<Navigate to="/dashboard" replace />} />
          </Routes>
        </BrowserRouter>
      </AuthProvider>
    </ThemeProvider>
  )
}

export default App
