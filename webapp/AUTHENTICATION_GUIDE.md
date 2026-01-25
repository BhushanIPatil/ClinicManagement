# Authentication Integration Guide

Complete authentication system with service layer, hooks, and protected routes.

## Architecture

### Separation of Concerns

- **Services** (`services/`): Pure API communication
- **Stores** (`stores/`): State management
- **Hooks** (`hooks/`): Reusable authentication logic
- **Components** (`components/auth/`): UI components (no business logic)

## Components

### Services

#### `api.service.ts`
Base API client with:
- Automatic token injection
- Token refresh on 401 errors
- Error handling
- Request/response interceptors

#### `auth.service.ts`
Authentication-specific API calls:
- `login()` - User login
- `register()` - User registration
- `logout()` - Clear tokens
- `refreshToken()` - Refresh access token
- `getCurrentUser()` - Fetch current user

### State Management

#### `auth.store.ts`
React Context-based auth store:
- User state
- Authentication status
- Loading states
- Error handling
- Auto-initialization from storage

### Hooks

#### `useAuth()`
Main authentication hook:
```tsx
const { user, isAuthenticated, login, logout } = useAuth()
```

#### `useRequireAuth()`
Redirects to login if not authenticated:
```tsx
function MyComponent() {
  useRequireAuth() // Auto-redirects if not logged in
  // Component code
}
```

#### `useRequireRole()`
Checks user roles:
```tsx
function AdminComponent() {
  useRequireRole('ADMIN') // Auto-redirects if not admin
  // Component code
}
```

### Components

#### `ProtectedRoute`
Wraps routes requiring authentication:
```tsx
<ProtectedRoute>
  <Dashboard />
</ProtectedRoute>
```

#### `RoleRoute`
Wraps routes requiring specific roles:
```tsx
<RoleRoute requiredRoles={['ADMIN', 'HR']}>
  <AdminPanel />
</RoleRoute>
```

#### `LoginForm`
Login form component (no auth logic):
- Form validation
- Error display
- Loading states
- Uses `useAuth()` hook

## Token Storage

Tokens are stored in localStorage:
- `clinic_access_token` - JWT access token
- `clinic_refresh_token` - JWT refresh token
- `clinic_user` - User data

### Security Notes

- Tokens stored in localStorage (consider httpOnly cookies for production)
- Automatic token refresh on 401 errors
- Tokens cleared on logout
- Token validation on app initialization

## Usage Examples

### Login
```tsx
import { useAuth } from '@/hooks/useAuth'

function LoginComponent() {
  const { login, isLoading, error } = useAuth()

  const handleLogin = async () => {
    try {
      await login({ username: 'user', password: 'pass' })
      // Redirect handled by router
    } catch (err) {
      // Error handled by store
    }
  }
}
```

### Protected Component
```tsx
import { useAuth } from '@/hooks/useAuth'

function Dashboard() {
  const { user, isAuthenticated } = useAuth()

  if (!isAuthenticated) return null

  return <div>Welcome, {user?.first_name}</div>
}
```

### Role-Based Access
```tsx
import { useRequireRole } from '@/hooks/useRequireRole'

function AdminPanel() {
  useRequireRole('ADMIN')
  // Component only renders if user is admin
  return <div>Admin Content</div>
}
```

## API Integration

### Endpoints Used

- `POST /auth/login` - User login
- `POST /auth/register` - User registration
- `POST /auth/refresh` - Refresh token
- `GET /auth/me` - Get current user

### Request/Response Format

**Login Request:**
```json
{
  "username": "user@example.com",
  "password": "password123"
}
```

**Login Response:**
```json
{
  "user": {
    "id": "uuid",
    "email": "user@example.com",
    "username": "username",
    "first_name": "John",
    "last_name": "Doe",
    "role_names": ["DOCTOR"],
    "is_active": true
  },
  "tokens": {
    "access_token": "jwt_token",
    "refresh_token": "refresh_token",
    "token_type": "bearer"
  }
}
```

## Routing

Routes are configured in `App.tsx`:

```tsx
<Routes>
  <Route path="/login" element={<Login />} />
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
  <Route
    path="/admin/*"
    element={
      <RoleRoute requiredRoles="ADMIN">
        <AppLayout>
          <AdminPanel />
        </AppLayout>
      </RoleRoute>
    }
  />
</Routes>
```

## Error Handling

- API errors are caught and displayed
- 401 errors trigger token refresh
- Failed refresh clears auth and redirects to login
- User-friendly error messages

## Best Practices

1. **No Auth Logic in Components**: All logic in services/hooks
2. **Centralized State**: Single source of truth in auth store
3. **Type Safety**: Full TypeScript coverage
4. **Error Handling**: Comprehensive error management
5. **Token Management**: Automatic refresh and cleanup

## Environment Variables

Create `.env` file:
```
VITE_API_BASE_URL=http://localhost:8000/api/v1
```

## Testing

Mock the auth service for testing:
```tsx
jest.mock('@/services/auth.service', () => ({
  authService: {
    login: jest.fn(),
    logout: jest.fn(),
  }
}))
```
