/**
 * Testing utilities
 * 
 * Custom render function with providers.
 */

import { ReactElement } from 'react'
import { render, RenderOptions } from '@testing-library/react'
import { BrowserRouter } from 'react-router-dom'
import { ThemeProvider } from '@/components/theme/theme-provider'
import { AuthProvider } from '@/stores/auth.store'

interface CustomRenderOptions extends Omit<RenderOptions, 'wrapper'> {
  initialAuthState?: {
    user?: any
    isAuthenticated?: boolean
  }
}

const AllTheProviders = ({ children, initialAuthState }: { children: React.ReactNode, initialAuthState?: any }) => {
  return (
    <BrowserRouter>
      <ThemeProvider defaultTheme="dark">
        <AuthProvider>
          {children}
        </AuthProvider>
      </ThemeProvider>
    </BrowserRouter>
  )
}

const customRender = (
  ui: ReactElement,
  options: CustomRenderOptions = {}
) => {
  const { initialAuthState, ...renderOptions } = options
  
  return render(ui, {
    wrapper: (props) => (
      <AllTheProviders {...props} initialAuthState={initialAuthState} />
    ),
    ...renderOptions,
  })
}

export * from '@testing-library/react'
export { customRender as render }
