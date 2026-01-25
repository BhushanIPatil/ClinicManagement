import { cn } from './utils'

/**
 * Glassmorphism utility classes
 */
export const glassStyles = {
  base: 'backdrop-blur-xl bg-opacity-10 border border-white/20',
  light: 'bg-white/10',
  dark: 'bg-black/10',
  hover: 'hover:bg-opacity-20 hover:border-white/30 transition-all duration-300',
  glow: 'shadow-[0_8px_32px_0_rgba(31,38,135,0.37)]',
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
