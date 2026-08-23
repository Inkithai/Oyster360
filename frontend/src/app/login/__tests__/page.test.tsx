import { QueryClient, QueryClientProvider } from '@tanstack/react-query'
import { fireEvent, render, screen, waitFor } from '@testing-library/react'
import { beforeEach, describe, expect, it, vi } from 'vitest'

import LoginPage from '../page'
import { apiRequest } from '@/lib/api'

const { mockToast, mockPush } = vi.hoisted(() => ({
  mockToast: vi.fn(),
  mockPush: vi.fn(),
}))

vi.mock('@/lib/api', () => ({ apiRequest: vi.fn() }))
vi.mock('@/components/ui/use-toast', () => ({
  useToast: () => ({ toast: mockToast, toasts: [] }),
}))
vi.mock('next/navigation', () => ({
  useRouter: () => ({ push: mockPush }),
}))

const mockedApiRequest = vi.mocked(apiRequest)

function renderPage() {
  const queryClient = new QueryClient({ defaultOptions: { queries: { retry: false } } })
  return render(
    <QueryClientProvider client={queryClient}>
      <LoginPage />
    </QueryClientProvider>,
  )
}

function fillCredentials(email: string, password: string) {
  fireEvent.change(screen.getByLabelText('Email'), { target: { value: email } })
  fireEvent.change(screen.getByLabelText('Password'), { target: { value: password } })
}

describe('LoginPage', () => {
  beforeEach(() => {
    mockedApiRequest.mockReset()
    mockToast.mockReset()
    mockPush.mockReset()
    localStorage.clear()
  })

  it('validates credentials before calling the API', async () => {
    renderPage()
    fireEvent.click(screen.getByRole('button', { name: 'Sign In' }))

    expect(await screen.findByText('Invalid email address')).toBeInTheDocument()
    expect(screen.getByText('Password must be at least 6 characters')).toBeInTheDocument()
    expect(mockedApiRequest).not.toHaveBeenCalled()
  })

  it('stores tokens and redirects after a successful login', async () => {
    mockedApiRequest.mockResolvedValueOnce({
      access_token: 'access-abc',
      refresh_token: 'refresh-xyz',
    })
    renderPage()
    fillCredentials('farmer@myco.farm', 'secret123')
    fireEvent.click(screen.getByRole('button', { name: 'Sign In' }))

    await waitFor(() => expect(mockPush).toHaveBeenCalledWith('/dashboard'))
    expect(localStorage.getItem('token')).toBe('access-abc')
    expect(localStorage.getItem('refresh_token')).toBe('refresh-xyz')
    expect(mockToast).toHaveBeenCalledWith(
      expect.objectContaining({ title: 'Login successful', variant: 'success' }),
    )
  })

  it('posts the submitted credentials to the login endpoint', async () => {
    mockedApiRequest.mockResolvedValueOnce({
      access_token: 'access-abc',
      refresh_token: 'refresh-xyz',
    })
    renderPage()
    fillCredentials('farmer@myco.farm', 'secret123')
    fireEvent.click(screen.getByRole('button', { name: 'Sign In' }))

    await waitFor(() => expect(mockedApiRequest).toHaveBeenCalled())
    expect(mockedApiRequest).toHaveBeenCalledWith('/api/auth/login', {
      method: 'POST',
      body: JSON.stringify({ email: 'farmer@myco.farm', password: 'secret123' }),
    })
  })

  it('shows an error toast without redirecting on bad credentials', async () => {
    mockedApiRequest.mockRejectedValueOnce(new Error('unauthorized'))
    renderPage()
    fillCredentials('farmer@myco.farm', 'wrongpass')
    fireEvent.click(screen.getByRole('button', { name: 'Sign In' }))

    await waitFor(() => expect(mockToast).toHaveBeenCalled())
    expect(mockToast).toHaveBeenCalledWith(
      expect.objectContaining({
        title: 'Login failed',
        description: 'Invalid credentials',
        variant: 'error',
      }),
    )
    expect(mockPush).not.toHaveBeenCalled()
    expect(localStorage.getItem('token')).toBeNull()
  })
})
