import { afterEach, beforeEach, describe, expect, it, vi } from 'vitest'

import { analytics, apiRequest, auth } from '../api'

function mockResponse(body: unknown, init: { ok?: boolean; status?: number } = {}): Response {
  const ok = init.ok ?? true
  const status = init.status ?? 200
  return {
    ok,
    status,
    json: async () => body,
  } as unknown as Response
}

type FetchImpl = (url: string, init: RequestInit) => Promise<Response>

describe('apiRequest', () => {
  const originalFetch = global.fetch

  beforeEach(() => {
    localStorage.clear()
  })

  afterEach(() => {
    global.fetch = originalFetch
    vi.restoreAllMocks()
  })

  it('sends a JSON request and returns parsed body', async () => {
    const fetchMock = vi.fn<FetchImpl>(async () => mockResponse({ ok: true }))
    global.fetch = fetchMock as unknown as typeof fetch

    const data = await apiRequest('/api/ping')
    expect(data).toEqual({ ok: true })
    expect(fetchMock).toHaveBeenCalledOnce()
    const [, init] = fetchMock.mock.calls[0]
    expect(init.headers).toMatchObject({ 'Content-Type': 'application/json' })
  })

  it('attaches the bearer token from localStorage when present', async () => {
    localStorage.setItem('token', 'abc123')
    const fetchMock = vi.fn<FetchImpl>(async () => mockResponse({ ok: true }))
    global.fetch = fetchMock as unknown as typeof fetch

    await apiRequest('/api/ping')
    const [, init] = fetchMock.mock.calls[0]
    expect(init.headers).toMatchObject({ Authorization: 'Bearer abc123' })
  })

  it('throws on a non-ok response, preferring server detail', async () => {
    global.fetch = vi.fn<FetchImpl>(async () =>
      mockResponse({ detail: 'Unauthorized' }, { ok: false, status: 401 })
    ) as unknown as typeof fetch
    await expect(apiRequest('/api/secret')).rejects.toThrow('Unauthorized')
  })

  it('returns null for 204 No Content', async () => {
    global.fetch = vi.fn<FetchImpl>(async () =>
      mockResponse(null, { ok: true, status: 204 })
    ) as unknown as typeof fetch
    await expect(apiRequest('/api/clear')).resolves.toBeNull()
  })
})

describe('api client namespaces', () => {
  afterEach(() => vi.restoreAllMocks())

  it('auth.login posts credentials', async () => {
    const fetchMock = vi.fn<FetchImpl>(async () => mockResponse({ access_token: 't' }))
    global.fetch = fetchMock as unknown as typeof fetch
    await auth.login('a@b.com', 'pw')
    const [url, init] = fetchMock.mock.calls[0]
    expect(url).toContain('/api/auth/login')
    expect(init.method).toBe('POST')
  })

  it('analytics.getDashboard hits the dashboard endpoint', async () => {
    const fetchMock = vi.fn<FetchImpl>(async () => mockResponse({ total: 0 }))
    global.fetch = fetchMock as unknown as typeof fetch
    await analytics.getDashboard()
    expect(fetchMock.mock.calls[0][0]).toContain('/api/analytics/dashboard')
  })
})
