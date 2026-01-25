import { ReactNode } from 'react'

interface BaseLayoutProps {
  children: ReactNode
}

export function BaseLayout({ children }: BaseLayoutProps) {
  return (
    <div className="min-h-screen bg-background text-foreground">
      <div className="container mx-auto px-4 py-8">
        {children}
      </div>
    </div>
  )
}
