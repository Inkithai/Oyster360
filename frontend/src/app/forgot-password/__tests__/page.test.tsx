import { QueryClient, QueryClientProvider } from '@tanstack/react-query'
import { fireEvent, render, screen, waitFor } from '@testing-library/react'
import { beforeEach, describe, expect, it, vi } from 'vitest'

import ForgotPasswordPage from '../page'
import { apiRequest } from '@/lib/api'

const { mockToast } = vi.hoisted(() => ({
  mockToast: vi.fn(),
}))

vi.mock('@/lib/api', () => ({ apiRequest: vi.fn() }))
vi.mock('@/components/ui/use-toast', () => ({
  useToast: () => ({ toast: mockToast, toasts: [] }),
}))

const mockedApiRequest = vi.mocked(apiRequest)

function renderPage() {
  const queryClient = new QueryClient({ defaultOptions: { queries: { retry: false } } })
  return render(
    <QueryClientProvider client={queryClient}>
      <ForgotPasswordPage />
    </QueryClientProvider>,
  )
}

describe('ForgotPasswordPage', () => {
  beforeEach(() => {
    mockedApiRequest.mockReset()
    mockToast.mockReset()
  })

  it('renders email input and submit button', () => {
    renderPage()
    expect(screen.getByText('Forgot Password?')).toBeInTheDocument()
    expect(screen.getByPlaceholderText('your@email.com')).toBeInTheDocument()
    expect(screen.getByRole('button', { name: /send reset link/i })).toBeInTheDocument()
  })

  it('submits email and triggers api call', async () => {
    mockedApiRequest.mockResolvedValueOnce({ message: 'Reset email sent successfully' })
    renderPage()

    const input = screen.getByPlaceholderText('your@email.com')
    fireEvent.change(input, { target: { value: 'user@farm.com' } })

    const submitBtn = screen.getByRole('button', { name: /send reset link/i })
    fireEvent.click(submitBtn)

    await waitFor(() => {
      expect(mockedApiRequest).toHaveBeenCalledWith('/api/auth/forgot-password', {
        method: 'POST',
        body: JSON.stringify({ email: 'user@farm.com' }),
      })
    })
  })
})
