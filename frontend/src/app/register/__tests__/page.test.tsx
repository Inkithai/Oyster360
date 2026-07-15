import { QueryClient, QueryClientProvider } from '@tanstack/react-query'
import { fireEvent, render, screen, waitFor } from '@testing-library/react'
import { beforeEach, describe, expect, it, vi } from 'vitest'

import RegisterPage from '../page'
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
      <RegisterPage />
    </QueryClientProvider>,
  )
}

function fillForm(values: Partial<Record<'name' | 'email' | 'password' | 'farmName', string>>) {
  // Field order on the page: name, email, password, farm name.
  const textboxes = screen.getAllByRole('textbox')
  const [nameField, emailField, farmNameField] = textboxes
  const passwordField = document.querySelector('input[type="password"]')

  if (values.name !== undefined) fireEvent.change(nameField, { target: { value: values.name } })
  if (values.email !== undefined) fireEvent.change(emailField, { target: { value: values.email } })
  if (values.password !== undefined)
    fireEvent.change(passwordField!, { target: { value: values.password } })
  if (values.farmName !== undefined)
    fireEvent.change(farmNameField, { target: { value: values.farmName } })
}

describe('RegisterPage', () => {
  beforeEach(() => {
    mockedApiRequest.mockReset()
    mockToast.mockReset()
    mockPush.mockReset()
  })

  it('validates every field before calling the API', async () => {
    renderPage()
    fireEvent.click(screen.getByRole('button', { name: 'Create Account' }))

    expect(await screen.findByText('Name is required')).toBeInTheDocument()
    expect(screen.getByText('Invalid email address')).toBeInTheDocument()
    expect(screen.getByText('Password must be at least 8 characters')).toBeInTheDocument()
    expect(screen.getByText('Farm name is required')).toBeInTheDocument()
    expect(mockedApiRequest).not.toHaveBeenCalled()
  })

  it('registers the account with a snake_case farm name payload', async () => {
    mockedApiRequest.mockResolvedValueOnce({ id: 1 })
    renderPage()
    fillForm({
      name: 'Nuwan Perera',
      email: 'nuwan@myco.farm',
      password: 'secure-pass-123',
      farmName: 'Bim Mal Farm',
    })
    fireEvent.click(screen.getByRole('button', { name: 'Create Account' }))

    await waitFor(() => expect(mockPush).toHaveBeenCalledWith('/login'))
    expect(mockedApiRequest).toHaveBeenCalledWith('/api/auth/register', {
      method: 'POST',
      body: JSON.stringify({
        name: 'Nuwan Perera',
        email: 'nuwan@myco.farm',
        password: 'secure-pass-123',
        farm_name: 'Bim Mal Farm',
      }),
    })
    expect(mockToast).toHaveBeenCalledWith(
      expect.objectContaining({ title: 'Account created successfully', variant: 'success' }),
    )
  })

  it('shows an error toast and stays on the page when registration fails', async () => {
    mockedApiRequest.mockRejectedValueOnce(new Error('email already registered'))
    renderPage()
    fillForm({
      name: 'Nuwan Perera',
      email: 'nuwan@myco.farm',
      password: 'secure-pass-123',
      farmName: 'Bim Mal Farm',
    })
    fireEvent.click(screen.getByRole('button', { name: 'Create Account' }))

    await waitFor(() => expect(mockToast).toHaveBeenCalled())
    expect(mockToast).toHaveBeenCalledWith(
      expect.objectContaining({ title: 'Registration failed', variant: 'error' }),
    )
    expect(mockPush).not.toHaveBeenCalled()
  })
})
