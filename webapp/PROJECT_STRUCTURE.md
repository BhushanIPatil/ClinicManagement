# Project Structure

This document outlines the scalable folder structure for the Clinic Management Webapp.

## Directory Structure

```
webapp/
├── public/                 # Static assets (images, fonts, etc.)
├── src/
│   ├── components/        # React components
│   │   ├── common/        # Shared/common components
│   │   │   ├── Header/
│   │   │   ├── Footer/
│   │   │   ├── Loading/
│   │   │   └── ErrorBoundary/
│   │   ├── features/      # Feature-specific components
│   │   │   ├── dashboard/
│   │   │   ├── appointments/
│   │   │   ├── patients/
│   │   │   └── ...
│   │   ├── layout/        # Layout components
│   │   │   ├── BaseLayout/
│   │   │   ├── AppLayout/
│   │   │   └── AuthLayout/
│   │   ├── theme/         # Theme-related components
│   │   │   ├── ThemeProvider/
│   │   │   └── ThemeToggle/
│   │   └── ui/            # ShadCN UI components
│   │       ├── button.tsx
│   │       ├── input.tsx
│   │       ├── card.tsx
│   │       └── ...
│   ├── hooks/             # Custom React hooks
│   │   ├── useAuth.ts
│   │   ├── useApi.ts
│   │   └── ...
│   ├── lib/               # Utility functions
│   │   ├── utils.ts
│   │   ├── api.ts
│   │   └── ...
│   ├── services/           # API services
│   │   ├── auth.service.ts
│   │   ├── dashboard.service.ts
│   │   ├── appointments.service.ts
│   │   └── ...
│   ├── stores/            # State management
│   │   ├── auth.store.ts
│   │   ├── ui.store.ts
│   │   └── ...
│   ├── types/             # TypeScript type definitions
│   │   ├── api.types.ts
│   │   ├── dashboard.types.ts
│   │   └── ...
│   ├── App.tsx            # Root component
│   ├── main.tsx           # Entry point
│   └── index.css          # Global styles
├── index.html
├── package.json
├── tsconfig.json
├── vite.config.ts
└── tailwind.config.js
```

## Component Organization

### Common Components (`components/common/`)

Reusable components used across multiple features:
- Header, Footer, Navigation
- Loading spinners, Error boundaries
- Modals, Dialogs
- Form elements (when not from UI library)

### Feature Components (`components/features/`)

Business logic components organized by feature:
- Each feature has its own folder
- Contains feature-specific components
- May include sub-components, hooks, and types

Example:
```
components/features/dashboard/
├── DashboardStats.tsx
├── DashboardChart.tsx
├── RecentAppointments.tsx
└── index.ts
```

### Layout Components (`components/layout/`)

Page structure components:
- BaseLayout: Basic page wrapper
- AppLayout: Main app layout with sidebar/nav
- AuthLayout: Authentication pages layout

### UI Components (`components/ui/`)

ShadCN UI primitives:
- Low-level, reusable components
- Follow ShadCN UI patterns
- Use variants for different styles

## File Naming Conventions

- **Components**: PascalCase (e.g., `DashboardStats.tsx`)
- **Hooks**: camelCase with `use` prefix (e.g., `useAuth.ts`)
- **Services**: camelCase with `.service.ts` suffix (e.g., `auth.service.ts`)
- **Types**: camelCase with `.types.ts` suffix (e.g., `api.types.ts`)
- **Utils**: camelCase (e.g., `utils.ts`, `formatDate.ts`)

## Import Patterns

### Path Aliases

Use `@/` prefix for imports from `src/`:

```typescript
// ✅ Good
import { Button } from '@/components/ui/button'
import { useAuth } from '@/hooks/useAuth'
import { cn } from '@/lib/utils'

// ❌ Bad
import { Button } from '../../../components/ui/button'
```

### Component Imports

```typescript
// Named exports preferred
import { DashboardStats } from '@/components/features/dashboard'

// Default exports for pages/routes only
import DashboardPage from '@/pages/Dashboard'
```

## Scalability Guidelines

### Adding New Features

1. Create feature folder in `components/features/`
2. Add service in `services/`
3. Add types in `types/`
4. Create hooks if needed in `hooks/`
5. Add store slice if state management needed

### Component Size

- Keep components focused and small (< 300 lines)
- Extract sub-components when component grows
- Use composition over large monolithic components

### State Management

- Local state: `useState`, `useReducer`
- Shared state: Zustand/Redux Toolkit stores
- Server state: React Query/SWR
- Form state: React Hook Form

## Best Practices

1. **Component Structure**: One component per file
2. **Exports**: Use index.ts files for clean imports
3. **Types**: Define types close to where they're used
4. **Styling**: Use Tailwind classes, avoid inline styles
5. **Performance**: Use React.memo, useMemo, useCallback appropriately
6. **Testing**: Co-locate tests with components when possible
