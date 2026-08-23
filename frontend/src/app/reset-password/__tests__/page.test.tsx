import { QueryClient, QueryClientProvider } from '@tanstack/react-query'
import { fireEvent, render, screen, waitFor } from '@testing-library/react'
import { beforeEach, describe, expect, it, vi } from 'vitest'

import ResetPasswordPage from '../page'
import { apiRequest } from '@/lib/api'

const { mockToast, mockPush, mockToken } = vi.hoisted(() => ({
  mockToast: vi.fn(),
  mockPush: vi.fn(),
  mockToken: { value: 'reset-token-123' },
}))

vi.mock('@/lib/api', () => ({ apiRequest: vi.fn() }))
vi.mock('@/components/ui/use-toast', () => ({
  useToast: () => ({ toast: mockToast, toasts: [] }),
}))
vi.mock('next/navigation', () => ({
  useRouter: () => ({ push: mockPush }),
  useSearchParams: () =>
    new URLSearchParams(mockToken.value ? `token=${mockToken.value}` : ''),
}))

const mockedApiRequest = vi.mocked(apiRequest)

function renderPage() {
  const queryClient = new QueryClient({ defaultOptions: { queries: { retry: false } } })
  return render(
    <QueryClientProvider client={queryClient}>
      <ResetPasswordPage />
    </QueryClientProvider>,
  )
}

function fillPasswords(newPassword: string, confirmPassword: string) {
  const fields = screen.getAllByPlaceholderText('••••••••')
  fireEvent.change(fields[0], { target: { value: newPassword } })
  fireEvent.change(fields[1], { target: { value: confirmPassword } })
}

describe('ResetPasswordPage', () => {
  beforeEach(() => {
    mockedApiRequest.mockReset()
    mockToast.mockReset()
    mockPush.mockReset()
    mockToken.value = 'reset-token-123'
  })

  it('rejects an invalid link without a token', () => {
    mockToken.value = ''

    renderPage()

    expect(screen.getByRole('heading', { name: 'Invalid Reset Link' })).toBeInTheDocument()
    expect(
      screen.getByRole('link', { name: 'Request a new reset link' }),
    ).toHaveAttribute('href', '/forgot-password')
    expect(mockedApiRequest).not.toHaveBeenCalled()
  })

  it('shows the form for a valid token', () => {
    renderPage()

    expect(screen.getByRole('heading', { name: 'Reset Password' })).toBeInTheDocument()
    expect(screen.getByRole('button', { name: 'Reset Password' })).toBeEnabled()
  })

  it('blocks submission when passwords do not match', () => {
    renderPage()
    fillPasswords('new-secret-pass', 'different-pass')
    fireEvent.click(screen.getByRole('button', { name: 'Reset Password' }))

    expect(mockToast).toHaveBeenCalledWith(
      expect.objectContaining({ description: 'Passwords do not match' }),
    )
    expect(mockedApiRequest).not.toHaveBeenCalled()
  })

  it('submits the token and new password to the API', async () => {
    mockedApiRequest.mockResolvedValueOnce({ message: 'Password updated' })
    renderPage()
    fillPasswords('new-secret-pass', 'new-secret-pass')
    fireEvent.click(screen.getByRole('button', { name: 'Reset Password' }))

    await waitFor(() =>
      expect(mockedApiRequest).toHaveBeenCalledWith('/api/auth/reset-password', {
        method: 'POST',
        body: JSON.stringify({ token: 'reset-token-123', new_password: 'new-secret-pass' }),
      }),
    )
    expect(mockToast).toHaveBeenCalledWith(
      expect.objectContaining({ title: 'Password reset successful', variant: 'success' }),
    )
  })

  it('surfaces an error toast when the reset request fails', async () => {
    mockedApiRequest.mockRejectedValueOnce(new Error('expired token'))
    renderPage()
    fillPasswords('new-secret-pass', 'new-secret-pass')
    fireEvent.click(screen.getByRole('button', { name: 'Reset Password' }))

    await waitFor(() => expect(mockToast).toHaveBeenCalled())
    expect(mockToast).toHaveBeenCalledWith(
      expect.objectContaining({
        title: 'Error',
        description: 'Failed to reset password. Please try again.',
        variant: 'error',
      }),
    )
  })
})
