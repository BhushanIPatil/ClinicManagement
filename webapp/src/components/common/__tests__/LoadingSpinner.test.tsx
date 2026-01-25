/**
 * Tests for LoadingSpinner component
 */

import { describe, it, expect } from 'vitest'
import { render, screen } from '@/test/utils/test-utils'
import { LoadingSpinner } from '../LoadingSpinner'

describe('LoadingSpinner', () => {
  it('renders loading spinner', () => {
    render(<LoadingSpinner />)
    const spinner = screen.getByRole('status', { hidden: true })
    expect(spinner).toBeInTheDocument()
  })

  it('displays text when provided', () => {
    render(<LoadingSpinner text="Loading data..." />)
    expect(screen.getByText('Loading data...')).toBeInTheDocument()
  })

  it('applies correct size classes', () => {
    const { container } = render(<LoadingSpinner size="lg" />)
    const spinner = container.querySelector('.w-12')
    expect(spinner).toBeInTheDocument()
  })
})
