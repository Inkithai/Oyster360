const API_BASE = (process.env.NEXT_PUBLIC_API_URL || '').replace(/\/$/, '')

export async function apiRequest(endpoint: string, options: RequestInit = {}) {
  const token = typeof window !== 'undefined' ? localStorage.getItem('token') : null

  const res = await fetch(`${API_BASE}${endpoint}`, {
    ...options,
    headers: {
      'Content-Type': 'application/json',
      ...(token && { Authorization: `Bearer ${token}` }),
      ...options.headers,
    },
  })

  if (!res.ok) {
    const error = await res.json().catch(() => ({}))
    throw new Error(error.detail || `API Error: ${res.status}`)
  }

  if (res.status === 204) {
    return null
  }

  return res.json()
}

// Auth
export const auth = {
  login: (email: string, password: string) =>
    apiRequest('/api/auth/login', {
      method: 'POST',
      body: JSON.stringify({ email, password }),
    }),
}

// Batches
export const batches = {
  getAll: () => apiRequest('/api/batches'),
  getById: (id: number) => apiRequest(`/api/batches/${id}`),
  updateStage: (id: number, stage: string) =>
    apiRequest(`/api/batches/${id}/stage`, {
      method: 'PATCH',
      body: JSON.stringify({ stage }),
    }),
}

// Recipes
export const recipes = {
  getAll: () => apiRequest('/api/recipes'),
  getPerformance: (id: number) => apiRequest(`/api/recipes/${id}/performance`),
}

// Analytics
export const analytics = {
  getDashboard: () => apiRequest('/api/analytics/dashboard'),
}

// Strains
export const strains = {
  getAll: () => apiRequest('/api/strains'),
}
