# Clinic Management Webapp

Frontend application for the Clinic Management System built with modern React stack.

## Tech Stack

- **Vite** - Fast build tool and dev server
- **React 18** - UI library
- **TypeScript** - Type safety
- **Tailwind CSS** - Utility-first CSS framework
- **ShadCN UI** - High-quality component library
- **Dark Mode** - Enabled by default

## Project Structure

```
webapp/
├── src/
│   ├── components/          # React components
│   │   ├── common/          # Shared/common components
│   │   ├── features/        # Feature-specific components
│   │   ├── layout/          # Layout components
│   │   ├── theme/           # Theme provider and utilities
│   │   └── ui/              # ShadCN UI components
│   ├── lib/                 # Utility functions
│   ├── hooks/               # Custom React hooks
│   ├── services/            # API services
│   ├── stores/              # State management
│   ├── types/               # TypeScript types
│   ├── App.tsx              # Root component
│   ├── main.tsx             # Entry point
│   └── index.css            # Global styles
├── public/                   # Static assets
├── index.html               # HTML template
├── package.json
├── tsconfig.json
├── vite.config.ts
└── tailwind.config.js
```

## Getting Started

### Prerequisites

- Node.js 18+
- npm or yarn

### Installation

```bash
# Install dependencies
npm install

# Start development server
npm run dev

# Build for production
npm run build

# Preview production build
npm run preview
```

## Features

### Dark Mode

Dark mode is enabled by default. The theme system uses:
- CSS variables for theming
- LocalStorage for persistence
- System preference detection

### ShadCN UI

ShadCN UI components are available in `src/components/ui/`. To add more components:

1. Visit [shadcn/ui](https://ui.shadcn.com)
2. Copy component code
3. Place in `src/components/ui/`
4. Export from `src/components/ui/index.ts`

### Path Aliases

Use `@/` prefix for imports from `src/`:

```typescript
import { Button } from '@/components/ui/button'
import { cn } from '@/lib/utils'
```

## Development Guidelines

### Component Organization

- **Common components**: Reusable UI elements (buttons, inputs, cards)
- **Feature components**: Business logic components (dashboard, appointments)
- **Layout components**: Page structure (header, sidebar, footer)
- **UI components**: ShadCN UI primitives

### Styling

- Use Tailwind CSS utility classes
- Use `cn()` utility for conditional classes
- Follow ShadCN UI patterns for component variants

### TypeScript

- Define types in `src/types/`
- Use strict TypeScript settings
- Avoid `any` types

## Next Steps

- [ ] Add routing (React Router)
- [ ] Set up API client
- [ ] Add state management (Zustand/Redux Toolkit)
- [ ] Implement authentication
- [ ] Add form handling (React Hook Form)
- [ ] Set up testing (Vitest + React Testing Library)
