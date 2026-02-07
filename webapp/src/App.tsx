import { Toaster } from 'sonner'
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
import PatientsPage from './pages/PatientsPage'
import WorkQueuePage from './pages/WorkQueuePage'
import MyTasksPage from './pages/MyTasksPage'
import PlaceholderPage from './pages/PlaceholderPage'
import PayrollPage from './pages/PayrollPage'
import UsersPage from './pages/UsersPage'
import ClinicAdminAddEmployee from './pages/ClinicAdminAddEmployee'
import SettingsPage from './pages/SettingsPage'

function App() {
  return (
    <ThemeProvider defaultTheme="dark" storageKey="clinic-ui-theme">
      <Toaster position="top-right" richColors closeButton theme="dark" />
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
            <Route
              path="/settings"
              element={
                <RoleRoute requiredRoles="CLINIC_ADMIN">
                  <AppLayout>
                    <SettingsPage />
                  </AppLayout>
                </RoleRoute>
              }
            />

            {/* Patients: add before setting up appointments */}
            <Route
              path="/patients"
              element={
                <RoleRoute requiredRoles={['CLINIC_ADMIN', 'RECEPTIONIST', 'DOCTOR', 'NURSE']}>
                  <AppLayout>
                    <PatientsPage />
                  </AppLayout>
                </RoleRoute>
              }
            />
            {/* Appointments: CLINIC_ADMIN, RECEPTIONIST, DOCTOR (add & manage); doctor dropdown shows clinic doctors */}
            <Route
              path="/appointments"
              element={
                <RoleRoute requiredRoles={['CLINIC_ADMIN', 'RECEPTIONIST', 'DOCTOR']}>
                  <AppLayout>
                    <AppointmentsPage />
                  </AppLayout>
                </RoleRoute>
              }
            />
            {/* Work Queue: CLINIC_ADMIN, RECEPTIONIST, DOCTOR (my schedule + status/fees), NURSE (patient status) */}
            <Route
              path="/work-queue"
              element={
                <RoleRoute requiredRoles={['CLINIC_ADMIN', 'RECEPTIONIST', 'DOCTOR', 'NURSE']}>
                  <AppLayout>
                    <WorkQueuePage />
                  </AppLayout>
                </RoleRoute>
              }
            />
            {/* Your Tasks: personal tasks, any authenticated user */}
            <Route
              path="/my-tasks"
              element={
                <ProtectedRoute>
                  <AppLayout>
                    <MyTasksPage />
                  </AppLayout>
                </ProtectedRoute>
              }
            />

            {/* Payroll: CLINIC_ADMIN, HR_OPERATIONS, DOCTOR */}
            <Route
              path="/payroll"
              element={
                <RoleRoute requiredRoles={['CLINIC_ADMIN', 'HR_OPERATIONS', 'DOCTOR']}>
                  <AppLayout>
                    <PayrollPage />
                  </AppLayout>
                </RoleRoute>
              }
            />
            {/* Finance: CLINIC_ADMIN, HR_OPERATIONS, DOCTOR, NURSE, RECEPTIONIST (small clinics) */}
            <Route
              path="/finance"
              element={
                <RoleRoute requiredRoles={['CLINIC_ADMIN', 'HR_OPERATIONS', 'DOCTOR', 'NURSE', 'RECEPTIONIST']}>
                  <AppLayout>
                    <PlaceholderPage />
                  </AppLayout>
                </RoleRoute>
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
