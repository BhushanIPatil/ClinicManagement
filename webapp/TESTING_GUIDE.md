# Frontend Testing Guide

## Test Setup

### Vitest Configuration
- Test framework: Vitest
- Test environment: jsdom
- Coverage: v8 provider
- Setup file: `src/test/setup.ts`

## Running Tests

```bash
# Run all tests
npm test

# Run in watch mode
npm test -- --watch

# Run with UI
npm run test:ui

# Run with coverage
npm run test:coverage
```

## Test Structure

```
src/
├── test/
│   ├── setup.ts              # Global test setup
│   ├── utils/
│   │   └── test-utils.tsx    # Custom render with providers
│   └── mocks/
│       └── handlers.ts       # MSW request handlers
├── components/
│   └── **/__tests__/         # Component tests
└── hooks/
    └── __tests__/            # Hook tests
```

## Writing Tests

### Component Tests

```tsx
import { describe, it, expect } from 'vitest'
import { render, screen } from '@/test/utils/test-utils'
import { LoadingSpinner } from '../LoadingSpinner'

describe('LoadingSpinner', () => {
  it('renders loading spinner', () => {
    render(<LoadingSpinner />)
    expect(screen.getByRole('status')).toBeInTheDocument()
  })
})
```

### Hook Tests

```tsx
import { renderHook, waitFor } from '@testing-library/react'
import { useAppointments } from '../useAppointments'

describe('useAppointments', () => {
  it('fetches appointments', async () => {
    const { result } = renderHook(() => useAppointments())
    
    await waitFor(() => {
      expect(result.current.loading).toBe(false)
    })
    
    expect(result.current.appointments).toBeDefined()
  })
})
```

### Service Tests

```tsx
import { describe, it, expect, vi } from 'vitest'
import { appointmentService } from '@/services/appointment.service'

vi.mock('@/services/appointment.service')

describe('AppointmentService', () => {
  it('books appointment', async () => {
    const mockAppointment = { id: '1', ... }
    vi.mocked(appointmentService.bookAppointment).mockResolvedValue(mockAppointment)
    
    const result = await appointmentService.bookAppointment({...})
    expect(result).toEqual(mockAppointment)
  })
})
```

## Mocking

### API Mocking (MSW)

```tsx
import { http, HttpResponse } from 'msw'

export const handlers = [
  http.get('/api/v1/appointments', () => {
    return HttpResponse.json([...])
  }),
]
```

### Service Mocking

```tsx
vi.mock('@/services/appointment.service', () => ({
  appointmentService: {
    listAppointments: vi.fn(),
    bookAppointment: vi.fn(),
  },
}))
```

## Best Practices

1. **Test Behavior, Not Implementation**
   - Test what users see/do
   - Don't test internal state

2. **Use Queries Wisely**
   - Prefer `getByRole` over `getByTestId`
   - Use semantic queries

3. **Async Testing**
   - Use `waitFor` for async operations
   - Use `findBy` queries

4. **Isolation**
   - Each test should be independent
   - Clean up after tests

5. **Coverage**
   - Aim for >80% coverage
   - Focus on critical paths

## Test Examples

See:
- `src/components/common/__tests__/LoadingSpinner.test.tsx`
- `src/hooks/__tests__/useAppointments.test.ts`
