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

// Batches & Grow Bags
export const batches = {
  getAll: () => apiRequest('/api/batches'),
  getById: (id: number) => apiRequest(`/api/batches/${id}`),
  getDailyTasks: () => apiRequest('/api/batches/daily-tasks'),
  updateStage: (id: number, stage: string) =>
    apiRequest(`/api/batches/${id}/stage`, {
      method: 'PATCH',
      body: JSON.stringify({ stage }),
    }),
  updateBags: (id: number, payload: Record<string, unknown>) =>
    apiRequest(`/api/batches/${id}/bags`, {
      method: 'PATCH',
      body: JSON.stringify(payload),
    }),
}

// Finance & LKR Profit Calculator
export const finance = {
  getExpenses: (batchId?: number) =>
    apiRequest(batchId ? `/api/finance/expenses?batch_id=${batchId}` : '/api/finance/expenses'),
  createExpense: (payload: Record<string, unknown>) =>
    apiRequest('/api/finance/expenses', {
      method: 'POST',
      body: JSON.stringify(payload),
    }),
  getProfitability: () => apiRequest('/api/finance/profitability'),
}

// Buyers & Harvest Sales
export const sales = {
  getBuyers: () => apiRequest('/api/sales/buyers'),
  createBuyer: (payload: Record<string, unknown>) =>
    apiRequest('/api/sales/buyers', {
      method: 'POST',
      body: JSON.stringify(payload),
    }),
  getOrders: () => apiRequest('/api/sales/orders'),
  createOrder: (payload: Record<string, unknown>) =>
    apiRequest('/api/sales/orders', {
      method: 'POST',
      body: JSON.stringify(payload),
    }),
  recordPayment: (saleId: number, paymentAmountLkr: number) =>
    apiRequest(`/api/sales/orders/${saleId}/payment`, {
      method: 'PATCH',
      body: JSON.stringify({ payment_amount_lkr: paymentAmountLkr }),
    }),
  getStockSummary: () => apiRequest('/api/sales/stock-summary'),
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

// Strains & Sri Lanka DOA Guide
export const strains = {
  getAll: () => apiRequest('/api/strains'),
  getDoaVarieties: () => apiRequest('/api/strains/doa-varieties'),
  getCultivationGuide: () => apiRequest('/api/strains/cultivation-guide'),
}
