# Frontend Integration Guide

Complete integration of frontend with backend modules: Appointments, Patients, Finance, Payroll, and Priority Queue.

## Architecture

### Separation of Concerns

- **Types** (`types/`): TypeScript interfaces matching backend DTOs
- **Services** (`services/`): Pure API communication layer
- **Hooks** (`hooks/`): Data fetching with loading/error states
- **Components** (`components/`): Reusable UI components
- **Features** (`components/features/`): Feature-specific components

## Structure

```
src/
├── types/
│   ├── appointment.types.ts
│   ├── patient.types.ts
│   ├── finance.types.ts
│   ├── payroll.types.ts
│   └── work-queue.types.ts
├── services/
│   ├── appointment.service.ts
│   ├── patient.service.ts
│   ├── finance.service.ts
│   ├── payroll.service.ts
│   └── work-queue.service.ts
├── hooks/
│   ├── useAppointments.ts
│   ├── usePatients.ts
│   └── useWorkQueue.ts
├── components/
│   ├── common/
│   │   ├── LoadingSpinner.tsx
│   │   ├── ErrorMessage.tsx
│   │   ├── EmptyState.tsx
│   │   └── DataTable.tsx
│   └── features/
│       ├── AppointmentsList.tsx
│       ├── PatientsList.tsx
│       └── WorkQueueList.tsx
```

## Reusable Components

### LoadingSpinner
Consistent loading indicator:
```tsx
<LoadingSpinner size="md" text="Loading..." />
```

### ErrorMessage
Error display with dismiss:
```tsx
<ErrorMessage message="Error occurred" onDismiss={() => setError(null)} />
```

### EmptyState
Empty state display:
```tsx
<EmptyState
  icon={<Icon />}
  title="No items"
  description="Description here"
  action={<Button>Action</Button>}
/>
```

### DataTable
Reusable table component:
```tsx
<DataTable
  columns={columns}
  data={items}
  keyExtractor={(item) => item.id}
  emptyMessage="No data"
/>
```

## Services

All services follow the same pattern:
- Pure API communication
- No business logic
- Type-safe with TypeScript
- Error handling via API service

### Example: Appointment Service
```tsx
import { appointmentService } from '@/services/appointment.service'

// Book appointment
const appointment = await appointmentService.bookAppointment({
  patient_id: '...',
  doctor_id: '...',
  appointment_date: '...',
})

// List appointments
const appointments = await appointmentService.listAppointments({
  patient_id: '...',
})
```

## Hooks

Hooks provide:
- Loading states
- Error handling
- Data fetching
- CRUD operations

### Example: useAppointments
```tsx
const { appointments, loading, error, bookAppointment } = useAppointments({
  patientId: '...',
  autoFetch: true,
})

// Book new appointment
await bookAppointment({ ... })
```

## Feature Components

### AppointmentsList
```tsx
<AppointmentsList
  patientId="..."
  doctorId="..."
/>
```

### PatientsList
```tsx
<PatientsList />
```

### WorkQueueList
```tsx
<WorkQueueList
  status="PENDING"
  priority="HIGH"
/>
```

## Usage Examples

### Complete Example: Appointments Page
```tsx
import { AppointmentsList } from '@/components/features'
import { useAppointments } from '@/hooks/useAppointments'
import { Button } from '@/components/ui/button'

function AppointmentsPage() {
  const { bookAppointment, loading } = useAppointments()

  const handleBook = async () => {
    try {
      await bookAppointment({
        patient_id: '...',
        doctor_id: '...',
        appointment_date: '...',
      })
    } catch (err) {
      // Error handled by hook
    }
  }

  return (
    <div>
      <Button onClick={handleBook} disabled={loading}>
        Book Appointment
      </Button>
      <AppointmentsList />
    </div>
  )
}
```

## Error Handling

All components handle errors consistently:
1. Services throw errors
2. Hooks catch and set error state
3. Components display errors via ErrorMessage

## Loading States

Loading is handled at multiple levels:
- Service level (API calls)
- Hook level (data fetching)
- Component level (UI feedback)

## Type Safety

All types match backend DTOs:
- Request types for API calls
- Response types for API responses
- Full TypeScript coverage

## Best Practices

1. **No Business Logic in Components**: All logic in services/hooks
2. **Consistent UI**: Use reusable components
3. **Error Handling**: Always handle errors gracefully
4. **Loading States**: Show loading feedback
5. **Type Safety**: Use TypeScript types throughout

## Next Steps

1. Add more feature components (Finance, Payroll)
2. Add form components for create/update
3. Add pagination to lists
4. Add filtering and sorting
5. Add real-time updates (WebSocket)
