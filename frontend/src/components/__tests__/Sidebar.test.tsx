import { describe, it, expect, vi } from 'vitest'
import { fireEvent, render, screen } from '@testing-library/react'
import { Sidebar } from '../layout/Sidebar'
import { I18nProvider } from '@/lib/i18n'

// Mock Next.js router
vi.mock('next/navigation', () => ({
  usePathname: () => '/dashboard',
  useRouter: () => ({ push: vi.fn() }),
}))

describe('Sidebar', () => {
  it('renders navigation items including Sri Lankan MVP sections', () => {
    render(
      <I18nProvider>
        <Sidebar />
      </I18nProvider>
    )

    expect(screen.getByText('Dashboard')).toBeInTheDocument()
    expect(screen.getByText('Batches')).toBeInTheDocument()
    expect(screen.getByText('Profit & Costs (LKR)')).toBeInTheDocument()
    expect(screen.getByText('Buyers & Sales')).toBeInTheDocument()
    expect(screen.getByText('Analytics')).toBeInTheDocument()
  })

  it('switches navigation labels between English, Sinhala, and Tamil', () => {
    render(
      <I18nProvider>
        <Sidebar />
      </I18nProvider>
    )

    fireEvent.click(screen.getByText('සිං'))
    expect(screen.getByText('ප්‍රධාන පුවරුව')).toBeInTheDocument()

    fireEvent.click(screen.getByText('தமிழ்'))
    expect(screen.getByText('முகப்புப் பலகை')).toBeInTheDocument()
  })

  it('shows logout button', () => {
    render(
      <I18nProvider>
        <Sidebar />
      </I18nProvider>
    )
    expect(screen.getByText('Logout')).toBeInTheDocument()
  })
})
