import { AppointmentsList } from '@/components/features/AppointmentsList'

export default function AppointmentsPage() {
  return (
    <div className="space-y-6">
      <h1 className="text-2xl font-bold">Appointments</h1>
      <AppointmentsList />
    </div>
  )
}
