import { cn } from './utils'

/**
 * Glassmorphism utility classes
 */
export const glassStyles = {
  base: 'backdrop-blur-sm bg-opacity-5 border border-slate-700/40',
  light: 'bg-white/5',
  dark: 'bg-slate-900/60',
  hover: 'hover:bg-opacity-10 hover:border-slate-600/50 transition-all duration-200',
  glow: '',
}

/**
 * Apply glassmorphism effect to an element
 */
export function glassmorphism(
  variant: 'light' | 'dark' = 'dark',
  withHover = false,
  withGlow = false
) {
  return cn(
    glassStyles.base,
    variant === 'light' ? glassStyles.light : glassStyles.dark,
    withHover && glassStyles.hover,
    withGlow && glassStyles.glow
  )
}
