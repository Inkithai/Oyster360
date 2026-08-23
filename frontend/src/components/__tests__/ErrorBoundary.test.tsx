import { render, screen } from '@testing-library/react'
import { beforeEach, describe, expect, it, vi } from 'vitest'

import { ErrorBoundary } from '../ErrorBoundary'
import { reportError } from '@/lib/logger'

const { reportSpy } = vi.hoisted(() => ({ reportSpy: vi.fn() }))

vi.mock('@/lib/logger', () => ({
  reportError: (...args: unknown[]) => reportSpy(...args),
}))

vi.mocked(reportError)

function Exploder(): never {
  throw new Error('render exploded')
}

describe('ErrorBoundary', () => {
  beforeEach(() => {
    reportSpy.mockReset()
    vi.spyOn(console, 'error').mockImplementation(() => {})
  })

  it('renders children when nothing throws', () => {
    render(
      <ErrorBoundary>
        <p>safe content</p>
      </ErrorBoundary>,
    )

    expect(screen.getByText('safe content')).toBeInTheDocument()
    expect(reportSpy).not.toHaveBeenCalled()
  })

  it('shows the fallback and reports when a child throws', () => {
    render(
      <ErrorBoundary>
        <Exploder />
      </ErrorBoundary>,
    )

    expect(screen.getByRole('alert')).toHaveTextContent('Something went wrong')
    expect(reportSpy).toHaveBeenCalled()
    expect(reportSpy.mock.calls[0][0]).toBeInstanceOf(Error)
    expect(reportSpy.mock.calls[0][1]).toMatchObject({ scope: 'react_error_boundary' })
  })

  it('honours a custom fallback', () => {
    render(
      <ErrorBoundary fallback={<p role="alert">custom fallback</p>}>
        <Exploder />
      </ErrorBoundary>,
    )

    expect(screen.getByRole('alert')).toHaveTextContent('custom fallback')
  })
})
