import { QueryClient, QueryClientProvider } from '@tanstack/react-query'
import { fireEvent, render, screen, waitFor } from '@testing-library/react'
import { beforeEach, describe, expect, it, vi } from 'vitest'

import ForgotPasswordPage from '../page'
import { apiRequest } from '@/lib/api'

const { mockToast } = vi.hoisted(() => ({ mockToast: vi.fn() }))

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

function submitEmail(email: string) {
  fireEvent.change(screen.getByLabelText('Email Address'), { target: { value: email } })
  fireEvent.click(screen.getByRole('button', { name: 'Send Reset Link' }))
}

describe('ForgotPasswordPage', () => {
  beforeEach(() => {
    mockedApiRequest.mockReset()
    mockToast.mockReset()
  })

  it('posts the entered email to the forgot-password endpoint', async () => {
    mockedApiRequest.mockResolvedValueOnce({ message: 'reset link sent' })
    renderPage()
    submitEmail('farmer@myco.farm')

    await waitFor(() =>
      expect(mockedApiRequest).toHaveBeenCalledWith('/api/auth/forgot-password', {
        method: 'POST',
        body: JSON.stringify({ email: 'farmer@myco.farm' }),
      }),
    )
  })

  it('confirms submission and clears the field on success', async () => {
    mockedApiRequest.mockResolvedValueOnce({ message: 'If the account exists, a link was sent' })
    renderPage()
    submitEmail('farmer@myco.farm')

    await waitFor(() =>
      expect(mockToast).toHaveBeenCalledWith(
        expect.objectContaining({
          title: 'Request submitted',
          description: 'If the account exists, a link was sent',
          variant: 'success',
        }),
      ),
    )
    expect(screen.getByLabelText('Email Address')).toHaveValue('')
  })

  it('surfaces an error toast and keeps the email on failure', async () => {
    mockedApiRequest.mockRejectedValueOnce(new Error('server error'))
    renderPage()
    submitEmail('farmer@myco.farm')

    await waitFor(() =>
      expect(mockToast).toHaveBeenCalledWith(
        expect.objectContaining({
          title: 'Error',
          description: 'Something went wrong. Please try again.',
          variant: 'error',
        }),
      ),
    )
    expect(screen.getByLabelText('Email Address')).toHaveValue('farmer@myco.farm')
  })

  it('links back to the sign-in page', () => {
    renderPage()
    expect(screen.getByRole('link', { name: 'Back to Sign In' })).toHaveAttribute(
      'href',
      '/login',
    )
  })
})
