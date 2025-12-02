import { describe, it, expect, vi } from 'vitest'
import { render, screen } from '@testing-library/react'
import { Sidebar } from '../layout/Sidebar'

// Mock Next.js router
vi.mock('next/navigation', () => ({
  usePathname: () => '/dashboard'
}))

describe('Sidebar', () => {
  it('renders navigation items', () => {
    render(<Sidebar />)
    
    expect(screen.getByText('Dashboard')).toBeInTheDocument()
    expect(screen.getByText('Batches')).toBeInTheDocument()
    expect(screen.getByText('Analytics')).toBeInTheDocument()
  })

  it('shows logout button', () => {
    render(<Sidebar />)
    expect(screen.getByText('Logout')).toBeInTheDocument()
  })
})