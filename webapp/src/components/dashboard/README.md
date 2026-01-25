# Dashboard Components

Ultra-modern futuristic dashboard with glassmorphism, animations, and interactive charts.

## Features

- ✨ **Glassmorphism Design** - Frosted glass effect with backdrop blur
- 🎨 **Animated Cards** - Smooth transitions and hover effects
- 📊 **Interactive Charts** - Recharts integration with custom styling
- 📱 **Responsive Grid** - Adapts to all screen sizes
- 🌙 **Dark Theme** - Optimized for dark mode
- ⚡ **Performance** - Optimized animations with Framer Motion

## Components

### KPIWidget

Displays key performance indicators with icons, values, and trend indicators.

```tsx
<KPIWidget
  title="Total Patients"
  value={1250}
  change={12.5}
  trend="up"
  icon={Users}
  delay={0}
/>
```

### ChartCard

Wrapper for chart components with glassmorphism styling.

```tsx
<ChartCard
  title="Revenue Trend"
  description="Weekly revenue and patient visits"
  delay={0.4}
>
  <RevenueChart data={data} />
</ChartCard>
```

### Charts

- **RevenueChart** - Area chart showing revenue trends
- **AppointmentsChart** - Bar chart for scheduled vs completed
- **PatientTrendChart** - Line chart for patient growth

### DashboardGrid & DashboardSection

Responsive grid system for organizing dashboard widgets.

```tsx
<DashboardSection cols={4}>
  <DashboardGrid>
    {/* KPI widgets */}
  </DashboardGrid>
</DashboardSection>
```

## Styling

### Glassmorphism

The `glassmorphism()` utility function applies frosted glass effects:

```tsx
import { glassmorphism } from '@/lib/glassmorphism'

<div className={glassmorphism('dark', true, true)}>
  {/* Content */}
</div>
```

### Animations

- Framer Motion for component animations
- CSS keyframes for background blob animations
- Smooth transitions on hover

## Data Integration

Example data is provided in `@/lib/dashboard-data.ts`. Replace with real API calls:

```tsx
import { fetchDashboardData } from '@/lib/dashboard-data'

const data = await fetchDashboardData()
```

## Customization

### Colors

Modify chart colors in individual chart components:
- Revenue: `#3b82f6` (blue)
- Appointments: `#3b82f6` (scheduled), `#10b981` (completed)
- Patients: `#8b5cf6` (new), `#ec4899` (returning)

### Animations

Adjust animation delays and durations in component props:
- `delay`: Stagger animation start times
- `duration`: Control animation speed

### Grid Layout

Modify grid columns using `DashboardSection`:
- `cols={1}` - Single column
- `cols={2}` - Two columns
- `cols={4}` - Full width
